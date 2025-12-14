from fastapi import APIRouter

from app.api.predict import router as predict_router
from app.api.customers import router as customers_router  # если используешь

router = APIRouter()
router.include_router(predict_router, prefix="/api")
router.include_router(customers_router, prefix="/api")
