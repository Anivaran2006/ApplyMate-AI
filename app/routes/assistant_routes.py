from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import Notice

from app.schemas.assistant import ChatRequest
from app.ai.assistant_service import ask_ai

router = APIRouter(
    prefix="/assistant",
    tags=["AI Assistant"]
)


@router.post("/chat")
def chat(request: ChatRequest):

    db: Session = SessionLocal()

    notices = (
        db.query(Notice)
        .order_by(Notice.created_at.desc())
        .limit(50)
        .all()
    )

    answer = ask_ai(
        request.question,
        notices
    )

    db.close()

    return {
        "answer": answer
    }