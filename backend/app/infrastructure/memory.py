from copy import deepcopy
from threading import RLock
from uuid import uuid4

from ..domain.models import (
    AIInteraction,
    AnalyticsEvent,
    ConsentPurpose,
    LearningEvidence,
    LearningSession,
    Lesson,
    Role,
    Submission,
    User,
    UserConsent,
)


class InMemoryRepository:
    """Thread-safe local adapter; replace with a PostgreSQL adapter in production."""

    def __init__(self) -> None:
        self._lock = RLock()
        self.users: dict[str, User] = {}
        self.user_consents: dict[str, UserConsent] = {}
        self.lessons: dict[str, Lesson] = {}
        self.sessions: dict[str, LearningSession] = {}
        self.submissions: dict[str, Submission] = {}
        self.interactions: dict[str, AIInteraction] = {}
        self.evidence: dict[str, LearningEvidence] = {}
        self.analytics_events: dict[str, AnalyticsEvent] = {}
        self.deletion_requests: dict[str, str] = {}

    def get_user(self, user_id: str) -> User | None:
        with self._lock:
            return deepcopy(self.users.get(user_id))

    def find_user_by_email(self, email: str) -> User | None:
        with self._lock:
            return deepcopy(next((u for u in self.users.values() if u.email == email), None))

    def save_user(self, user: User) -> None:
        with self._lock:
            self.users[user.id] = deepcopy(user)

    def get_lesson(self, slug: str) -> Lesson | None:
        with self._lock:
            return deepcopy(self.lessons.get(slug))

    def save_lesson(self, lesson: Lesson) -> None:
        with self._lock:
            self.lessons[lesson.slug] = deepcopy(lesson)

    @staticmethod
    def _consent_key(user_id: str, purpose: ConsentPurpose) -> str:
        return f"{user_id}:{purpose.value}"

    def get_user_consent(self, user_id: str, purpose: ConsentPurpose) -> UserConsent | None:
        with self._lock:
            return deepcopy(self.user_consents.get(self._consent_key(user_id, purpose)))

    def save_user_consent(self, consent: UserConsent) -> None:
        with self._lock:
            self.user_consents[self._consent_key(consent.user_id, consent.purpose)] = deepcopy(consent)

    def get_session(self, session_id: str) -> LearningSession | None:
        with self._lock:
            return deepcopy(self.sessions.get(session_id))

    def save_session(self, session: LearningSession) -> None:
        with self._lock:
            self.sessions[session.id] = deepcopy(session)

    def list_sessions(self) -> list[LearningSession]:
        with self._lock:
            return deepcopy(list(self.sessions.values()))

    def get_submission(self, submission_id: str) -> Submission | None:
        with self._lock:
            return deepcopy(self.submissions.get(submission_id))

    def save_submission(self, submission: Submission) -> None:
        with self._lock:
            self.submissions[submission.id] = deepcopy(submission)

    def find_submission_by_key(self, session_id: str, idempotency_key: str) -> Submission | None:
        with self._lock:
            return deepcopy(
                next(
                    (
                        submission
                        for submission in self.submissions.values()
                        if submission.session_id == session_id
                        and submission.idempotency_key == idempotency_key
                    ),
                    None,
                )
            )

    def get_interaction(self, interaction_id: str) -> AIInteraction | None:
        with self._lock:
            return deepcopy(self.interactions.get(interaction_id))

    def save_interaction(self, interaction: AIInteraction) -> None:
        with self._lock:
            self.interactions[interaction.id] = deepcopy(interaction)

    def list_interactions(self, session_id: str) -> list[AIInteraction]:
        with self._lock:
            return [
                deepcopy(interaction)
                for interaction in self.interactions.values()
                if interaction.session_id == session_id
            ]

    def get_evidence(self, session_id: str) -> LearningEvidence | None:
        with self._lock:
            return deepcopy(self.evidence.get(session_id))

    def save_evidence(self, evidence: LearningEvidence) -> None:
        with self._lock:
            self.evidence[evidence.session_id] = deepcopy(evidence)

    def save_analytics_event(self, event: AnalyticsEvent) -> None:
        with self._lock:
            self.analytics_events[event.id] = deepcopy(event)

    def list_analytics_events(
        self,
        session_id: str | None = None,
        user_id: str | None = None,
        event_name: str | None = None,
    ) -> list[AnalyticsEvent]:
        with self._lock:
            events = [
                event
                for event in self.analytics_events.values()
                if (session_id is None or event.session_id == session_id)
                and (user_id is None or event.user_id == user_id)
                and (event_name is None or event.event_name == event_name)
            ]
            return deepcopy(sorted(events, key=lambda event: event.occurred_at))

    def create_deletion_request(self, user_id: str) -> str:
        with self._lock:
            request_id = f"del_{uuid4().hex[:12]}"
            self.deletion_requests[request_id] = user_id
            return request_id

    def check_ready(self) -> bool:
        """The in-process adapter has no external dependency to probe."""

        return True

    @classmethod
    def seeded(cls) -> "InMemoryRepository":
        from .seed import build_demo_lesson

        repo = cls()
        repo.save_user(User("student_demo", "student.demo@codemind.local", "Minh — người học", Role.STUDENT))
        repo.save_user(
            User("instructor_demo", "instructor.demo@codemind.local", "Lan — giảng viên", Role.INSTRUCTOR)
        )
        repo.save_user(User("admin_demo", "admin.demo@codemind.local", "An — quản trị", Role.CONTENT_ADMIN))
        repo.save_lesson(build_demo_lesson())
        return repo
