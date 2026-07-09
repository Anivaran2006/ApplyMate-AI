from fastapi import APIRouter, HTTPException

from app.schemas.notice import (
    NoticeCreate,
    NoticeResponse
)

from app.services.notice_service import (
    create_notice,
    get_all_notices,
    get_notice_by_id,
    delete_notice
)

router = APIRouter(
    prefix="/notices",
    tags=["Notices"]
)


@router.post("/", response_model=NoticeResponse)
def add_notice(notice: NoticeCreate):

    return create_notice(notice)


from fastapi import Query


@router.get("/", response_model=list[NoticeResponse])
def all_notices(

    category: str | None = Query(default=None)

):

    notices = get_all_notices()

    if category:

        notices = [

            n for n in notices

            if n.category == category

        ]

    return notices


@router.get("/{notice_id}", response_model=NoticeResponse)
def one_notice(notice_id: int):

    notice = get_notice_by_id(notice_id)

    if not notice:
        raise HTTPException(
            status_code=404,
            detail="Notice not found"
        )

    return notice


@router.delete("/{notice_id}")
def remove_notice(notice_id: int):

    success = delete_notice(notice_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Notice not found"
        )

    return {
        "message": "Notice deleted successfully"
    }