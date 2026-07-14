from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database.database import Base, engine, SessionLocal
from app.database.models import User

from app.services.scheduler import start_scheduler

# ---------------- ROUTES ----------------

from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.notice_routes import router as notice_router
from app.routes.admin_routes import router as admin_router
from app.routes.category_routes import router as category_router
from app.routes.telegram_routes import router as telegram_router
from app.routes.subscription_routes import router as subscription_router
from app.routes.bookmark_routes import router as bookmark_router
from app.routes.notification_routes import router as notification_router
from app.routes.profile_routes import router as profile_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.analytics_routes import router as analytics_router
from app.routes.assistant_routes import router as assistant_router

app = FastAPI(
    title="ApplyMate AI",
    version="2.0.0"
)

# ---------------- DATABASE ----------------

Base.metadata.create_all(bind=engine)

# ---------------- STARTUP ----------------

@app.on_event("startup")
def startup():

    start_scheduler()

# ---------------- ROUTERS ----------------

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(notice_router)
app.include_router(admin_router)
app.include_router(category_router)
app.include_router(telegram_router)
app.include_router(subscription_router)
app.include_router(bookmark_router)
app.include_router(notification_router)
app.include_router(profile_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(assistant_router)

# ---------------- STATIC ----------------

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)

# ---------------- HOME ----------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )

# ---------------- LOGIN ----------------

@app.get("/login", response_class=HTMLResponse)
def login(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )

# ---------------- SIGNUP ----------------

@app.get("/signup", response_class=HTMLResponse)
def signup(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="signup.html",
        context={}
    )

# ---------------- DASHBOARD ----------------

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={}
    )

# ---------------- ADMIN ----------------

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={}
    )

# ---------------- FORGOT PASSWORD ----------------

@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="forgot-password.html",
        context={}
    )

# ---------------- USERS ----------------

@app.get("/users")
def get_users():

    db = SessionLocal()

    try:

        users = db.query(User).all()

        return [
            {
                "id": user.id,
                "email": user.email,
                "category": user.category,
                "role": user.role,
                "telegram_chat_id": user.telegram_chat_id,
                "telegram_notifications": user.telegram_notifications,
                "email_notifications": user.email_notifications
            }
            for user in users
        ]

    finally:
        db.close()