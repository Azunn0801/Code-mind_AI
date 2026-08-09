"""Policy-aware AI gateway seam used by the local MVP.

The default implementation is deterministic and offline so a demo never depends
on provider credentials.  A hosted provider can implement the same protocol in
Stage 4 without changing the learning routes or response contract.
"""

from dataclasses import dataclass
from time import perf_counter
from typing import Protocol

from ..domain.models import Lesson


@dataclass(frozen=True, slots=True)
class AIGatewayResult:
    message: str
    next_action: str
    refused_complete_answer: bool
    policy_version: str
    model_id: str
    policy_decision: str
    citation_source_id: str
    citation_url: str
    citation_title: str
    citation_version_label: str
    quota_cost: int
    latency_ms: int


class AIGateway(Protocol):
    def answer(self, question: str, lesson: Lesson) -> AIGatewayResult: ...


class CannedSocraticGateway:
    """Offline fallback that preserves the production gateway contract."""

    mode = "canned"
    policy_version = "socratic-v2"
    model_id = "canned-socratic-v1"

    def check_ready(self) -> bool:
        return True

    def answer(self, question: str, lesson: Lesson) -> AIGatewayResult:
        started = perf_counter()
        source = lesson.source
        normalized = question.strip()
        latency_ms = max(0, round((perf_counter() - started) * 1000))
        return AIGatewayResult(
            message=(
                "Mình chưa đưa đáp án hoàn chỉnh. Hãy mở từng gợi ý để tự tìm ra lỗi, "
                f"bắt đầu bằng câu hỏi: “{normalized[:160]}”."
            ),
            next_action="open_hint_1",
            refused_complete_answer=True,
            policy_version=self.policy_version,
            model_id=self.model_id,
            policy_decision="allow_socratic",
            citation_source_id=source.id,
            citation_url=source.url,
            citation_title=source.title,
            citation_version_label=source.version_label,
            quota_cost=1,
            latency_ms=latency_ms,
        )
