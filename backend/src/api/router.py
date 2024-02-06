from fastapi import APIRouter

from .jwt.router import router as jwt_router
from .api_key.router import router as api_key_router
from .users.router import router as users_router
from .books.router import router as books_router


router = APIRouter(
    prefix='/api/v1'
)


router.include_router(jwt_router)
router.include_router(api_key_router)
router.include_router(users_router)
router.include_router(books_router)
