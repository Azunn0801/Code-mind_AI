from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.demo_auth import DemoTokenExpired, issue_demo_token, verify_demo_token
from app.main import app, create_app

client = TestClient(app)


def auth(user_id: str = "student_demo") -> dict[str, str]:
    settings = get_settings()
    token = issue_demo_token(
        user_id,
        settings.demo_token_secret,
        settings.demo_token_ttl_seconds,
    )
    return {"Authorization": f"Bearer {token}"}


def start_session(teacher_visibility: bool = True) -> tuple[str, dict[str, str]]:
    response = client.post(
        "/v1/learning-sessions",
        headers=auth(),
        json={
            "lesson_slug": "deque",
            "integrity_consent": True,
            "teacher_visibility": teacher_visibility,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"], auth()


def passing_code() -> str:
    return """
from collections import deque
history = deque(maxlen=3)
def visit(page):
    if not page:
        return list(history)
    history.append(page)
    return list(history)
history.append(1)
recent = list(history)
"""


def test_health_and_source_version_are_available():
    assert client.get("/health/live").json()["status"] == "ok"
    lesson = client.get("/v1/lessons/deque")
    assert lesson.status_code == 200
    assert lesson.json()["source"]["version_label"] == "Python 3.12"
    assert len(lesson.json()["steps"]) == 6


def test_demo_session_issues_short_lived_signed_token():
    response = client.post(
        "/v1/demo/session",
        json={"email": "student.demo@codemind.local", "role": "student"},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["expires_in"] == get_settings().demo_token_ttl_seconds
    assert payload["access_token"].startswith("demo.")

    issued_at = datetime(2026, 8, 9, tzinfo=UTC)
    token = issue_demo_token("student_demo", "test-secret", 60, now=issued_at)
    assert verify_demo_token(token, "test-secret", now=issued_at + timedelta(seconds=59)) == "student_demo"
    try:
        verify_demo_token(token, "test-secret", now=issued_at + timedelta(seconds=60))
    except DemoTokenExpired:
        pass
    else:
        raise AssertionError("Expired demo token must be rejected")


def test_consent_and_optimistic_progress():
    denied = client.post(
        "/v1/learning-sessions",
        headers=auth(),
        json={"lesson_slug": "deque", "integrity_consent": False},
    )
    assert denied.status_code == 403

    session_id, headers = start_session()
    current = client.get(f"/v1/learning-sessions/{session_id}", headers=headers).json()
    moved = client.patch(
        f"/v1/learning-sessions/{session_id}/progress",
        headers=headers,
        json={"current_step": 2, "expected_version": current["version"]},
    )
    assert moved.status_code == 200
    conflict = client.patch(
        f"/v1/learning-sessions/{session_id}/progress",
        headers=headers,
        json={"current_step": 3, "expected_version": current["version"]},
    )
    assert conflict.status_code == 409

    revoked = client.patch(
        "/v1/me/consents/teacher_visibility",
        headers=headers,
        json={"granted": False, "policy_version": "consent-v1", "expected_version": 0},
    )
    assert revoked.status_code == 200
    assert revoked.json()["granted"] is False
    assert revoked.json()["version"] == 1
    assert client.get(
        f"/v1/instructor/sessions/{session_id}/summary", headers=auth("instructor_demo")
    ).status_code == 403
    restored_consent = client.patch(
        "/v1/me/consents/teacher_visibility",
        headers=headers,
        json={"granted": True, "policy_version": "consent-v1", "expected_version": 1},
    )
    assert restored_consent.status_code == 200
    assert restored_consent.json()["version"] == 2


def test_happy_path_hint_ladder_idempotency_and_evidence():
    session_id, headers = start_session(teacher_visibility=True)
    invalid_terms = client.post(
        f"/v1/sessions/{session_id}/terms",
        headers=headers,
        json={"terms": ["does-not-appear-in-source"]},
    )
    assert invalid_terms.status_code == 422
    terms = client.post(
        f"/v1/sessions/{session_id}/terms",
        headers=headers,
        json={"terms": ["deque", "maxlen"]},
    )
    assert terms.status_code == 201
    concept = client.post(
        f"/v1/sessions/{session_id}/concept-answers",
        headers=headers,
        json={
            "pairs": [
                {"from_term": "deque", "to_term": "append", "relationship": "thêm phần tử"},
                {"from_term": "deque", "to_term": "maxlen", "relationship": "giới hạn số phần tử"},
            ]
        },
    )
    assert concept.status_code == 200
    assert concept.json()["passed"] is True

    interaction = client.post(
        f"/v1/sessions/{session_id}/ai-interactions",
        headers=headers,
        json={"question": "Mình chưa hiểu vì sao chỉ giữ lại ba phần tử."},
    )
    assert interaction.status_code == 200
    interaction_id = interaction.json()["id"]
    assert interaction.json()["refused_complete_answer"] is True
    assert client.post(
        f"/v1/ai-interactions/{interaction_id}/hints/2/open", headers=headers
    ).status_code == 409
    for level in (1, 2, 3):
        assert client.post(
            f"/v1/ai-interactions/{interaction_id}/hints/{level}/open", headers=headers
        ).status_code == 200

    missing_key = client.post(
        f"/v1/sessions/{session_id}/submissions",
        headers=headers,
        json={"code": "from collections import deque"},
    )
    assert missing_key.status_code == 422
    first = client.post(
        f"/v1/sessions/{session_id}/submissions",
        headers={**headers, "Idempotency-Key": "demo-final"},
        json={"code": "from collections import deque\nhistory = deque(maxlen=3)"},
    )
    assert first.status_code == 202
    assert first.json()["passed_count"] < first.json()["total_count"]
    final = client.post(
        f"/v1/sessions/{session_id}/submissions",
        headers={**headers, "Idempotency-Key": "demo-final-pass"},
        json={"code": passing_code()},
    )
    assert final.status_code == 202
    assert final.json()["passed_count"] == final.json()["total_count"]
    replay = client.post(
        f"/v1/sessions/{session_id}/submissions",
        headers={**headers, "Idempotency-Key": "demo-final-pass"},
        json={"code": "different code is ignored for the same key"},
    )
    assert replay.status_code == 202
    assert replay.json()["id"] == final.json()["id"]

    completed = client.post(f"/v1/sessions/{session_id}/complete", headers=headers)
    assert completed.status_code == 200, completed.text
    assert completed.json()["session"]["status"] == "completed"
    assert completed.json()["evidence"]["passed_count"] == 5

    student_evidence = client.get(f"/v1/sessions/{session_id}/evidence", headers=headers)
    instructor_evidence = client.get(
        f"/v1/sessions/{session_id}/evidence", headers=auth("instructor_demo")
    )
    assert student_evidence.status_code == 200
    assert instructor_evidence.status_code == 200
    assert instructor_evidence.json()["before_code"].startswith("[Mã bài làm được ẩn")


def test_instructor_cannot_read_session_without_teacher_consent():
    session_id, _ = start_session(teacher_visibility=False)
    response = client.get(
        f"/v1/sessions/{session_id}/evidence", headers=auth("instructor_demo")
    )
    assert response.status_code == 403


def test_ai_gateway_returns_citation_and_enforces_session_quota():
    session_id, headers = start_session(teacher_visibility=False)
    responses = [
        client.post(
            f"/v1/sessions/{session_id}/ai-interactions",
            headers=headers,
            json={"question": f"Câu hỏi số {index}"},
        )
        for index in range(1, 4)
    ]
    assert all(response.status_code == 200 for response in responses)
    first = responses[0].json()
    assert first["refused_complete_answer"] is True
    assert first["policy_decision"] == "allow_socratic"
    assert first["citation"]["url"].startswith("https://docs.python.org/")
    assert first["quota_remaining"] == 2

    exhausted = client.post(
        f"/v1/sessions/{session_id}/ai-interactions",
        headers=headers,
        json={"question": "Câu hỏi vượt quota"},
    )
    assert exhausted.status_code == 429
    assert exhausted.json()["code"] == "ai_quota_exceeded"
    assert exhausted.json()["details"] == {"limit": 3, "used": 3, "remaining": 0}

    events = client.get(
        "/v1/analytics/events",
        headers=auth("admin_demo"),
        params={"session_id": session_id, "event_name": "ai_interaction_created"},
    )
    assert events.status_code == 200
    assert events.json()["total"] == 3
    assert all("question" not in event["properties"] for event in events.json()["events"])
    assert client.get("/v1/analytics/events", headers=headers).status_code == 403


def test_teacher_summary_is_read_only_and_consent_scoped():
    visible_session, _ = start_session(teacher_visibility=True)
    summary = client.get(
        f"/v1/instructor/sessions/{visible_session}/summary",
        headers=auth("instructor_demo"),
    )
    assert summary.status_code == 200
    assert summary.json()["teacher_visibility"] is True
    assert summary.json()["evidence_available"] is False
    assert "before_code" not in summary.json()
    listed = client.get("/v1/instructor/sessions", headers=auth("instructor_demo"))
    assert listed.status_code == 200
    assert visible_session in {item["session_id"] for item in listed.json()["sessions"]}
    assert (
        client.get(
            f"/v1/instructor/sessions/{visible_session}/summary",
            headers=auth(),
        ).status_code
        == 403
    )

    private_session, _ = start_session(teacher_visibility=False)
    denied = client.get(
        f"/v1/instructor/sessions/{private_session}/summary",
        headers=auth("instructor_demo"),
    )
    assert denied.status_code == 403


def test_no_ai_vertical_slice_survives_refresh():
    session_id, headers = start_session(teacher_visibility=False)
    assert client.post(
        f"/v1/sessions/{session_id}/terms",
        headers=headers,
        json={"terms": ["maxlen"]},
    ).status_code == 201
    concept = client.post(
        f"/v1/sessions/{session_id}/concept-answers",
        headers=headers,
        json={
            "pairs": [
                {"from_term": "deque", "to_term": "append", "relationship": "thêm phần tử"},
                {"from_term": "deque", "to_term": "maxlen", "relationship": "giới hạn số phần tử"},
            ]
        },
    )
    assert concept.json()["passed"] is True
    draft = client.post(
        f"/v1/sessions/{session_id}/submissions",
        headers={**headers, "Idempotency-Key": "no-ai-draft"},
        json={"code": "from collections import deque\nhistory = deque(maxlen=3)\nhistory.append(page)"},
    )
    assert draft.json()["passed_count"] == 4
    fixed = client.post(
        f"/v1/sessions/{session_id}/submissions",
        headers={**headers, "Idempotency-Key": "no-ai-fixed"},
        json={"code": passing_code()},
    )
    assert fixed.json()["passed_count"] == 5
    completed = client.post(f"/v1/sessions/{session_id}/complete", headers=headers)
    assert completed.status_code == 200
    restored = client.get(f"/v1/learning-sessions/{session_id}", headers=headers)
    assert restored.status_code == 200
    assert restored.json()["status"] == "completed"
    assert restored.json()["current_step"] == 6
def test_file_repository_survives_app_restart(tmp_path, monkeypatch):
    state_file = tmp_path / "codemind-state.json"
    monkeypatch.setenv("REPOSITORY_MODE", "file")
    monkeypatch.setenv("STATE_FILE_PATH", str(state_file))
    get_settings.cache_clear()

    first_app = create_app()
    with TestClient(first_app) as first_client:
        created = first_client.post(
            "/v1/learning-sessions",
            headers=auth(),
            json={
                "lesson_slug": "deque",
                "integrity_consent": True,
                "teacher_visibility": False,
            },
        )
        assert created.status_code == 201, created.text
        session_id = created.json()["id"]
        moved = first_client.patch(
            f"/v1/learning-sessions/{session_id}/progress",
            headers=auth(),
            json={"current_step": 2, "expected_version": 1},
        )
        assert moved.status_code == 200, moved.text

    get_settings.cache_clear()
    second_app = create_app()
    with TestClient(second_app) as second_client:
        restored = second_client.get(
            f"/v1/learning-sessions/{session_id}",
            headers=auth(),
        )
        restored_events = second_client.get(
            "/v1/analytics/events",
            headers=auth("admin_demo"),
            params={"session_id": session_id, "event_name": "learning_session_started"},
        )
    get_settings.cache_clear()
    assert restored.status_code == 200, restored.text
    assert restored.json()["current_step"] == 2
    assert restored.json()["version"] == 2
    assert restored_events.status_code == 200, restored_events.text
    assert restored_events.json()["total"] == 1
