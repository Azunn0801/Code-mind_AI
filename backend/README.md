# CodeMind backend — P0 architecture

Đây là backend scaffold cho vertical slice P0 của vòng 3: một lesson `deque`,
consent, source version, concept check, code submission, hint ladder, evidence
và instructor read-only.

## Kiến trúc

```text
HTTP (FastAPI routes)
        ↓
Application policies / use-case orchestration
        ↓
Domain models + ports (Repository, CodeRunner, AI Gateway)
        ↓
Infrastructure adapters (in-memory/file/PostgreSQL P0, simulated runner/canned AI)
```

`PersistentRepository` giúp profile local giữ session/progress sau khi backend khởi động
lại. `PostgresRepository` lưu aggregate snapshot P0 trong bảng migration
`application_state`; `InMemoryRepository` vẫn dùng cho test. Đây là persistence
P0 cho một API replica, không phải claim multi-writer/production-scale.

## Chạy local

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Nếu chạy bằng **CMD** thay dòng kích hoạt môi trường bằng:

```bat
cd /d "D:\4Study\SideProject\Khoi nguyen 2026\Round 3\MVP\backend"
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Trên máy Windows của đội, cổng `8000` có thể nằm trong dải cổng bị hệ điều hành đặt trước. Dùng `8765` để tránh `WinError 10013`. Lệnh mặc định không dùng `--reload` để tránh process phụ của Uvicorn; chỉ thêm `--reload` sau khi bản chạy thường đã hoạt động.

Mở Swagger tại <http://127.0.0.1:8765/docs>.

Nếu gặp `ModuleNotFoundError: No module named 'fastapi'`, virtual environment
chưa được cài dependency. Chạy lại:

```bat
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Smoke test:

```powershell
pytest
```

## Docker PostgreSQL profile

Compose configuration is designed for the durable P0 runtime: it starts PostgreSQL,
runs the idempotent migration service, and then starts the API in `REPOSITORY_MODE=postgres`.
The database is intentionally not published to the host. Cấu hình đã qua kiểm tra
interpolation với biến tạm thời, nhưng chưa có bằng chứng chạy Compose/staging hoặc
backup/restore thực tế; không mô tả nó như runtime đã phát hành.

```powershell
cd backend
Copy-Item .env.example .env
# Edit POSTGRES_PASSWORD in .env before the first shared run.
docker compose up --build
```

Sau khi đội tự chạy Compose thành công, mở `http://127.0.0.1:8765/health/ready`. A successful response contains
`database: up`; a database outage returns HTTP 503 without exposing connection
details. The current `application_state` adapter persists the P0 aggregate in
PostgreSQL and is bounded to one API replica. It is not a claim of multi-writer
or production-scale persistence.

## Demo token

`POST /v1/demo/session` tạo token demo ký HMAC, có hạn dùng (mặc định 1 giờ).
Frontend `/#/demo/access` lấy token này tự động. Khi kiểm thử API, gửi token qua
`Authorization: Bearer <access_token>`; header `X-Demo-User` chỉ được chấp nhận
ngoài production để hỗ trợ local test. Đây vẫn chỉ là adapter demo; production phải thay bằng OIDC/JWT thật.

## P0 endpoints

- `GET /health/live`, `GET /health/ready`
- `POST /v1/demo/session`
- `PATCH /v1/me/consents/{purpose}`
- `GET /v1/lessons/{slug}`
- `POST /v1/learning-sessions`, `GET/PATCH /v1/learning-sessions/{id}`
- `POST /v1/sessions/{id}/terms`
- `POST /v1/sessions/{id}/concept-answers`
- `POST /v1/sessions/{id}/submissions`, `GET /v1/submissions/{id}`
- `POST /v1/sessions/{id}/ai-interactions`
- `POST /v1/ai-interactions/{id}/hints/{level}/open`
- `GET /v1/instructor/sessions`, `GET /v1/instructor/sessions/{id}/summary`
- `GET /v1/analytics/events` (content admin)
- `POST /v1/sessions/{id}/complete`
- `GET /v1/sessions/{id}/evidence`
- `DELETE /v1/me/data`

## Giai đoạn tiếp theo

1. Chuẩn hóa snapshot P0 thành các bảng domain ở PostgreSQL và hỗ trợ migration/backup/restore cho nhiều replica.
2. Đưa code runner ra worker cô lập, chặn network và giới hạn CPU/RAM/output.
3. Thay provider canned bằng adapter AI thật có timeout/retry, cost guard và secret management.
4. Chạy Compose/staging, integration/E2E, security/load/backup và deploy HTTPS.

## Tiến độ thực tế — 09/08/2026

Backend đã hoàn tất **Stage 3 local — AI policy, analytics và teacher read-only contract**:

- `[x]` FastAPI routes, domain policies, in-memory adapter, seed lesson và migration đầu.
- `[x]` Luồng local auth demo → consent → source → concept → submission → progress/evidence.
- `[x]` Ruff, compile và API contract checker; gate local hiện có **12 test pass** và 20 route bắt buộc.
- `[x]` Local profile dùng snapshot JSON và đã có test đọc lại progress sau restart.
- `[~]` PostgreSQL P0 adapter/migration/readiness đã có test local; Compose/staging/restore thực tế chưa được xác nhận.
- `[x]` AI gateway contract local có canned fallback, policy decision, citation, quota 3 lượt/phiên và latency/cost metadata.
- `[x]` Analytics event redacted, teacher summary kiểm tra RBAC + consent; test xác nhận event tồn tại sau restart.
- `[~]` Runner vẫn simulated; provider AI thật, multi-replica PostgreSQL, production observability và staging chưa hoàn tất.
- `[ ]` Chưa có staging URL, E2E/security/load/backup-restore hoặc pilot production.

Chi tiết và nhật ký theo ngày xem tại [`docs/CodeMind_Progress_Log.md`](../docs/CodeMind_Progress_Log.md).
## Nhật ký lịch sử — Stage 2 local (đã được thay thế bởi gate hiện hành)

- `[x]` Local profile mặc định dùng `PersistentRepository` và snapshot nguyên tử tại `.data/codemind_state.json`.
- `[x]` Test `test_file_repository_survives_app_restart` dựng app lần một, lưu progress, dựng app lần hai và đọc lại session thành công.
- `[x]` Bản ghi tại thời điểm Stage 2: Ruff pass, compile pass, contract **16 route**, pytest **6 passed**, frontend lint/build pass. Đây chỉ là lịch sử; gate hiện hành ở phần trên là **20 route/12 test**.
- `[~]` PostgreSQL runtime, runner cô lập, AI gateway production và public staging vẫn thuộc các stage sau.

Để chạy profile bền vững local, giữ `REPOSITORY_MODE=file` và `STATE_FILE_PATH=.data/codemind_state.json` (đã có trong `.env.example`). Test tự chuyển sang in-memory bằng `tests/conftest.py`.

## Stage 3 local — policy và audit contract

- `POST /v1/sessions/{id}/ai-interactions` dùng `AIGateway`; local mặc định là canned/offline nhưng response luôn có `policy_decision`, `policy_version`, `model_id`, citation, `quota_remaining`, `quota_cost` và `latency_ms`.
- Quota local là `AI_MAX_INTERACTIONS_PER_SESSION=3`. Khi hết quota, API trả `429 ai_quota_exceeded` và không tạo interaction mới.
- Analytics chỉ lưu số liệu cần cho product/audit, không lưu raw code hoặc full question trong `properties`. `content_admin` mới đọc được danh sách event.
- Instructor summary chỉ đọc, yêu cầu đúng role + organization + `teacher_visibility=true`, và không trả `before_code`/`after_code`.
