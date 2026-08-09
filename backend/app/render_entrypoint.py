"""Render startup entrypoint for the CodeMind MVP API."""

from __future__ import annotations

import os

import uvicorn

from .core.config import get_settings
from .infrastructure.postgres import bootstrap_postgres_schema


def main() -> None:
    settings = get_settings()
    if settings.repository_mode == "postgres":
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL is required when REPOSITORY_MODE=postgres")
        bootstrap_postgres_schema(settings.database_url)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
