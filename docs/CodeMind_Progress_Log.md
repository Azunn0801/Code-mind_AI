# CodeMind MVP — Progress Log

**Cập nhật gần nhất:** 09/08/2026  
**Phạm vi:** CodeMind Round 3 MVP  
**Người ghi:** Codex audit theo repository và các gate local

## Snapshot

- **Stage hiện tại:** P0 local integration candidate; đang chuẩn bị các gate Compose/staging/public release. Frontend production build đã pass lại tại thư mục MVP gốc sau khi canonical hóa Vite root cho junction/D:, nhưng đây vẫn chỉ là bằng chứng local.
- **Mức sẵn sàng:** demo role access → six-step learning → AI hint → evidence chạy local; Instructor summary và Content admin analytics có UI read-only tối thiểu.
- **Đã nối:** frontend live flow gọi FastAPI qua Vite proxy; progress/evidence hiển thị, có localStorage restore; signed demo token, consent grant/revoke, idempotency và term validation đã có test local.
- **Giới hạn:** backend local dùng `PersistentRepository` hoặc `PostgresRepository` P0 adapter; runner là `SimulatedDequeRunner`, AI là canned gateway offline. Compose/staging PostgreSQL, runner cô lập/provider thật chưa có bằng chứng release.

## Audit các mốc trong Section 9

| Mốc | Trạng thái thực tế | Bằng chứng / khoảng trống |
|---|---|---|
| 22–24/07: scope, use case, data/API, repo/CI, migration | ✅ Hoàn tất repository/local | Scope freeze, data spec, migration SQL, contract checker, CI. |
| 25–30/07: vertical slice không AI | ⚠️ Hoàn tất local, chưa đạt staging DoD | Flow role demo → consent → source → concept → code 4/5 → 5/5 → evidence có API/client/test; có adapter PostgreSQL P0 test local nhưng chưa có Compose/public staging hoặc runner cô lập. |
| 31/07–03/08: AI, hint, evidence, teacher, analytics | ✅ Hoàn tất local | Gateway contract offline, policy/quota/citation metadata, redacted analytics, teacher summary RBAC/consent và test local đã pass; provider thật/analytics production còn pending. |
| 04–06/08: recovery, security/performance/E2E, backup | ⬜ Chưa hoàn tất | Chưa có bằng chứng test/staging. |
| 07/08: deploy và pilot | ⬜ Chưa bắt đầu | Chưa có URL public, production accounts hoặc pilot log. |
| 08–09/08: báo cáo chi tiết, video/slide, nộp | ⚠️ Một phần hoàn tất | PDF proposal đã render QA: 22 trang vật lý, ~185 KB; cấu trúc giữ giới hạn **≤60 trang nội dung** (không tính bìa/phụ lục) và **≤30 MB**. Còn team/mentor/member, URL public, account, checksum/biên nhận. Video/slide nằm ngoài phạm vi làm việc hiện tại theo chủ dự án nhưng vẫn là yêu cầu chính thức. |

## Gate đã kiểm chứng

### Lần chạy thành công gần nhất — Stage 3 local, 09/08/2026

- Backend Ruff: pass.
- Backend compile: pass.
- API contract: **20 required routes**.
- Backend pytest: **12 passed**.
- Frontend ESLint: pass.
- Frontend production build: pass (33 modules, 2.02s) tại thư mục MVP gốc; canonical Vite root đã loại lỗi asset path tuyệt đối khi làm việc qua junction. Live practice có AI coach/hint ladder ở local.
- HTTP smoke local: chạy Uvicorn tạm với `REPOSITORY_MODE=memory` tại cổng 8876; `/health/live=ok` và `/health/ready=ok`, sau đó đã dừng tiến trình. Chưa thay thế browser E2E.

### Bổ sung kiểm chứng Stage 3 — 09/08/2026

- Backend Ruff: pass; compile và API contract **20 route bắt buộc**: pass.
- Test quota/citation/policy AI: pass; lần hỏi thứ 4 trả `429 ai_quota_exceeded`.
- Test analytics: `content_admin` đọc được event redacted; student bị từ chối; event tồn tại sau restart snapshot.
- Test teacher summary: instructor đúng organization + consent đọc được summary read-only; student/phiên private bị từ chối.
- Frontend ESLint và production build: pass sau khi nối API client/context, role demo, AI step, recovery state và canonical Vite root.
- PDF proposal: render visual QA pass (cover, user flow, architecture diagram, ERD và phụ lục); 22 trang, khoảng 185 KB.
- Data specification workbook v1.1: archive/open validation pass, 12 sheets/11 tables/8 formulas giữ nguyên; status được đổi sang Local verified/Partial/Planned/Deferred/External.

## Việc còn lại để chuyển sang staging

| Owner đề xuất | Việc cần làm | Điều kiện đóng |
|---|---|---|
| Backend/Data | Chạy PostgreSQL qua Compose/Alembic thực, seed và kiểm thử restore | Session/progress tồn tại sau restart; migration chạy sạch và restore được ghi log. |
| Runner | Tách code execution thành worker/container, chặn network và giới hạn CPU/RAM/time/output | Có timeout, retry và test bảo mật độc lập. |
| AI/Backend | Thay canned provider bằng adapter AI thật, timeout/retry, cost guard và secret management | Provider staging có policy tests, fallback và budget được đo. |
| Frontend | Hoàn thiện loading/error/retry và xác nhận refresh với API thật | E2E happy path và recovery pass trên staging. |
| QA/DevOps | Security scan, performance 50 users, backup/restore, monitoring | Có log kết quả và ngưỡng P95/error rate. |
| Release | Deploy HTTPS, seed demo accounts, pilot 5–10 người | URL public mở được ở incognito và có pilot log. |

## Hồ sơ release và yêu cầu Round 3

- `[x]` Đã có hướng dẫn role/account, kịch bản P0 3 phút, checklist incognito và deployment runbook trong `docs/`; đây là tài liệu chuẩn bị, **không** là bằng chứng URL public hay account production.
- `[~]` Báo cáo chi tiết PDF theo Proposal Template: giới hạn mới **≤60 trang nội dung**, giữ **≤30 MB** từ đề gốc. File hiện render QA 22 trang vật lý/~185 KB; còn placeholder team/mentor/member, URL public và pilot data phải do đội chốt trước khi nộp.
- `[ ]` URL public HTTPS, ba account role, browser E2E, backup/restore rehearsal và pilot log vẫn chưa xác nhận.
- `[~]` Chủ dự án yêu cầu không làm slide/video trong scope hiện tại. Chúng vẫn là yêu cầu chính thức; không gắn nhãn toàn bộ bộ bài nộp “complete” chỉ dựa trên ngoại lệ này.

## Nhật ký lịch sử — Stage 2 local (đã được thay thế bởi gate hiện hành)

- `[x]` Bổ sung `PersistentRepository`: snapshot JSON có schema version, encode/decode domain dataclasses, ghi file tạm rồi replace nguyên tử.
- `[x]` Backend mặc định dùng `REPOSITORY_MODE=file`; test dùng in-memory qua `tests/conftest.py` để độc lập.
- `[x]` Test restart route pass: app lần một lưu session/progress, app lần hai đọc lại đúng `current_step=2` và `version=2`.
- `[x]` **Bản ghi tại thời điểm Stage 2:** Ruff pass, compile pass, API contract **16 route**, pytest **6 passed**, frontend ESLint/build pass. Số liệu này chỉ để truy vết lịch sử; đã được thay thế bởi gate hiện hành 20 route/12 pytest và không xác nhận production build frontend ở trạng thái hiện tại.
- `[~]` Stage 2 local đã đạt DoD; public staging/production vẫn chưa hoàn tất vì PostgreSQL runtime, runner cô lập, security/E2E/load/backup và pilot còn để roadmap.

## Nhật ký lịch sử — Stage 3 local (đã được thay thế bởi gate hiện hành)

- `[x]` Tách `AIGateway` và `CannedSocraticGateway`; route không phụ thuộc provider cụ thể.
- `[x]` AI response có policy decision/version, model id, citation tới source version, latency và quota cost; quota mặc định 3 lượt/phiên, lỗi vượt quota trả `429`.
- `[x]` Thêm `AnalyticsEvent` vào repository + persistent snapshot; event properties chỉ là số liệu redacted, không ghi raw code/full question.
- `[x]` Thêm `GET /v1/analytics/events` (content admin) và `GET /v1/instructor/sessions/{id}/summary` (role + organization + consent, read-only).
- `[x]` Live practice frontend đã gọi AI/hint API, hiển thị citation link và khóa thứ tự hint 1 → 2 → 3.
- `[~]` Provider AI thật, token/cost budget thực, PostgreSQL runtime, runner cô lập, security/performance/E2E staging, monitoring, backup/restore và public deploy vẫn chưa đóng.

## Liên kết

- [README trạng thái tổng](../README.md)
- [Kế hoạch vòng 3](CodeMind_Round3_MVP_Plan.md)
- [Scope freeze](CodeMind_MVP_Scope_Freeze.md)
- [Backend README](../backend/README.md)
- [Frontend README](../frontend/README.md)
- [CI workflow](../.github/workflows/ci.yml)
