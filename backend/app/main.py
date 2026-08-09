from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.deps import Container
from .api.routes import api_router, health_router
from .core.config import get_settings
from .core.errors import DomainError
from .domain.ports import Repository
from .infrastructure.ai import CannedSocraticGateway
from .infrastructure.memory import InMemoryRepository
from .infrastructure.persistent import PersistentRepository
from .infrastructure.postgres import PostgresRepository
from .infrastructure.runner import SimulatedDequeRunner


def build_repository(settings) -> Repository:
    if settings.repository_mode == "memory":
        return InMemoryRepository.seeded()
    if settings.repository_mode == "file":
        return PersistentRepository.seeded(settings.state_file_path)
    if settings.repository_mode == "postgres":
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL is required when REPOSITORY_MODE=postgres")
        return PostgresRepository.seeded(settings.database_url)
    raise RuntimeError(f"Unsupported REPOSITORY_MODE: {settings.repository_mode}")


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            close = getattr(app.state.container.repo, "close", None)
            if close:
                close()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="CodeMind P0 learning vertical slice API",
        docs_url="/docs" if settings.app_env != "production" else None,
        redoc_url="/redoc" if settings.app_env != "production" else None,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Demo-User"],
    )
    app.state.container = Container(
        repo=build_repository(settings),
        runner=SimulatedDequeRunner(),
        ai_gateway=CannedSocraticGateway(),
        settings=settings,
    )
    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.api_prefix)

    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message, "details": exc.details},
        )

    return app


app = create_app()
