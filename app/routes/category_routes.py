from fastapi import APIRouter

from app.services.category_service import get_categories

router = APIRouter()


@router.get("/categories")
def categories():

    return get_categories()