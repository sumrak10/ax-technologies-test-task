import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from config.api_key import api_key_settings
from src.schemas.users import UserDTO, UserAPIKeyDTO
from src.services.users import APIKeyService, JWTService
from src.utils.oauth2 import OAuth2RefreshRequestForm
from src.utils.session_context_manager import SessionContextManager, AbstractSessionContextManager
from src.utils import exceptions, responses

router = APIRouter(
    prefix='/apikey',
    tags=['ApiKey']
)


@router.post(
    path='/',
    responses={
        status.HTTP_200_OK: {
            "description": "Возвращает API Key",
            "content": {
                "application/json": {
                    "example": {"message": "Successfully created", "key": 'x' * api_key_settings.LENGTH}
                }
            },
        },
        **exceptions.NotAcceptableHTTPException.docs(),
        **exceptions.ForbiddenHTTPException.docs(),
    })
async def create_api_token(
        session_: Annotated[SessionContextManager, Depends(SessionContextManager)],
        expire_date: datetime.date,
        current_user=Depends(JWTService.get_current_user)
):
    key = await APIKeyService.create(session_, current_user, expire_date)
    return JSONResponse(content={"message": "Successfully created", "key": key})


@router.get(
    path='/',
    response_model=list[UserAPIKeyDTO],
    responses={
        **exceptions.ForbiddenHTTPException.docs(),
    })
async def get_all_api_tokens(
        session_: Annotated[SessionContextManager, Depends(SessionContextManager)],
        current_user=Depends(JWTService.get_current_user)
):
    return await APIKeyService.get_all(session_, current_user)


@router.delete(
    path='/',
    responses={
        **responses.ObjectDeleted.docs,
        **exceptions.NotFoundHTTPException.docs(),
        **exceptions.ForbiddenHTTPException.docs(),
    })
async def delete_api_token(
        session: Annotated[SessionContextManager, Depends(SessionContextManager)],
        id: int,
        current_user: UserDTO = Depends(JWTService.get_current_user)
):
    await APIKeyService.delete(session, current_user, id)
    return responses.ObjectDeleted.response()
