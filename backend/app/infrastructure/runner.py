from dataclasses import dataclass


@dataclass(slots=True)
class RunResult:
    passed_count: int
    total_count: int
    results: list[dict[str, object]]


class CodeRunner:
    def run(self, code: str) -> RunResult:
        raise NotImplementedError


class SimulatedDequeRunner(CodeRunner):
    """Deterministic local adapter; never executes untrusted student code."""

    mode = "simulated"

    def check_ready(self) -> bool:
        return True

    def run(self, code: str) -> RunResult:
        normalized = code.lower()
        rejects_empty = "if not page" in normalized or "if page == ''" in normalized or 'if page == ""' in normalized
        checks = [
            ("imports_deque", "from collections import deque" in normalized or "deque(" in normalized),
            ("sets_maxlen", "maxlen=3" in normalized.replace(" ", "")),
            ("appends_value", ".append(" in normalized),
            ("keeps_recent_values", "history" in normalized or "recent" in normalized or "deque" in normalized),
            ("guards_empty_input", rejects_empty),
        ]
        results = [
            {
                "name": name,
                "passed": passed,
                "message": "Đạt" if passed else "Hãy xem lại phần này trong mã.",
            }
            for name, passed in checks
        ]
        return RunResult(sum(1 for _, passed in checks if passed), len(checks), results)
