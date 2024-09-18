from .registration import router as registration_router
from aiogram import Router

router = Router()
router.include_router(registration_router)
