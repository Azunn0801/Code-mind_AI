from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(UTC)


class Role(StrEnum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    CONTENT_ADMIN = "content_admin"
    ORG_ADMIN = "org_admin"


class ConsentPurpose(StrEnum):
    INTEGRITY = "academic_integrity"
    TEACHER_VISIBILITY = "teacher_visibility"


class SessionStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class SubmissionStatus(StrEnum):
    QUEUED = "queued"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class User:
    id: str
    email: str
    display_name: str
    role: Role
    organization_id: str | None = "org_demo_codemind"


@dataclass(slots=True)
class SourceVersion:
    id: str
    source_id: str
    version_label: str
    title: str
    url: str
    checksum: str
    retrieved_at: datetime
    excerpt: str


@dataclass(slots=True)
class LessonStep:
    sequence: int
    key: str
    title: str
    objective: str


@dataclass(slots=True)
class Lesson:
    slug: str
    version: int
    title: str
    objective: str
    source: SourceVersion
    steps: list[LessonStep]
    expected_concept_pairs: set[tuple[str, str, str]]
    hints: dict[int, str]


@dataclass(slots=True)
class Consent:
    purpose: ConsentPurpose
    granted: bool
    policy_version: str
    granted_at: datetime


@dataclass(slots=True)
class UserConsent:
    """The user's current choice for a privacy/integrity purpose.

    A learning session also keeps the consent captured when that session was
    started.  This record is the user-level control used for an explicit later
    grant or revocation; a revocation takes effect immediately for access
    checks without rewriting historical session evidence.
    """

    user_id: str
    purpose: ConsentPurpose
    granted: bool
    policy_version: str
    version: int
    created_at: datetime
    updated_at: datetime
    granted_at: datetime | None = None
    revoked_at: datetime | None = None


@dataclass(slots=True)
class Submission:
    id: str
    session_id: str
    code: str
    status: SubmissionStatus
    passed_count: int
    total_count: int
    results: list[dict[str, Any]]
    idempotency_key: str
    created_at: datetime = field(default_factory=utc_now)
    completed_at: datetime | None = None


@dataclass(slots=True)
class AIInteraction:
    id: str
    session_id: str
    question: str
    refused_complete_answer: bool
    policy_version: str
    model_id: str
    created_at: datetime = field(default_factory=utc_now)
    opened_hints: list[int] = field(default_factory=list)
    policy_decision: str = "allow_socratic"
    citation_source_id: str | None = None
    quota_cost: int = 1
    latency_ms: int = 0


@dataclass(slots=True)
class AnalyticsEvent:
    """Small, privacy-aware audit/analytics record for product decisions."""

    id: str
    event_name: str
    user_id: str
    session_id: str | None
    properties: dict[str, Any]
    occurred_at: datetime = field(default_factory=utc_now)
    source: str = "api"


@dataclass(slots=True)
class LearningEvidence:
    id: str
    session_id: str
    lesson_slug: str
    before_code: str
    after_code: str
    passed_count: int
    total_count: int
    hint_levels: list[int]
    selected_terms: list[str]
    completed_at: datetime


@dataclass(slots=True)
class LearningSession:
    id: str
    user_id: str
    organization_id: str | None
    lesson_slug: str
    lesson_version: int
    status: SessionStatus = SessionStatus.IN_PROGRESS
    current_step: int = 1
    version: int = 1
    consents: dict[ConsentPurpose, Consent] = field(default_factory=dict)
    selected_terms: list[str] = field(default_factory=list)
    concept_score: int = 0
    concept_passed: bool = False
    submission_ids: list[str] = field(default_factory=list)
    ai_interaction_ids: list[str] = field(default_factory=list)
    hint_levels: list[int] = field(default_factory=list)
    completed_at: datetime | None = None

    @classmethod
    def create(cls, user: User, lesson: Lesson, integrity: bool, teacher_visibility: bool) -> "LearningSession":
        now = utc_now()
        policy = "consent-v1"
        return cls(
            id=f"ls_{uuid4().hex[:12]}",
            user_id=user.id,
            organization_id=user.organization_id,
            lesson_slug=lesson.slug,
            lesson_version=lesson.version,
            consents={
                ConsentPurpose.INTEGRITY: Consent(
                    purpose=ConsentPurpose.INTEGRITY,
                    granted=integrity,
                    policy_version=policy,
                    granted_at=now,
                ),
                ConsentPurpose.TEACHER_VISIBILITY: Consent(
                    purpose=ConsentPurpose.TEACHER_VISIBILITY,
                    granted=teacher_visibility,
                    policy_version=policy,
                    granted_at=now,
                ),
            },
        )
