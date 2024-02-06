import datetime
from abc import ABC, abstractmethod
from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from config.jwt import jwt_settings
from config.api_key import api_key_settings
from src.repositories import UsersRepository, UserAPIKeysRepository
from src.schemas.users import UserDTO, UserAPIKeyDTO
from src.utils.utils import generate_random_string
from src.utils import exceptions
from src.utils.session_context_manager import SessionContextManager


class PasswordService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password):
        return cls.pwd_context.hash(password)


class AbstractAuthService(ABC):
    @classmethod
    @abstractmethod
    async def get_current_user(cls,
                               sign: Any,
                               ) -> UserDTO:
        raise NotImplementedError()

    @classmethod
    async def authenticate(cls,
                           session: SessionContextManager,
                           username: str,
                           password: str,
                           ) -> UserDTO:
        session = SessionContextManager()
        async with session:
            users_repo = UsersRepository(session.session)
            user = await users_repo.get_one_by_username(username=username, with_password=True)
            await session.commit()
        if user is None:
            raise exceptions.UnauthorizedHTTPException(detail="Incorrect email or password")
        if not PasswordService.verify_password(password, user.password):
            raise exceptions.UnauthorizedHTTPException(detail="Incorrect email or password")
        return UserDTO.model_validate(user, from_attributes=True)


class APIKeyService(AbstractAuthService):

    @classmethod
    async def create(cls,
                     session: SessionContextManager,
                     current_user: UserDTO,
                     expire_date: datetime.datetime,
                     ) -> str:
        if expire_date < datetime.date.today():
            raise exceptions.NotAcceptableHTTPException("Expire date must be in the future")
        async with session:
            user_api_keys_repo = UserAPIKeysRepository(session.session)
            key = cls._generate_api_key(api_key_settings.LENGTH)
            user_api_key_id = await user_api_keys_repo.add_one(
                {
                    "user_id": current_user.id,
                    "key": key,
                    "expire_date": expire_date
                }
            )
            await session.commit()
        return key

    @classmethod
    async def get_all(cls,
                      current_user: UserDTO,
                      ) -> list[UserAPIKeyDTO]:
        session = SessionContextManager()
        async with session:
            user_api_keys_repo = UserAPIKeysRepository(session.session)
            user_api_keys = await user_api_keys_repo.get_all_with_filters(user_id=current_user.id)
            await session.commit()
        return user_api_keys

    @classmethod
    async def delete(cls,
                     session: SessionContextManager,
                     current_user: UserDTO,
                     id: int
                     ) -> None:
        async with session as s:
            user_api_keys_repo = UserAPIKeysRepository(s)
            api_key = await user_api_keys_repo.get_one(id=id)
            if api_key is None:
                raise exceptions.NotFoundHTTPException()
            if api_key.user_id != current_user.id:
                raise exceptions.ForbiddenHTTPException()
            await user_api_keys_repo.delete(id=id)
            s.commit()

    @classmethod
    async def get_current_user(cls,
                               api_key: str,
                               ) -> UserDTO:
        session = SessionContextManager()
        async with session:
            user_api_keys_repo = UserAPIKeysRepository(session.session)
            user_api_key = await user_api_keys_repo.get_one(key=api_key)
            if user_api_key is None:
                raise exceptions.UnauthorizedHTTPException()
            if user_api_key.expire_date < datetime.date.today():
                raise exceptions.UnauthorizedHTTPException()
            users_repo = UsersRepository(session.session)
            user = await users_repo.get_one(id=user_api_key.user_id)
            if user.banned:
                raise exceptions.UnauthorizedHTTPException()
            await session.commit()
        return user

    @classmethod
    def _generate_api_key(cls, length: int) -> str:
        return generate_random_string(length=length, only_digits=True, only_letters=True)


class JWTService(AbstractAuthService):
    oauth2_password_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/jwt/tokens")
    token_type = 'Bearer'

    @classmethod
    async def get_current_user(cls,
                               token: Annotated[str, Depends(oauth2_password_scheme)],
                               ) -> UserDTO:
        session = SessionContextManager()
        user = await cls.authenticate_by_token(session, token)
        if user.banned:
            raise exceptions.UnauthorizedHTTPException()
        return user

    @classmethod
    async def authenticate_by_token(cls, session: SessionContextManager, token: str):
        try:
            payload = jwt.decode(token, jwt_settings.SECRET_KEY, algorithms=jwt_settings.ALGORITHM)
        except JWTError:
            raise exceptions.UnauthorizedHTTPException()
        username = payload.get("username")
        if username is None:
            raise exceptions.UnauthorizedHTTPException()
        async with session:
            users_repo = UsersRepository(session.session)
            user = await users_repo.get_one_by_username(username=username)
            if user.banned:
                raise exceptions.UnauthorizedHTTPException()
            await session.commit()
        if user is None:
            raise exceptions.UnauthorizedHTTPException()
        if user.banned:
            raise exceptions.UnauthorizedHTTPException()
        return user

    @classmethod
    async def authenticate_by_refresh_token(cls, session: SessionContextManager, token: str,
                                            grant_type: str) -> UserDTO:
        if grant_type != 'refresh_token':
            raise exceptions.UnauthorizedHTTPException(
                detail="Expected 'grant_type' parameter with 'refresh_token' value")
        return await cls.authenticate_by_token(session, token)

    @classmethod
    def create_tokens(cls,
                      data: dict,
                      ) -> tuple[token_type, str, str]:
        now = datetime.datetime.utcnow()

        access_token_exp = now + datetime.timedelta(minutes=jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = data.copy()
        to_encode["exp"] = access_token_exp
        access_token = jwt.encode(to_encode, jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM)

        refresh_token_exp = now + datetime.timedelta(hours=jwt_settings.REFRESH_TOKEN_EXPIRE_HOURS)
        to_encode = data.copy()
        to_encode["exp"] = refresh_token_exp
        refresh_token = jwt.encode(to_encode, jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM)

        return cls.token_type, access_token, refresh_token
