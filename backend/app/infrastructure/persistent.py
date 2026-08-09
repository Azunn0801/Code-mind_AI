"""Durable local repository for the Stage 2 single-process demo.

The adapter stores the same domain objects as InMemoryRepository in an atomic
JSON snapshot. It is intentionally a local/staging aid, not the production
PostgreSQL adapter: use one API process and keep the state file private.
"""

import json
import os
from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..domain.models import (
    AIInteraction,
    AnalyticsEvent,
    Consent,
    ConsentPurpose,
    LearningEvidence,
    LearningSession,
    Lesson,
    LessonStep,
    Role,
    SessionStatus,
    SourceVersion,
    Submission,
    SubmissionStatus,
    User,
    UserConsent,
)
from .memory import InMemoryRepository

_SCHEMA_VERSION = 1
_ENUM_TYPES = {
    "ConsentPurpose": ConsentPurpose,
    "Role": Role,
    "SessionStatus": SessionStatus,
    "SubmissionStatus": SubmissionStatus,
}
_DATACLASS_TYPES = {
    cls.__name__: cls
    for cls in (
        AIInteraction,
        AnalyticsEvent,
        Consent,
        LearningEvidence,
        LearningSession,
        Lesson,
        LessonStep,
        SourceVersion,
        Submission,
        User,
        UserConsent,
    )
}
_STATE_COLLECTIONS = (
    "users",
    "user_consents",
    "lessons",
    "sessions",
    "submissions",
    "interactions",
    "evidence",
    "analytics_events",
    "deletion_requests",
)


def _encode(value: Any) -> Any:
    if isinstance(value, Enum):
        return {"__enum__": type(value).__name__, "value": value.value}
    if isinstance(value, datetime):
        return {"__datetime__": value.isoformat()}
    if is_dataclass(value):
        return {
            "__type__": type(value).__name__,
            "fields": {field.name: _encode(getattr(value, field.name)) for field in fields(value)},
        }
    if isinstance(value, set):
        return {"__set__": [_encode(item) for item in sorted(value, key=repr)]}
    if isinstance(value, tuple):
        return {"__tuple__": [_encode(item) for item in value]}
    if isinstance(value, list):
        return [_encode(item) for item in value]
    if isinstance(value, dict):
        return {"__dict__": [[_encode(key), _encode(item)] for key, item in value.items()]}
    return value


def _decode(value: Any) -> Any:
    if isinstance(value, list):
        return [_decode(item) for item in value]
    if not isinstance(value, dict):
        return value
    if "__datetime__" in value:
        return datetime.fromisoformat(str(value["__datetime__"]))
    if "__enum__" in value:
        enum_type = _ENUM_TYPES[str(value["__enum__"])]
        return enum_type(value["value"])
    if "__set__" in value:
        return set(_decode(item) for item in value["__set__"])
    if "__tuple__" in value:
        return tuple(_decode(item) for item in value["__tuple__"])
    if "__dict__" in value:
        return {_decode(pair[0]): _decode(pair[1]) for pair in value["__dict__"]}
    if "__type__" in value:
        data_type = _DATACLASS_TYPES[str(value["__type__"])]
        return data_type(**_decode(value["fields"]))
    return {key: _decode(item) for key, item in value.items()}


class PersistentRepository(InMemoryRepository):
    """Thread-safe atomic JSON storage for a local single-process profile."""

    def __init__(self, state_file_path: str) -> None:
        super().__init__()
        self.state_file_path = Path(state_file_path)
        self._loaded_from_disk = self.state_file_path.exists()
        if self._loaded_from_disk:
            self._load()

    @classmethod
    def seeded(cls, state_file_path: str) -> "PersistentRepository":
        repo = cls(state_file_path)
        if not repo._loaded_from_disk:
            repo._seed_defaults()
        return repo

    def _seed_defaults(self) -> None:
        from .seed import build_demo_lesson

        with self._lock:
            InMemoryRepository.save_user(
                self,
                User("student_demo", "student.demo@codemind.local", "Minh — người học", Role.STUDENT),
            )
            InMemoryRepository.save_user(
                self,
                User(
                    "instructor_demo",
                    "instructor.demo@codemind.local",
                    "Lan — giảng viên",
                    Role.INSTRUCTOR,
                ),
            )
            InMemoryRepository.save_user(
                self,
                User("admin_demo", "admin.demo@codemind.local", "An — quản trị", Role.CONTENT_ADMIN),
            )
            InMemoryRepository.save_lesson(self, build_demo_lesson())
            self._persist_locked()

    def _snapshot(self) -> dict[str, Any]:
        return {
            "schema_version": _SCHEMA_VERSION,
            **{name: _encode(getattr(self, name)) for name in _STATE_COLLECTIONS},
        }

    def _load(self) -> None:
        try:
            payload = json.loads(self.state_file_path.read_text(encoding="utf-8"))
            snapshot = _decode(payload)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise RuntimeError(f"Không thể đọc state file Stage 2: {self.state_file_path}") from exc
        if snapshot.get("schema_version") != _SCHEMA_VERSION:
            raise RuntimeError("State file không đúng schema Stage 2.")
        with self._lock:
            for name in _STATE_COLLECTIONS:
                setattr(self, name, snapshot.get(name, {}))

    def _persist_locked(self) -> None:
        self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.state_file_path.with_name(f"{self.state_file_path.name}.tmp")
        temp_path.write_text(
            json.dumps(self._snapshot(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.replace(temp_path, self.state_file_path)

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

