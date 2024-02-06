from typing import Any

from fastapi import HTTPException, status


class AbstractHttpException(HTTPException):
    _status_code = None
    _detail = None
    _description = None

    def __init__(self, detail: str | None = None) -> None:
        if detail is None:
            detail = self._detail
        super().__init__(
            status_code=self._status_code,
            detail=detail,
        )

    @classmethod
    def docs(cls, detail: str | None = None) -> dict[int | str, dict[str, Any]] | None:
        if detail is None:
            detail = cls._detail
        return {
            cls._status_code: {
                "description": cls._description,
                "content": {
                    "application/json": {
                        "example": {"detail": detail}
                    }
                },
            }
        }


class UnauthorizedHTTPException(AbstractHttpException):
    _status_code = status.HTTP_401_UNAUTHORIZED
    _detail = "Could not validate credentials"


class ForbiddenHTTPException(AbstractHttpException):
    _status_code = status.HTTP_403_FORBIDDEN
    _detail = "You don't have enough rights"


class NotFoundHTTPException(AbstractHttpException):
    _status_code = status.HTTP_404_NOT_FOUND
    _detail = "Object(s) not found"


class NotAcceptableHTTPException(AbstractHttpException):
    _status_code = status.HTTP_406_NOT_ACCEPTABLE
    _detail = "Your queries do not meet the required conditions. You will get more details when a real error occurs."


class ImUsedHTTPException(AbstractHttpException):
    _status_code = status.HTTP_226_IM_USED
    _detail = "Im used ;D"
    _description = "Email уже активирован. Можно продолжить регистрацию."

class ImUsedHTTPException(AbstractHttpException):
    _status_code = status.HTTP_226_IM_USED
    _detail = "Im used ;D"
    _description = "Email уже активирован. Можно продолжить регистрацию."
