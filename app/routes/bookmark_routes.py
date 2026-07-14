from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import User, Notice, Bookmark
from app.auth.jwt_handler import verify_access_token

router = APIRouter(
    prefix="/bookmarks",
    tags=["Bookmarks"]
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = verify_access_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(User.email == payload["sub"])
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.get("/")
def get_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    bookmarks = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == current_user.id)
        .all()
    )

    return [
        {
            "id": b.notice.id,
            "title": b.notice.title,
            "category": b.notice.category,
            "summary": b.notice.summary,
            "url": b.notice.notice_url
        }
        for b in bookmarks
    ]


@router.post("/{notice_id}")
def add_bookmark(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    notice = db.query(Notice).filter(
        Notice.id == notice_id
    ).first()

    if not notice:
        raise HTTPException(
            status_code=404,
            detail="Notice not found."
        )

    existing = (
        db.query(Bookmark)
        .filter(
            Bookmark.user_id == current_user.id,
            Bookmark.notice_id == notice_id
        )
        .first()
    )

    if existing:
        return {
            "message": "Already bookmarked."
        }

    bookmark = Bookmark(
        user_id=current_user.id,
        notice_id=notice_id
    )

    db.add(bookmark)
    db.commit()

    return {
        "message": "Bookmarked successfully."
    }


@router.delete("/{notice_id}")
def remove_bookmark(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    bookmark = (
        db.query(Bookmark)
        .filter(
            Bookmark.user_id == current_user.id,
            Bookmark.notice_id == notice_id
        )
        .first()
    )

    if not bookmark:
        raise HTTPException(
            status_code=404,
            detail="Bookmark not found."
        )

    db.delete(bookmark)
    db.commit()

    return {
        "message": "Bookmark removed."
    }