from ..domain.models import LearningSession, Lesson, Submission
from ..schemas import (
    ConsentResponse,
    LearningSessionResponse,
    LessonResponse,
    LessonStepResponse,
    SourceResponse,
    SubmissionResponse,
    TestResultResponse,
)


def lesson_response(lesson: Lesson) -> LessonResponse:
    return LessonResponse(
        slug=lesson.slug,
        version=lesson.version,
        title=lesson.title,
        objective=lesson.objective,
        source=SourceResponse(
            id=lesson.source.id,
            version_label=lesson.source.version_label,
            title=lesson.source.title,
            url=lesson.source.url,
            checksum=lesson.source.checksum,
            retrieved_at=lesson.source.retrieved_at,
            excerpt=lesson.source.excerpt,
        ),
        steps=[
            LessonStepResponse(
                sequence=step.sequence,
                key=step.key,
                title=step.title,
                objective=step.objective,
            )
            for step in lesson.steps
        ],
    )


def session_response(session: LearningSession) -> LearningSessionResponse:
    return LearningSessionResponse(
        id=session.id,
        user_id=session.user_id,
        lesson_slug=session.lesson_slug,
        lesson_version=session.lesson_version,
        status=session.status,
        current_step=session.current_step,
        version=session.version,
        selected_terms=session.selected_terms,
        concept_score=session.concept_score,
        concept_passed=session.concept_passed,
        submission_ids=session.submission_ids,
        hint_levels=session.hint_levels,
        consents=[
            ConsentResponse(
                purpose=str(consent.purpose),
                granted=consent.granted,
                policy_version=consent.policy_version,
                granted_at=consent.granted_at,
            )
            for consent in session.consents.values()
        ],
        completed_at=session.completed_at,
    )


def submission_response(submission: Submission) -> SubmissionResponse:
    return SubmissionResponse(
        id=submission.id,
        session_id=submission.session_id,
        status=submission.status,
        passed_count=submission.passed_count,
        total_count=submission.total_count,
        results=[TestResultResponse(**result) for result in submission.results],
        idempotency_key=submission.idempotency_key,
        created_at=submission.created_at,
        completed_at=submission.completed_at,
    )
