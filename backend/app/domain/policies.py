from ..core.errors import DomainError
from .models import ConsentPurpose, LearningSession, Lesson, Role, User, UserConsent


def require_session_owner(session: LearningSession, user: User) -> None:
    if session.user_id != user.id:
        raise DomainError("session_forbidden", "Bạn chỉ có thể thao tác trên phiên học của mình.", 403)


def require_integrity_consent(
    session: LearningSession, user_consent: UserConsent | None = None
) -> None:
    consent = session.consents.get("academic_integrity")
    if not consent or not consent.granted:
        raise DomainError("consent_required", "Bạn cần đồng ý cam kết học tập trước khi bắt đầu.", 403)
    if user_consent is not None and not user_consent.granted:
        raise DomainError("consent_revoked", "Consent has been revoked for this account.", 403)


def require_instructor_access(
    session: LearningSession,
    viewer: User,
    user_consent: UserConsent | None = None,
) -> None:
    if viewer.role != Role.INSTRUCTOR:
        require_session_owner(session, viewer)
        return
    visibility = session.consents.get("teacher_visibility")
    if (
        viewer.organization_id != session.organization_id
        or not visibility
        or not visibility.granted
        or (
            user_consent is not None
            and user_consent.purpose == ConsentPurpose.TEACHER_VISIBILITY
            and not user_consent.granted
        )
    ):
        raise DomainError("evidence_forbidden", "Phiên học này chưa được phép chia sẻ cho giảng viên.", 403)


def validate_progress_step(session: LearningSession, step: int) -> None:
    if step < 1 or step > 6:
        raise DomainError("invalid_step", "Bước học phải nằm trong khoảng 1 đến 6.", 422)
    if step > session.current_step + 1:
        raise DomainError("step_locked", "Hãy hoàn thành bước hiện tại trước khi đi tiếp.", 409)


def validate_completion(session: LearningSession, lesson: Lesson) -> None:
    if not session.selected_terms:
        raise DomainError("terms_required", "Hãy chọn ít nhất một thuật ngữ từ tài liệu.", 409)
    if not session.concept_passed:
        raise DomainError("concept_required", "Hãy hoàn thành phần nối khái niệm trước.", 409)
    if not session.submission_ids:
        raise DomainError("submission_required", "Hãy gửi mã và chạy bài kiểm tra trước.", 409)
