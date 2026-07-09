from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

from app.services.monitor import monitor
from app.services.scheduler import start_scheduler

from app.routes.user_routes import router as user_router
from app.routes.category_routes import router as category_router


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()


@app.on_event("startup")
def startup_event():

    # start_scheduler()
    pass


app.include_router(user_router)
app.include_router(category_router)


@app.get("/")
def home():

    return {
        "message": "ApplyMate AI Running Successfully"
    }


@app.get("/check")
def check_updates():

    return monitor()

 
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


# @app.get(
#     "/dashboard",
#     response_class=HTMLResponse
# )
# def dashboard(request: Request):

#     return templates.TemplateResponse(
#         "index.html",
#         {
#             "request": request
#         }
#     )
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )
@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin.html"
    )