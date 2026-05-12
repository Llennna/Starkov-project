from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import create_access_token, get_current_admin, verify_password
from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .models import AdminUser, ContactMessage, Profile, Project, TimelineEvent
from .schemas import (
    ContactMessageCreate,
    ContactMessageOut,
    LoginRequest,
    PortfolioPayload,
    ProfileOut,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
    StatusResponse,
    TimelineEventOut,
    TokenResponse,
)
from .seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    yield


app = FastAPI(title=settings.project_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def calculate_age(birth_date: date) -> int:
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def serialize_profile(profile: Profile) -> ProfileOut:
    interests = [item.strip() for item in profile.interests.split(",") if item.strip()]
    return ProfileOut(
        full_name=profile.full_name,
        tagline=profile.tagline,
        city=profile.city,
        birth_date=profile.birth_date,
        age=calculate_age(profile.birth_date),
        avatar_path=profile.avatar_path,
        intro=profile.intro,
        current_study=profile.current_study,
        previous_study=profile.previous_study,
        interests=interests,
        quote=profile.quote,
    )


def get_profile_or_404(db: Session) -> Profile:
    profile = db.scalar(select(Profile).limit(1))
    if profile is None:
        raise HTTPException(status_code=404, detail="Профиль не найден.")
    return profile


def get_project_or_404(project_id: int, db: Session) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден.")
    return project


def get_admin_or_401(username: str, password: str, db: Session) -> AdminUser:
    admin = db.scalar(select(AdminUser).where(AdminUser.username == username))
    if admin is None or not verify_password(password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль.",
        )
    return admin


@app.get("/api/health", response_model=StatusResponse)
def healthcheck() -> StatusResponse:
    return StatusResponse(message="API готово к работе.")


@app.get("/api/public/portfolio", response_model=PortfolioPayload)
def read_portfolio(db: Session = Depends(get_db)) -> PortfolioPayload:
    profile = get_profile_or_404(db)
    timeline = db.scalars(
        select(TimelineEvent).order_by(TimelineEvent.sort_order.asc(), TimelineEvent.id.asc())
    ).all()
    projects = db.scalars(
        select(Project).order_by(Project.sort_order.asc(), Project.id.asc())
    ).all()

    return PortfolioPayload(
        profile=serialize_profile(profile),
        timeline=[TimelineEventOut.model_validate(item) for item in timeline],
        projects=[ProjectOut.model_validate(item) for item in projects],
    )


@app.post("/api/public/messages", response_model=StatusResponse, status_code=status.HTTP_201_CREATED)
def create_message(payload: ContactMessageCreate, db: Session = Depends(get_db)) -> StatusResponse:
    message = ContactMessage(
        name=payload.name,
        email=payload.email,
        message=payload.message,
    )
    db.add(message)
    db.commit()
    return StatusResponse(message="Сообщение отправлено. Спасибо за обратную связь.")


@app.post("/api/admin/login", response_model=TokenResponse)
def admin_login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    admin = get_admin_or_401(payload.username, payload.password, db)
    token = create_access_token(admin.username)
    return TokenResponse(access_token=token, username=admin.username)


@app.get("/api/admin/projects", response_model=list[ProjectOut])
def admin_projects(
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[ProjectOut]:
    projects = db.scalars(select(Project).order_by(Project.sort_order.asc(), Project.id.asc())).all()
    return [ProjectOut.model_validate(item) for item in projects]


@app.post("/api/admin/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProjectOut:
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectOut.model_validate(project)


@app.put("/api/admin/projects/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProjectOut:
    project = get_project_or_404(project_id, db)
    for field, value in payload.model_dump().items():
        setattr(project, field, value)
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectOut.model_validate(project)


@app.delete("/api/admin/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Response:
    project = get_project_or_404(project_id, db)
    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/admin/messages", response_model=list[ContactMessageOut])
def read_messages(
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[ContactMessageOut]:
    messages = db.scalars(
        select(ContactMessage).order_by(ContactMessage.created_at.desc(), ContactMessage.id.desc())
    ).all()
    return [ContactMessageOut.model_validate(item) for item in messages]


@app.patch("/api/admin/messages/{message_id}/read", response_model=StatusResponse)
def mark_message_as_read(
    message_id: int,
    _: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> StatusResponse:
    message = db.get(ContactMessage, message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Сообщение не найдено.")
    message.is_read = True
    db.add(message)
    db.commit()
    return StatusResponse(message="Сообщение отмечено как прочитанное.")


if settings.frontend_dist_dir.exists():
    app.mount("/", StaticFiles(directory=settings.frontend_dist_dir, html=True), name="frontend")
else:
    @app.get("/", response_model=StatusResponse)
    def root() -> StatusResponse:
        return StatusResponse(
            message="API запущено. Соберите frontend, чтобы FastAPI раздавал готовый сайт."
        )
