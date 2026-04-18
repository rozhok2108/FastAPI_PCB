from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, AsyncSessionLocal
from app.routers import auth, services, orders, users
from app.utils.init_admin import create_default_admin
from app.config import settings
from app.auth import get_current_user
from app.models import User, UserRole
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PCB Order System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables created")

    async with AsyncSessionLocal() as db:
        await create_default_admin(
            db=db,
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD
        )

    logger.info(f"🚀 Application started on http://0.0.0.0:8000")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard")
async def dashboard_page(request: Request):
    """Перенаправляет на дашборд в зависимости от роли (проверка на клиенте)"""
    return templates.TemplateResponse("dashboard_redirect.html", {"request": request})

@app.get("/dashboard/admin")
async def dashboard_admin(request: Request, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return templates.TemplateResponse("dashboard_admin.html", {"request": request})

@app.get("/dashboard/manager")
async def dashboard_manager(request: Request, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return templates.TemplateResponse("dashboard_manager.html", {"request": request})

@app.get("/dashboard/engineer")
async def dashboard_engineer(request: Request, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.ENGINEER]:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return templates.TemplateResponse("dashboard_engineer.html", {"request": request})

@app.get("/dashboard/client")
async def dashboard_client(request: Request, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.CLIENT]:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return templates.TemplateResponse("dashboard_client.html", {"request": request})

app.include_router(auth.router, prefix="/api")
app.include_router(services.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(users.router, prefix="/api")