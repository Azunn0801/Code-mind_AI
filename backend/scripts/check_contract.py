from app.main import app

required = {
    ("GET", "/health/live"),
    ("GET", "/health/ready"),
    ("POST", "/v1/demo/session"),
    ("PATCH", "/v1/me/consents/{purpose}"),
    ("GET", "/v1/lessons/{slug}"),
    ("POST", "/v1/learning-sessions"),
    ("GET", "/v1/learning-sessions/{session_id}"),
    ("PATCH", "/v1/learning-sessions/{session_id}/progress"),
    ("POST", "/v1/sessions/{session_id}/terms"),
    ("POST", "/v1/sessions/{session_id}/concept-answers"),
    ("POST", "/v1/sessions/{session_id}/submissions"),
    ("GET", "/v1/submissions/{submission_id}"),
    ("POST", "/v1/sessions/{session_id}/ai-interactions"),
    ("POST", "/v1/ai-interactions/{interaction_id}/hints/{level}/open"),
    ("POST", "/v1/sessions/{session_id}/complete"),
    ("GET", "/v1/sessions/{session_id}/evidence"),
    ("GET", "/v1/instructor/sessions/{session_id}/summary"),
    ("GET", "/v1/instructor/sessions"),
    ("GET", "/v1/analytics/events"),
    ("DELETE", "/v1/me/data"),
}

actual = {
    (method.upper(), path)
    for path, operations in app.openapi()["paths"].items()
    for method in operations
}
missing = sorted(required - actual)
if missing:
    raise SystemExit(f"Missing API contract routes: {missing}")

print(f"API contract OK: {len(required)} required routes")
