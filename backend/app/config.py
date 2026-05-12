from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent


@dataclass(frozen=True)
class Settings:
    project_name: str = "Ivan Starkov Portfolio"
    database_path: Path = BACKEND_DIR / "portfolio.db"
    secret_key: str = os.getenv("PORTFOLIO_SECRET_KEY", "change-this-secret-before-production")
    admin_username: str = os.getenv("PORTFOLIO_ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("PORTFOLIO_ADMIN_PASSWORD", "starkov2004")
    token_expire_hours: int = int(os.getenv("PORTFOLIO_TOKEN_EXPIRE_HOURS", "24"))
    frontend_dist_dir: Path = PROJECT_DIR / "frontend" / "dist"

    @property
    def cors_origins(self) -> list[str]:
        raw_origins = os.getenv(
            "PORTFOLIO_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,https://starkov-project.vercel.app",
        )
        return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


settings = Settings()

