from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.domain.models import ConsentPurpose, LearningSession
from app.infrastructure.postgres import PostgresRepository, create_postgres_engine
from app.main import build_repository, create_app


def test_postgres_state_repository_survives_rebuild(tmp_path):
    database_url = f"sqlite+pysqlite:///{tmp_path / 'p0-state.db'}"
    first = PostgresRepository.seeded(database_url, bootstrap_schema=True)
    user = first.get_user("student_demo")
    lesson = first.get_lesson("deque")
    assert user is not None
    assert lesson is not None

    session = LearningSession.create(user, lesson, integrity=True, teacher_visibility=False)
    session.current_step = 2
    session.version = 2
    first.save_session(session)
    assert first.check_ready() is True
    first.close()

    second = PostgresRepository.seeded(database_url, bootstrap_schema=True)
    restored = second.get_session(session.id)
    restored_lesson = second.get_lesson("deque")
    assert restored is not None
    assert restored.current_step == 2
    assert restored.version == 2
    assert restored.consents[ConsentPurpose.INTEGRITY].granted is True
    assert restored_lesson is not None
    assert restored_lesson.source.url.startswith("https://docs.python.org/")
    second.close()


def test_render_postgres_url_uses_psycopg3_driver():
    engine = create_postgres_engine("postgresql://demo:demo@db:5432/codemind")
    try:
        assert engine.url.drivername == "postgresql+psycopg"
    finally:
        engine.dispose()


def test_build_repository_selects_postgres_mode(monkeypatch):
    expected = object()
    captured: dict[str, str] = {}

    def seeded(database_url: str):
        captured["database_url"] = database_url
        return expected

    monkeypatch.setattr(PostgresRepository, "seeded", staticmethod(seeded))
    settings = SimpleNamespace(
        repository_mode="postgres",
        database_url="postgresql+psycopg://demo:demo@db:5432/codemind",
    )
    assert build_repository(settings) is expected
    assert captured["database_url"] == settings.database_url


def test_ready_health_checks_the_postgres_repository(tmp_path, monkeypatch):
    database_url = f"sqlite+pysqlite:///{tmp_path / 'ready-state.db'}"
    setup = PostgresRepository.seeded(database_url, bootstrap_schema=True)
    setup.close()

    with monkeypatch.context() as context:
        context.setenv("REPOSITORY_MODE", "postgres")
        context.setenv("DATABASE_URL", database_url)
        get_settings.cache_clear()
        app = create_app()
        with TestClient(app) as client:
            response = client.get("/health/ready")
    get_settings.cache_clear()

    assert response.status_code == 200
    assert response.json()["dependencies"]["database"] == "up"
