"""PostgreSQL-backed state repository for the P0 vertical slice.

The domain layer is intentionally kept independent from SQLAlchemy. Until the
P0 entities are mapped one-by-one to the logical schema, this adapter stores a
versioned, encoded aggregate snapshot in PostgreSQL. It is a durable runtime
adapter (not a fake configuration seam) and is safe for the single API replica
used by the MVP deployment profile.

``application_state`` is created by ``migrations/001_initial.sql``. Tests can
opt into ``bootstrap_schema=True`` with SQLite; production must run migrations
before the API starts.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    select,
    text,
)
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError, IntegrityError

from ..domain.models import (
    AIInteraction,
    AnalyticsEvent,
    LearningEvidence,
    LearningSession,
    Lesson,
    Submission,
    User,
    UserConsent,
)
from .memory import InMemoryRepository
from .persistent import _SCHEMA_VERSION, _STATE_COLLECTIONS, _decode, _encode

_STATE_KEY = "p0_runtime"
_METADATA = MetaData()
_APPLICATION_STATE = Table(
    "application_state",
    _METADATA,
    Column("state_key", String(80), primary_key=True),
    Column("schema_version", Integer, nullable=False),
    Column("payload", JSON, nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def create_postgres_engine(database_url: str) -> Engine:
    """Create the engine only when the PostgreSQL repository mode is selected."""

    return create_engine(database_url, pool_pre_ping=True, future=True)


class PostgresRepository(InMemoryRepository):
    """Persist the current P0 domain snapshot in a PostgreSQL transaction.

    The repository keeps the existing port intact, so routes and policies do
    not need to know whether the chosen runtime profile is memory, file or
    PostgreSQL. A snapshot is deliberately bounded to one API replica: it is
    suitable for the MVP's deployed vertical slice, not a multi-writer scale
    out strategy.
    """

    def __init__(self, database_url: str, *, bootstrap_schema: bool = False) -> None:
        super().__init__()
        self.engine = create_postgres_engine(database_url)
        if bootstrap_schema:
            _METADATA.create_all(self.engine)
        self._loaded_from_database = self._load()

    @classmethod
    def seeded(cls, database_url: str, *, bootstrap_schema: bool = False) -> PostgresRepository:
        repo = cls(database_url, bootstrap_schema=bootstrap_schema)
        if not repo._loaded_from_database:
            repo._seed_defaults()
        return repo

    def _load(self) -> bool:
        try:
            with self.engine.connect() as connection:
                row = connection.execute(
                    select(_APPLICATION_STATE.c.schema_version, _APPLICATION_STATE.c.payload).where(
                        _APPLICATION_STATE.c.state_key == _STATE_KEY
                    )
                ).mappings().one_or_none()
        except DBAPIError as exc:
            raise RuntimeError(
                "PostgreSQL state storage is unavailable. Run migrations before starting the API."
            ) from exc

        if row is None:
            return False
        if row["schema_version"] != _SCHEMA_VERSION:
            raise RuntimeError("PostgreSQL state does not match the supported P0 schema version.")

        try:
            snapshot = _decode(row["payload"])
            if snapshot.get("schema_version") != _SCHEMA_VERSION:
                raise ValueError("payload schema version mismatch")
            with self._lock:
                for name in _STATE_COLLECTIONS:
                    setattr(self, name, snapshot.get(name, {}))
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError("PostgreSQL state payload is invalid.") from exc
        return True

    def _seed_defaults(self) -> None:
        """Use the canonical in-memory seed, then durably store it once."""

        seeded = InMemoryRepository.seeded()
        with self._lock:
            for name in _STATE_COLLECTIONS:
                setattr(self, name, getattr(seeded, name))
            self._persist_locked()

    def _snapshot(self) -> dict[str, Any]:
        return {
            "schema_version": _SCHEMA_VERSION,
            **{name: _encode(getattr(self, name)) for name in _STATE_COLLECTIONS},
        }

    def _persist_locked(self) -> None:
        values = {
            "state_key": _STATE_KEY,
            "schema_version": _SCHEMA_VERSION,
            "payload": self._snapshot(),
            "updated_at": datetime.now(UTC),
        }
        try:
            with self.engine.begin() as connection:
                if connection.dialect.name == "postgresql":
                    statement = postgres_insert(_APPLICATION_STATE).values(**values).on_conflict_do_update(
                        index_elements=[_APPLICATION_STATE.c.state_key],
                        set_={
                            "schema_version": values["schema_version"],
                            "payload": values["payload"],
                            "updated_at": values["updated_at"],
                        },
                    )
                    connection.execute(statement)
                    return

                updated = connection.execute(
                    _APPLICATION_STATE.update()
                    .where(_APPLICATION_STATE.c.state_key == _STATE_KEY)
                    .values(**values)
                )
                if not updated.rowcount:
                    connection.execute(_APPLICATION_STATE.insert().values(**values))
        except (DBAPIError, IntegrityError) as exc:
            raise RuntimeError("PostgreSQL state could not be persisted.") from exc

    def check_ready(self) -> bool:
        """Verify both database connectivity and the migrated state table."""

        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                connection.execute(select(_APPLICATION_STATE.c.state_key).limit(1))
        except DBAPIError as exc:
            raise RuntimeError("PostgreSQL repository is not ready.") from exc
        return True

    def close(self) -> None:
        self.engine.dispose()

    def save_user(self, user: User) -> None:
        with self._lock:
            super().save_user(user)
            self._persist_locked()

    def save_lesson(self, lesson: Lesson) -> None:
        with self._lock:
            super().save_lesson(lesson)
            self._persist_locked()

    def save_user_consent(self, consent: UserConsent) -> None:
        with self._lock:
            super().save_user_consent(consent)
            self._persist_locked()

    def save_session(self, session: LearningSession) -> None:
        with self._lock:
            super().save_session(session)
            self._persist_locked()

    def save_submission(self, submission: Submission) -> None:
        with self._lock:
            super().save_submission(submission)
            self._persist_locked()

    def save_interaction(self, interaction: AIInteraction) -> None:
        with self._lock:
            super().save_interaction(interaction)
            self._persist_locked()

    def save_evidence(self, evidence: LearningEvidence) -> None:
        with self._lock:
            super().save_evidence(evidence)
            self._persist_locked()

    def save_analytics_event(self, event: AnalyticsEvent) -> None:
        with self._lock:
            super().save_analytics_event(event)
            self._persist_locked()

    def create_deletion_request(self, user_id: str) -> str:
        with self._lock:
            request_id = super().create_deletion_request(user_id)
            self._persist_locked()
            return request_id
