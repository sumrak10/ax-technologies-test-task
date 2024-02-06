from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.services.users import JWTService
from src.utils.oauth2 import OAuth2RefreshRequestForm
from src.utils.session_context_manager import SessionContextManager

router = APIRouter(
    prefix='/jwt',
    tags=['jwt']
)


@router.post(
    path="/tokens",
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/json": {
                    "example": {
                        "token_type": "Bearer",
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbW...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbW...",
                    }
                }
            },
        },
    })
async def login_for_tokens(
        session: Annotated[SessionContextManager, Depends(SessionContextManager)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await JWTService.authenticate(
        session,
        username=form_data.username,
        password=form_data.password
    )
    token_type, access_token, refresh_token = JWTService.create_tokens(
        {"username": user.username}
    )
    return {
        "token_type": token_type,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post(
    path='/refresh_token',
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/json": {
                    "example": {
                        "token_type": "Bearer",
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbW...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbW...",
                    }
                }
            },
        },
    })
async def get_refresh_token(
        session: Annotated[SessionContextManager, Depends(SessionContextManager)],
        form_data: Annotated[OAuth2RefreshRequestForm, Depends()]):
    user = await JWTService.authenticate_by_token(session, form_data.refresh_token)
    token_type, access_token, refresh_token = JWTService.create_tokens(
        {"username": user.username}
    )
    return {
        "token_type": token_type,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
