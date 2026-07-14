from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

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


# ================= AI ACTION =================

class AIAction(BaseModel):
    action: str


# ================= CREATE =================

@router.post("/", response_model=NoticeResponse)
def add_notice(notice: NoticeCreate):

    try:
        return create_notice(notice)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ================= GET ALL =================

@router.get("/")
def all_notices(

    page: int = Query(1, ge=1),

    limit: int = Query(10, ge=1, le=100),

    category: str | None = None,

    search: str | None = None

):

    notices = get_all_notices()

    if category:

        notices = [

            n

            for n in notices

            if n.category.lower() == category.lower()

        ]

    if search:

        s = search.lower()

        notices = [

            n

            for n in notices

            if (

                s in n.title.lower()

                or

                s in n.summary.lower()

            )

        ]

    total = len(notices)

    start = (page - 1) * limit

    end = start + limit

    return {

        "items": notices[start:end],

        "page": page,

        "limit": limit,

        "total": total,

        "pages": (

            total + limit - 1

        ) // limit

    }


# ================= GET ONE =================

@router.get("/{notice_id}", response_model=NoticeResponse)
def one_notice(notice_id: int):

    notice = get_notice_by_id(notice_id)

    if notice is None:

        raise HTTPException(

            status_code=404,

            detail="Notice not found"

        )

    return notice


# ================= DELETE =================

@router.delete("/{notice_id}")
def remove_notice(notice_id: int):

    success = delete_notice(notice_id)

    if not success:

        raise HTTPException(

            status_code=404,

            detail="Notice not found"

        )

    return {

        "success": True,

        "message": "Notice deleted successfully"

    }


# ================= AI ACTION =================

@router.post("/{notice_id}/ai-action")
def ai_action(

    notice_id: int,

    request: AIAction

):

    notice = get_notice_by_id(notice_id)

    if not notice:

        raise HTTPException(

            status_code=404,

            detail="Notice not found"

        )

    action = request.action.lower()

    if action == "translate":

        return {

            "result": notice.translated_summary

        }

    elif action == "summarize":

        return {

            "result": notice.summary

        }

    elif action == "eligibility":

        return {

            "result": notice.eligibility

        }

    elif action == "important_dates":

        return {

            "result": notice.important_dates

        }

    elif action == "action_required":

        return {

            "result": notice.action_required

        }

    return {

        "result": notice.summary

    }