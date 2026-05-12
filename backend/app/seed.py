from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import hash_password
from .config import settings
from .models import AdminUser, Profile, Project, TimelineEvent

PROFILE_SEED = {
    "full_name": "Старков Иван Михайлович",
    "tagline": "Студент СВФУ, который превращает интерес к играм и компьютерному железу в веб-проекты.",
    "city": "Якутск",
    "birth_date": date(2004, 9, 26),
    "avatar_path": "/images/ivan-starkov.jpg",
    "intro": (
        "С детства увлекаюсь компьютерными играми и сборкой компьютеров. "
        "Мне интересны интерфейсы, backend-логика и проекты, которые решают понятные задачи."
    ),
    "current_study": (
        "На данный момент являюсь студентом 2 курса СВФУ на направлении "
        "прикладной информатики и компьютерных наук."
    ),
    "previous_study": (
        "Ранее учился в Красноярске в СФУ на направлении математики и компьютерных наук, "
        "что усилило интерес к аналитическому мышлению и разработке."
    ),
    "interests": "Компьютерные игры,Сборка ПК,Frontend-разработка,Backend на Python,Базы данных",
    "quote": "Интерес к играм и железу стал для меня входом в программирование и разработку собственных проектов.",
}

TIMELINE_SEED = [
    {
        "period_label": "2004",
        "title": "Родился в Якутске",
        "description": "Родился 26 сентября 2004 года в городе Якутск.",
        "location": "Якутск",
        "sort_order": 1,
    },
    {
        "period_label": "Детство",
        "title": "Школа в Момском улусе",
        "description": (
            "До 8 класса жил и учился в селе Чуумпу Кытыл Момского улуса, "
            "в Тебюляхской средней общеобразовательной школе."
        ),
        "location": "Чуумпу Кытыл, Момский улус",
        "sort_order": 2,
    },
    {
        "period_label": "Старшие классы",
        "title": "Возвращение в Якутск",
        "description": "Переехал обратно в Якутск и окончил Октемский НОЦ.",
        "location": "Якутск",
        "sort_order": 3,
    },
    {
        "period_label": "После школы",
        "title": "Обучение в СФУ",
        "description": "Начал обучение в Красноярске на направлении математики и компьютерных наук.",
        "location": "Красноярск",
        "sort_order": 4,
    },
    {
        "period_label": "Сейчас",
        "title": "СВФУ, 2 курс",
        "description": (
            "Продолжаю обучение в СВФУ на направлении прикладной информатики и компьютерных наук "
            "и развиваюсь в веб-разработке."
        ),
        "location": "Якутск",
        "sort_order": 5,
    },
]

PROJECT_SEED = [
    {
        "title": "Конфигуратор игрового ПК",
        "description": (
            "Учебный сервис для подбора комплектующих по бюджету и целям пользователя. "
            "Отдельное внимание уделено удобству интерфейса и структуре каталога."
        ),
        "stack": "Vue 3, FastAPI, SQLite",
        "project_url": "https://example.com/pc-configurator",
        "year": 2026,
        "featured": True,
        "sort_order": 1,
    },
    {
        "title": "Трекер учебных задач",
        "description": (
            "Приложение для контроля дедлайнов, заметок и статусов по учебным проектам. "
            "Сделано как pet-проект для повседневного использования."
        ),
        "stack": "Python, FastAPI, SQLAlchemy",
        "project_url": "https://example.com/study-tracker",
        "year": 2025,
        "featured": False,
        "sort_order": 2,
    },
    {
        "title": "Мини-каталог комплектующих",
        "description": (
            "Небольшая веб-база комплектующих и сборок с фильтрацией по типу железа, "
            "ценовому сегменту и назначению."
        ),
        "stack": "Vue 3, REST API, SQLite",
        "project_url": "https://example.com/hardware-catalog",
        "year": 2024,
        "featured": False,
        "sort_order": 3,
    },
]


def seed_database(db: Session) -> None:
    profile_exists = db.scalar(select(Profile.id).limit(1))
    if not profile_exists:
        db.add(Profile(**PROFILE_SEED))

    timeline_exists = db.scalar(select(TimelineEvent.id).limit(1))
    if not timeline_exists:
        db.add_all(TimelineEvent(**item) for item in TIMELINE_SEED)

    project_exists = db.scalar(select(Project.id).limit(1))
    if not project_exists:
        db.add_all(Project(**item) for item in PROJECT_SEED)

    admin = db.scalar(select(AdminUser).where(AdminUser.username == settings.admin_username))
    if admin is None:
        db.add(
            AdminUser(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
            )
        )

    db.commit()

