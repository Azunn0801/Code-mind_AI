from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .domain.models import ConsentPurpose, Role, SessionStatus, SubmissionStatus


class DemoSessionRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    role: Role | None = None

    @field_validator("email")
    @classmethod
    def validate_email_shape(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("email không hợp lệ")
        return normalized


class DemoSessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user_id: str
    role: Role
    display_name: str


class ConsentUpdateRequest(BaseModel):
    granted: bool
    policy_version: str = Field(min_length=1, max_length=32)
    expected_version: int | None = Field(default=None, ge=0)

    @field_validator("policy_version")
    @classmethod
    def normalize_policy_version(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("policy_version không được để trống")
        return normalized


class UserConsentResponse(BaseModel):
    user_id: str
    purpose: ConsentPurpose
    granted: bool
    policy_version: str
    version: int
    created_at: datetime
    updated_at: datetime
    granted_at: datetime | None = None
    revoked_at: datetime | None = None


class SourceResponse(BaseModel):
    id: str
    version_label: str
    title: str
    url: str
    checksum: str
    retrieved_at: datetime
    excerpt: str


class LessonStepResponse(BaseModel):
    sequence: int
    key: str
    title: str
    objective: str


class LessonResponse(BaseModel):
    slug: str
    version: int
    title: str
    objective: str
    source: SourceResponse
    steps: list[LessonStepResponse]


class LearningSessionCreate(BaseModel):
    lesson_slug: str = "deque"
    integrity_consent: bool
    teacher_visibility: bool = False


class ConsentResponse(BaseModel):
    purpose: str
    granted: bool
    policy_version: str
    granted_at: datetime


class LearningSessionResponse(BaseModel):
    id: str
    user_id: str
    lesson_slug: str
    lesson_version: int
    status: SessionStatus
    current_step: int
    version: int
    selected_terms: list[str]
    concept_score: int
    concept_passed: bool
    submission_ids: list[str]
    hint_levels: list[int]
    consents: list[ConsentResponse]
    completed_at: datetime | None = None


class ProgressPatch(BaseModel):
    current_step: int = Field(ge=1, le=6)
    expected_version: int = Field(ge=1)


class TermSelectionRequest(BaseModel):
    terms: list[str] = Field(min_length=1, max_length=5)


class ConceptPair(BaseModel):
    from_term: str
    to_term: str
    relationship: str


class ConceptAnswerRequest(BaseModel):
    pairs: list[ConceptPair] = Field(min_length=1, max_length=5)


class ConceptAnswerResponse(BaseModel):
    score: int
    total: int
    passed: bool
    feedback: str
    session: LearningSessionResponse


class SubmissionCreate(BaseModel):
    code: str = Field(min_length=1, max_length=20_000)
    idempotency_key: str | None = Field(default=None, max_length=120)

    @field_validator("idempotency_key")
    @classmethod
    def normalize_idempotency_key(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("idempotency_key không được để trống")
        return normalized


class TestResultResponse(BaseModel):
    name: str
    passed: bool
    message: str


class SubmissionResponse(BaseModel):
    id: str
    session_id: str
    status: SubmissionStatus
    passed_count: int
    total_count: int
    results: list[TestResultResponse]
    idempotency_key: str
    created_at: datetime
    completed_at: datetime | None = None


class AIInteractionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2_000)


class AICitationResponse(BaseModel):
    source_id: str
    version_label: str
    title: str
    url: str


class AIInteractionResponse(BaseModel):
    id: str
    refused_complete_answer: bool
    policy_version: str
    model_id: str
    message: str
    next_action: str
    opened_hints: list[int]
    policy_decision: str
    citation: AICitationResponse
    quota_cost: int
    quota_remaining: int
    latency_ms: int


class HintResponse(BaseModel):
    interaction_id: str
    level: int
    hint: str
    opened_hints: list[int]
    remaining: int


class AnalyticsEventResponse(BaseModel):
    id: str
    event_name: str
    user_id: str
    session_id: str | None
    properties: dict[str, Any]
    occurred_at: datetime
    source: str


class AnalyticsEventListResponse(BaseModel):
    events: list[AnalyticsEventResponse]
    total: int


class TeacherSessionSummaryResponse(BaseModel):
    session_id: str
    learner_id: str
    lesson_slug: str
    status: SessionStatus
    current_step: int
    concept_score: int
    concept_passed: bool
    test_passed: bool
    hint_levels: list[int]
    completed_at: datetime | None
    teacher_visibility: bool
    evidence_available: bool


class TeacherSessionListResponse(BaseModel):
    sessions: list[TeacherSessionSummaryResponse]
    next_cursor: str | None = None


class EvidenceResponse(BaseModel):
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


class CompletionResponse(BaseModel):
    session: LearningSessionResponse
    evidence: EvidenceResponse


class DeletionRequestResponse(BaseModel):
    request_id: str
    status: str = "queued"
    message: str = "Yêu cầu xóa dữ liệu đã được ghi nhận."


class HealthResponse(BaseModel):
    status: str
    environment: str
    dependencies: dict[str, str]


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: str
    message: str
    details: dict[str, Any] | None = None
