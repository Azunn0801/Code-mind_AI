# CodeMind MVP — Biên bản kiểm chứng local

**Ngày kiểm chứng:** 09/08/2026  
**Phạm vi:** P0 vertical slice tại máy local; không phải biên bản nghiệm thu staging/production.

## Kết quả đã kiểm chứng

| Hạng mục | Kết quả | Bằng chứng tái lập |
|---|---|---|
| Backend lint | Pass | `backend/.venv/Scripts/python.exe -m ruff check app tests` |
| Backend compile | Pass | `backend/.venv/Scripts/python.exe -m compileall -q app tests` |
| Backend test | **12 passed** | `backend/.venv/Scripts/python.exe -m pytest` (có 1 Starlette deprecation warning sẵn có) |
| Hợp đồng API | **20 route bắt buộc** hợp lệ | `backend/.venv/Scripts/python.exe scripts/check_contract.py` |
| HTTP smoke backend | `/health/live=ok`, `/health/ready=ok` | Uvicorn local tạm thời tại `127.0.0.1:8876`, profile `REPOSITORY_MODE=memory`, sau đó đã dừng tiến trình |
| Frontend lint | Pass | `frontend/npm.cmd run lint` |
| Frontend build | Pass: 33 modules, 2.02s | `frontend/npm.cmd run build` tại thư mục MVP gốc sau khi canonical hóa Vite root |
| Docker Compose syntax | Pass **chỉ với** biến môi trường tạm thời; cấu hình cố ý từ chối khi thiếu `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | `docker compose config --quiet` (không chạy container) |
| PDF proposal | Đã tạo và kiểm tra render trực quan; 22 trang vật lý, dưới 60 trang và 30 MB | `deliverables/[KHOINGUYEN - VONG 3] - CodeMind.pdf` |
| Data specification | Mở lại được; 12 sheet, 11 table, 8 công thức được giữ | `docs/CodeMind_MVP_Data_Spec.xlsx` và status log |
| Git diff whitespace | Pass | `git diff --check` |
| Git tracking | Chưa sẵn sàng làm bằng chứng CI remote | `git status --short` còn có các thư mục/file MVP untracked, gồm `.github/`, `backend/`, README và hồ sơ mới; chủ repo cần review, track, commit và push |

## Phạm vi chức năng mà kết quả trên bao phủ

- Người học: chọn tài khoản demo → consent → đọc nguồn chính thức → kiểm tra concept → nộp mã qua runner mô phỏng → AI Socratic/hint → evidence.
- Instructor: xem summary read-only khi learner đã bật `teacher_visibility`; evidence được redacted, không trả raw code.
- Content admin: xem analytics event đã redacted.
- Bảo vệ P0 đã test: token demo HMAC có hạn dùng, RBAC, consent grant/revoke, term-source validation và idempotency submission.
- Persistence P0: `PersistentRepository` local và `PostgresRepository` adapter/migration/readiness có test local. Đây không phải xác nhận Compose hay PostgreSQL staging đã chạy.

## Không được suy diễn từ biên bản này

Các mục sau **chưa có bằng chứng hoàn thành** và vẫn là gate trước khi tuyên bố sẵn sàng nộp MVP công khai:

1. URL HTTPS public, tài khoản demo production và thử nghiệm cửa sổ ẩn danh.
2. Compose/staging với PostgreSQL thực, backup/restore thực tế và rollback release.
3. Runner cô lập, AI provider/RAG/MOSS/GitHub OAuth thực; P0 hiện dùng `SimulatedDequeRunner` và canned Socratic gateway.
4. Browser E2E, security scan, load/performance test, monitoring và DR drill.
5. Pilot 30–50 người học và số liệu D7; không có số liệu nào được bịa trong báo cáo.
6. Dashboard Student/Teacher/Admin đầy đủ, VARK/gamification/community/ads/payment/Campus: chỉ là V2 roadmap hoặc Figma prototype, không phải P0 đã phát hành.

File `.env` không được tạo thay cho chủ dự án và không có container nào được khởi chạy trong lần kiểm chứng này. Việc Compose từ chối thiếu ba biến Postgres là một guardrail mong muốn, không phải bằng chứng rằng môi trường staging đã sẵn sàng.

## Điều kiện bàn giao chính thức

Chỉ đổi trạng thái sang “public release candidate” sau khi điền đủ URL, account theo role, commit/tag/image digest, kết quả `/health/live` và `/health/ready`, biên bản smoke ẩn danh, cùng các bằng chứng staging tương ứng trong [Experience Guide](CodeMind_MVP_Experience_Guide.md) và [Deployment Runbook](CodeMind_Deployment_Runbook.md).

Tên file hiện là `[KHOINGUYEN - VONG 3] - CodeMind.pdf` theo tên sản phẩm. Nếu tên đội khác CodeMind, chủ dự án phải thay phần sau dấu gạch bằng **tên đội chính thức** theo cú pháp BTC trước khi nộp; các placeholder tên đội/mentor/thành viên trên bìa cũng phải được điền từ dữ liệu thật.

Video và slide được chủ dự án loại khỏi phạm vi triển khai hiện tại, nhưng vẫn là yêu cầu chính thức của Ban Tổ chức; biên bản này không thay thế hai hạng mục đó.
