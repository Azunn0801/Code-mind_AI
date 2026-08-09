import re
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, Query, Request
from fastapi.responses import JSONResponse

from ..core.demo_auth import issue_demo_token
from ..core.errors import DomainError
from ..domain.models import (
    AIInteraction,
    AnalyticsEvent,
    ConsentPurpose,
    LearningEvidence,
    LearningSession,
    Role,
    SessionStatus,
    Submission,
    SubmissionStatus,
    User,
    UserConsent,
    utc_now,
)
from ..domain.policies import (
    require_instructor_access,
    require_integrity_consent,
    require_session_owner,
    validate_completion,
    validate_progress_step,
)
from ..schemas import (
    AICitationResponse,
    AIInteractionRequest,
    AIInteractionResponse,
    AnalyticsEventListResponse,
    AnalyticsEventResponse,
    CompletionResponse,
    ConceptAnswerRequest,
    ConceptAnswerResponse,
    ConsentUpdateRequest,
    DeletionRequestResponse,
    DemoSessionRequest,
    DemoSessionResponse,
    EvidenceResponse,
    HealthResponse,
    HintResponse,
    LearningSessionCreate,
    ProgressPatch,
    SubmissionCreate,
    SubmissionResponse,
    TeacherSessionListResponse,
    TeacherSessionSummaryResponse,
    TermSelectionRequest,
    UserConsentResponse,
)
from .deps import Container, current_user, get_container
from .presenters import lesson_response, session_response, submission_response

health_router = APIRouter(tags=["health"])
api_router = APIRouter()


def _track_event(
    container: Container,
    user: User,
    event_name: str,
    session_id: str | None = None,
    properties: dict[str, object] | None = None,
) -> None:
    """Persist a redacted product/audit event without raw code or full prompts."""

    container.repo.save_analytics_event(
        AnalyticsEvent(
            id=f"evt_{uuid4().hex[:12]}",
            event_name=event_name,
            user_id=user.id,
            session_id=session_id,
            properties=properties or {},
        )
    )


@health_router.get("/health/live", response_model=HealthResponse)
def health_live(container: Container = Depends(get_container)) -> HealthResponse:
    return HealthResponse(status="ok", environment=container.settings.app_env, dependencies={"api": "up"})


@health_router.get("/health/ready", response_model=HealthResponse)
def health_ready(container: Container = Depends(get_container)) -> HealthResponse:
    dependencies = {
        "repository": container.settings.repository_mode,
        "runner": container.settings.code_runner_mode,
        "ai_gateway": container.settings.ai_mode,
    }
    probes = {
        "repository_status": container.repo,
        "runner_status": container.runner,
        "ai_gateway_status": container.ai_gateway,
    }
    unavailable = False
    for name, dependency in probes.items():
        check_ready = getattr(dependency, "check_ready", None)
        if check_ready is None:
            dependencies[name] = "not_checked"
            continue
        try:
            check_ready()
            dependencies[name] = "up"
        except Exception:
            dependencies[name] = "down"
            unavailable = True
    if container.settings.repository_mode == "postgres":
        dependencies["database"] = dependencies["repository_status"]
    if unavailable:
        payload = HealthResponse(
            status="unavailable",
            environment=container.settings.app_env,
            dependencies=dependencies,
        )
        return JSONResponse(status_code=503, content=payload.model_dump())
    return HealthResponse(
        status="ok",
        environment=container.settings.app_env,
        dependencies=dependencies,
    )


@api_router.post(
    "/demo/session",
    response_model=DemoSessionResponse,
    status_code=201,
    tags=["auth"],
)
def create_demo_session(payload: DemoSessionRequest, container: Container = Depends(get_container)):
    user = container.repo.find_user_by_email(str(payload.email))
    if not user:
        raise DomainError("demo_user_not_found", "Tài khoản demo không tồn tại.", 404)
    if payload.role and payload.role != user.role:
        raise DomainError("role_mismatch", "Vai trò không khớp với tài khoản demo.", 403)
    return DemoSessionResponse(
        access_token=issue_demo_token(
            user.id,
            container.settings.demo_token_secret,
            container.settings.demo_token_ttl_seconds,
        ),
        expires_in=container.settings.demo_token_ttl_seconds,
        user_id=user.id,
        role=user.role,
        display_name=user.display_name,
    )


@api_router.get("/lessons/{slug}", tags=["content"])
def get_lesson(slug: str, container: Container = Depends(get_container)):
    lesson = container.repo.get_lesson(slug)
    if not lesson:
        raise DomainError("lesson_not_found", "Không tìm thấy bài học.", 404)
    return lesson_response(lesson)


@api_router.post("/learning-sessions", status_code=201, tags=["learning"])
def create_learning_session(
    payload: LearningSessionCreate,
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    if user.role != Role.STUDENT:
        raise DomainError("student_required", "Chỉ tài khoản người học mới có thể bắt đầu bài học.", 403)
    if not payload.integrity_consent:
        raise DomainError("consent_required", "Bạn cần đồng ý cam kết học tập trước khi bắt đầu.", 403)
    lesson = container.repo.get_lesson(payload.lesson_slug)
    if not lesson:
        raise DomainError("lesson_not_found", "Không tìm thấy bài học.", 404)
    session = LearningSession.create(user, lesson, payload.integrity_consent, payload.teacher_visibility)
    container.repo.save_session(session)
    _track_event(
        container,
        user,
        "learning_session_started",
        session.id,
        {"lesson_slug": session.lesson_slug, "lesson_version": session.lesson_version},
    )
    return session_response(session)


@api_router.patch(
    "/me/consents/{purpose}",
    response_model=UserConsentResponse,
    tags=["privacy"],
)
def update_my_consent(
    purpose: ConsentPurpose,
    payload: ConsentUpdateRequest,
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    if user.role != Role.STUDENT:
        raise DomainError(
            "student_required",
            "Chỉ tài khoản người học mới có thể thay đổi lựa chọn đồng ý của mình.",
            403,
        )
    existing = container.repo.get_user_consent(user.id, purpose)
    current_version = existing.version if existing else 0
    if payload.expected_version is not None and payload.expected_version != current_version:
        raise DomainError(
            "version_conflict",
            "Lựa chọn đồng ý đã được cập nhật ở nơi khác. Hãy tải lại trước khi thử lại.",
            409,
            {"current_version": current_version},
        )

    now = utc_now()
    consent = UserConsent(
        user_id=user.id,
        purpose=purpose,
        granted=payload.granted,
        policy_version=payload.policy_version,
        version=current_version + 1,
        created_at=existing.created_at if existing else now,
        updated_at=now,
        granted_at=now if payload.granted else (existing.granted_at if existing else None),
        revoked_at=now if not payload.granted else None,
    )
    container.repo.save_user_consent(consent)
    _track_event(
        container,
        user,
        "consent_updated",
        properties={
            "purpose": purpose.value,
            "granted": consent.granted,
            "version": consent.version,
        },
    )
    return UserConsentResponse.model_validate(consent, from_attributes=True)


def _owned_session(session_id: str, user: User, container: Container) -> LearningSession:
    session = container.repo.get_session(session_id)
    if not session:
        raise DomainError("session_not_found", "Không tìm thấy phiên học.", 404)
    require_session_owner(session, user)
    return session


def _require_active_integrity_consent(
    session: LearningSession, user: User, container: Container
) -> None:
    user_consent = container.repo.get_user_consent(user.id, ConsentPurpose.INTEGRITY)
    require_integrity_consent(session, user_consent)


def _audit_access_denied(
    container: Container,
    user: User,
    session_id: str | None,
    resource: str,
    reason: str,
) -> None:
    _track_event(
        container,
        user,
        "access_denied",
        session_id,
        {"resource": resource, "reason": reason},
    )


def _require_teacher_read_access(
    session: LearningSession,
    user: User,
    container: Container,
    resource: str,
) -> None:
    learner_consent = container.repo.get_user_consent(
        session.user_id, ConsentPurpose.TEACHER_VISIBILITY
    )
    try:
        require_instructor_access(session, user, learner_consent)
    except DomainError as exc:
        _audit_access_denied(container, user, session.id, resource, exc.code)
        raise


def _teacher_session_summary(
    session: LearningSession, container: Container
) -> TeacherSessionSummaryResponse:
    evidence = container.repo.get_evidence(session.id)
    teacher_consent = session.consents.get(ConsentPurpose.TEACHER_VISIBILITY)
    return TeacherSessionSummaryResponse(
        session_id=session.id,
        learner_id=session.user_id,
        lesson_slug=session.lesson_slug,
        status=session.status,
        current_step=session.current_step,
        concept_score=session.concept_score,
        concept_passed=session.concept_passed,
        test_passed=bool(evidence and evidence.passed_count == evidence.total_count),
        hint_levels=list(session.hint_levels),
        completed_at=session.completed_at,
        teacher_visibility=bool(teacher_consent and teacher_consent.granted),
        evidence_available=evidence is not None,
    )


def _term_in_pinned_source(term: str, lesson_source_text: str) -> bool:
    normalized_term = term.casefold()
    normalized_source = lesson_source_text.casefold()
    return bool(re.search(rf"(?<!\\w){re.escape(normalized_term)}(?!\\w)", normalized_source))


@api_router.get("/learning-sessions/{session_id}", tags=["learning"])
def get_learning_session(
    session_id: str,
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    return session_response(_owned_session(session_id, user, container))


@api_router.patch("/learning-sessions/{session_id}/progress", tags=["learning"])
def patch_progress(
    session_id: str,
    payload: ProgressPatch,
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    session = _owned_session(session_id, user, container)
    _require_active_integrity_consent(session, user, container)
    if payload.expected_version != session.version:
        raise DomainError(
            "version_conflict",
            "Phiên học đã được cập nhật ở nơi khác. Hãy tải lại tiến trình.",
            409,
            {"current_version": session.version},
        )
    validate_progress_step(session, payload.current_step)
    session.current_step = max(session.current_step, payload.current_step)
    session.version += 1
    container.repo.save_session(session)
    _track_event(container, user, "progress_updated", session.id, {"current_step": session.current_step})
    return session_response(session)


@api_router.post("/sessions/{session_id}/terms", status_code=201, tags=["learning"])
def select_terms(
    session_id: str,
    payload: TermSelectionRequest,
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    session = _owned_session(session_id, user, container)
    _require_active_integrity_consent(session, user, container)
    terms = list(dict.fromkeys(term.strip().lower() for term in payload.terms if term.strip()))
    if not terms:
        raise DomainError("terms_required", "Hãy chọn ít nhất một thuật ngữ.", 422)
    lesson = container.repo.get_lesson(session.lesson_slug)
    assert lesson is not None
    source_text = f"{lesson.source.title} {lesson.source.excerpt}"
    invalid_terms = [term for term in terms if not _term_in_pinned_source(term, source_text)]
    if invalid_terms:
        raise DomainError(
            "terms_not_in_source",
            "Chỉ chọn thuật ngữ xuất hiện trong tài liệu chính thức của bài học.",
            422,
            {"invalid_terms": invalid_terms, "source_version": lesson.source.version_label},
        )
    session.selected_terms = terms
    session.current_step = max(session.current_step, 2)
    session.version += 1
    container.repo.save_session(session)
    _track_event(container, user, "terms_selected", session.id, {"selected_count": len(terms)})
    return session_response(session)


@api_router.post("/sessions/{session_id}/concept-answers", response_model=ConceptAnswerResponse, tags=["learning"])
def submit_concept_answer(
    session_id: str,
    payload: ConceptAnswerRequest,
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    session = _owned_session(session_id, user, container)
    _require_active_integrity_consent(session, user, container)
    lesson = container.repo.get_lesson(session.lesson_slug)
    assert lesson is not None
    received = {(p.from_term.lower(), p.to_term.lower(), p.relationship.lower()) for p in payload.pairs}
    score = len(received.intersection(lesson.expected_concept_pairs))
    total = len(lesson.expected_concept_pairs)
    session.concept_score = score
    session.concept_passed = score == total
    session.current_step = max(session.current_step, 3 if session.concept_passed else 2)
    session.version += 1
    container.repo.save_session(session)
    _track_event(
        container,
        user,
        "concept_checked",
        session.id,
        {"score": score, "total": total, "passed": session.concept_passed},
    )
    feedback = "Tốt lắm, các mối quan hệ đã đúng." if session.concept_passed else "Hãy xem lại thuật ngữ và thử nối lại."
    return ConceptAnswerResponse(
        score=score,
        total=total,
        passed=session.concept_passed,
        feedback=feedback,
        session=session_response(session),
    )


@api_router.post(
    "/sessions/{session_id}/submissions",
    response_model=SubmissionResponse,
    status_code=202,
    tags=["assessment"],
)
def create_submission(
    session_id: str,
    payload: SubmissionCreate,
    request: Request,
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
    idempotency_header: str | None = Header(default=None, alias="Idempotency-Key"),
):
    session = _owned_session(session_id, user, container)
    _require_active_integrity_consent(session, user, container)
    header_key = idempotency_header.strip() if idempotency_header else None
    if header_key and len(header_key) > 120:
        raise DomainError("invalid_idempotency_key", "Idempotency-Key dài tối đa 120 ký tự.", 422)
    if header_key and payload.idempotency_key and header_key != payload.idempotency_key:
        raise DomainError(
            "idempotency_key_conflict",
            "Idempotency-Key ở header và nội dung gửi lên không khớp.",
            409,
        )
    key = header_key or payload.idempotency_key
    if not key:
        raise DomainError(
            "idempotency_key_required",
            "Hãy gửi Idempotency-Key để lần thử lại không tạo thêm bài nộp.",
            422,
        )
    existing = container.repo.find_submission_by_key(session_id, key)
    if existing:
        return submission_response(existing)
    run = container.runner.run(payload.code)
    submission = Submission(
        id=f"sub_{uuid4().hex[:12]}",
        session_id=session_id,
        code=payload.code,
        status=SubmissionStatus.COMPLETED,
        passed_count=run.passed_count,
        total_count=run.total_count,
        results=run.results,
        idempotency_key=key,
        completed_at=utc_now(),
    )
    container.repo.save_submission(submission)
    session.submission_ids.append(submission.id)
    session.current_step = max(session.current_step, 4)
    session.version += 1
    container.repo.save_session(session)
    _track_event(
        container,
        user,
        "submission_evaluated",
        session.id,
        {
            "passed_count": submission.passed_count,
            "total_count": submission.total_count,
            "status": submission.status.value,
        },
    )
    return submission_response(submission)


@api_router.get("/submissions/{submission_id}", response_model=SubmissionResponse, tags=["assessment"])
def get_submission(
    submission_id: str,
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    submission = container.repo.get_submission(submission_id)
    if not submission:
        raise DomainError("submission_not_found", "Không tìm thấy lần nộp bài.", 404)
    session = container.repo.get_session(submission.session_id)
    if not session:
        raise DomainError("session_not_found", "Không tìm thấy phiên học.", 404)
    if user.id != session.user_id:
        _require_teacher_read_access(session, user, container, "submission")
    return submission_response(submission)


@api_router.post("/sessions/{session_id}/ai-interactions", response_model=AIInteractionResponse, tags=["ai"])
def create_ai_interaction(
    session_id: str,
    payload: AIInteractionRequest,
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    session = _owned_session(session_id, user, container)
    _require_active_integrity_consent(session, user, container)
    lesson = container.repo.get_lesson(session.lesson_slug)
    assert lesson is not None
    used = len(container.repo.list_interactions(session.id))
    limit = container.settings.ai_max_interactions_per_session
    if used >= limit:
        raise DomainError(
            "ai_quota_exceeded",
            "Bạn đã dùng hết lượt hỏi AI trong phiên học này.",
            429,
            {"limit": limit, "used": used, "remaining": 0},
        )
    result = container.ai_gateway.answer(payload.question, lesson)
    interaction = AIInteraction(
        id=f"ai_{uuid4().hex[:12]}",
        session_id=session_id,
        question=payload.question,
        refused_complete_answer=result.refused_complete_answer,
        policy_version=result.policy_version,
        model_id=result.model_id,
        policy_decision=result.policy_decision,
        citation_source_id=result.citation_source_id,
        quota_cost=result.quota_cost,
        latency_ms=result.latency_ms,
    )
    container.repo.save_interaction(interaction)
    session.ai_interaction_ids.append(interaction.id)
    session.current_step = max(session.current_step, 5)
    session.version += 1
    container.repo.save_session(session)
    _track_event(
        container,
        user,
        "ai_interaction_created",
        session.id,
        {
            "policy_decision": result.policy_decision,
            "policy_version": result.policy_version,
            "model_id": result.model_id,
            "citation_attached": bool(result.citation_source_id),
            "quota_cost": result.quota_cost,
            "latency_ms": result.latency_ms,
        },
    )
    return AIInteractionResponse(
        id=interaction.id,
        refused_complete_answer=interaction.refused_complete_answer,
        policy_version=interaction.policy_version,
        model_id=interaction.model_id,
        message=result.message,
        next_action=result.next_action,
        opened_hints=[],
        policy_decision=result.policy_decision,
        citation=AICitationResponse(
            source_id=result.citation_source_id,
            version_label=result.citation_version_label,
            title=result.citation_title,
            url=result.citation_url,
        ),
        quota_cost=result.quota_cost,
        quota_remaining=max(0, limit - used - result.quota_cost),
        latency_ms=result.latency_ms,
    )


@api_router.post("/ai-interactions/{interaction_id}/hints/{level}/open", response_model=HintResponse, tags=["ai"])
def open_hint(
    interaction_id: str,
    level: int,
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    interaction = container.repo.get_interaction(interaction_id)
    if not interaction:
        raise DomainError("interaction_not_found", "Không tìm thấy lượt hỏi AI.", 404)
    session = _owned_session(interaction.session_id, user, container)
    if level not in (1, 2, 3):
        raise DomainError("invalid_hint_level", "Mức gợi ý phải từ 1 đến 3.", 422)
    if level in interaction.opened_hints:
        lesson = container.repo.get_lesson(session.lesson_slug)
        assert lesson is not None
        return HintResponse(
            interaction_id=interaction.id,
            level=level,
            hint=lesson.hints[level],
            opened_hints=interaction.opened_hints,
            remaining=3 - len(interaction.opened_hints),
        )
    expected = len(interaction.opened_hints) + 1
    if level != expected:
        raise DomainError("hint_order", f"Hãy mở gợi ý {expected} trước.", 409)
    lesson = container.repo.get_lesson(session.lesson_slug)
    assert lesson is not None
    interaction.opened_hints.append(level)
    session.hint_levels = sorted(set(session.hint_levels + [level]))
    session.version += 1
    container.repo.save_interaction(interaction)
    container.repo.save_session(session)
    _track_event(
        container,
        user,
        "hint_opened",
        session.id,
        {"interaction_id": interaction.id, "level": level, "remaining": 3 - len(interaction.opened_hints)},
    )
    return HintResponse(
        interaction_id=interaction.id,
        level=level,
        hint=lesson.hints[level],
        opened_hints=interaction.opened_hints,
        remaining=3 - len(interaction.opened_hints),
    )


@api_router.post("/sessions/{session_id}/complete", response_model=CompletionResponse, tags=["learning"])
def complete_session(
    session_id: str,
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    session = _owned_session(session_id, user, container)
    lesson = container.repo.get_lesson(session.lesson_slug)
    assert lesson is not None
    validate_completion(session, lesson)
    submissions = [container.repo.get_submission(submission_id) for submission_id in session.submission_ids]
    completed = [submission for submission in submissions if submission and submission.passed_count == submission.total_count]
    if not completed:
        raise DomainError("tests_incomplete", "Hãy sửa mã để đạt đủ 5/5 bài kiểm tra.", 409)
    if session.status.value == "completed":
        evidence = container.repo.get_evidence(session.id)
        assert evidence is not None
    else:
        before = submissions[0].code if submissions and submissions[0] else ""
        after = completed[-1].code
        session.status = SessionStatus.COMPLETED
        session.current_step = 6
        session.completed_at = utc_now()
        session.version += 1
        evidence = LearningEvidence(
            id=f"ev_{uuid4().hex[:12]}",
            session_id=session.id,
            lesson_slug=session.lesson_slug,
            before_code=before,
            after_code=after,
            passed_count=completed[-1].passed_count,
            total_count=completed[-1].total_count,
            hint_levels=session.hint_levels,
            selected_terms=session.selected_terms,
            completed_at=session.completed_at,
        )
        container.repo.save_session(session)
        container.repo.save_evidence(evidence)
        _track_event(
            container,
            user,
            "session_completed",
            session.id,
            {
                "passed_count": evidence.passed_count,
                "total_count": evidence.total_count,
                "hint_count": len(evidence.hint_levels),
            },
        )
    evidence_response = EvidenceResponse.model_validate(evidence, from_attributes=True)
    return CompletionResponse(session=session_response(session), evidence=evidence_response)


@api_router.get("/sessions/{session_id}/evidence", response_model=EvidenceResponse, tags=["evidence"])
def get_evidence(
    session_id: str,
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    session = container.repo.get_session(session_id)
    if not session:
        raise DomainError("session_not_found", "Không tìm thấy phiên học.", 404)
    is_owner = user.id == session.user_id
    if not is_owner:
        _require_teacher_read_access(session, user, container, "evidence")
    evidence = container.repo.get_evidence(session_id)
    if not evidence:
        raise DomainError("evidence_not_found", "Phiên học chưa có evidence.", 404)
    _track_event(container, user, "evidence_viewed", session.id, {"viewer_role": user.role.value})
    if not is_owner:
        # Instructor review has to be useful without exposing a learner's raw code.
        return EvidenceResponse(
            id=evidence.id,
            session_id=evidence.session_id,
            lesson_slug=evidence.lesson_slug,
            before_code="[Mã bài làm được ẩn trong chế độ giảng viên]",
            after_code="[Mã bài làm được ẩn trong chế độ giảng viên]",
            passed_count=evidence.passed_count,
            total_count=evidence.total_count,
            hint_levels=evidence.hint_levels,
            selected_terms=evidence.selected_terms,
            completed_at=evidence.completed_at,
        )
    return EvidenceResponse.model_validate(evidence, from_attributes=True)


@api_router.get(
    "/instructor/sessions",
    response_model=TeacherSessionListResponse,
    tags=["evidence"],
)
def list_instructor_sessions(
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    if user.role != Role.INSTRUCTOR:
        _audit_access_denied(container, user, None, "instructor_sessions", "instructor_required")
        raise DomainError("instructor_required", "Chỉ giảng viên mới có thể xem danh sách này.", 403)

    visible: list[TeacherSessionSummaryResponse] = []
    for session in container.repo.list_sessions():
        learner_consent = container.repo.get_user_consent(
            session.user_id, ConsentPurpose.TEACHER_VISIBILITY
        )
        try:
            require_instructor_access(session, user, learner_consent)
        except DomainError:
            continue
        visible.append(_teacher_session_summary(session, container))
    return TeacherSessionListResponse(sessions=visible)


@api_router.get(
    "/instructor/sessions/{session_id}/summary",
    response_model=TeacherSessionSummaryResponse,
    tags=["evidence"],
)
def get_instructor_session_summary(
    session_id: str,
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    if user.role != Role.INSTRUCTOR:
        _audit_access_denied(container, user, session_id, "instructor_summary", "instructor_required")
        raise DomainError("instructor_required", "Chỉ giảng viên mới có thể xem bản tóm tắt này.", 403)
    session = container.repo.get_session(session_id)
    if not session:
        raise DomainError("session_not_found", "Không tìm thấy phiên học.", 404)
    _require_teacher_read_access(session, user, container, "evidence")
    _track_event(container, user, "teacher_summary_viewed", session.id, {"read_only": True})
    return _teacher_session_summary(session, container)


@api_router.get("/analytics/events", response_model=AnalyticsEventListResponse, tags=["analytics"])
def list_analytics_events(
    session_id: str | None = Query(default=None),
    event_name: str | None = Query(default=None),
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    if user.role != Role.CONTENT_ADMIN:
        _audit_access_denied(container, user, session_id, "analytics_events", "admin_required")
        raise DomainError("admin_required", "Chỉ content admin mới có thể xem analytics event.", 403)
    events = container.repo.list_analytics_events(session_id=session_id, event_name=event_name)
    return AnalyticsEventListResponse(
        events=[AnalyticsEventResponse.model_validate(event, from_attributes=True) for event in events],
        total=len(events),
    )


@api_router.delete("/me/data", response_model=DeletionRequestResponse, tags=["privacy"])
def request_data_deletion(
    user: User = Depends(current_user),
    container: Container = Depends(get_container),
):
    request_id = container.repo.create_deletion_request(user.id)
    return DeletionRequestResponse(request_id=request_id)
