from fastapi.routing import APIRouter
from .auth import router as auth_router
from .notes import router as notes_router

router = APIRouter()


router.include_router(router=notes_router, prefix="/notes")
router.include_router(router=auth_router, prefix="/auth")
