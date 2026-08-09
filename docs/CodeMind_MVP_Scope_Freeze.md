# CodeMind Round 3 — P0 Scope Freeze

**Mốc:** 22–24/07/2026 (hoàn tất baseline ngày 06/08/2026)  
**Trạng thái:** Baseline P0 đã khóa để triển khai  
**Mục tiêu:** một vertical slice có thể kiểm thử từ đăng nhập demo đến evidence.

## 1. Phạm vi P0

| ID | Phạm vi | Acceptance chính |
|---|---|---|
| P0-01 | Demo login cho student/instructor | Token demo xác định đúng user/role; user lạ bị từ chối |
| P0-02 | Một lesson `deque` duy nhất | Lesson có version và source snapshot Python 3.12 cố định |
| P0-03 | Consent | Không có `academic_integrity` thì không tạo learning session; `teacher_visibility` tách riêng |
| P0-04 | Luồng 6 bước | Objective → Source → Concept → Practice → AI → Review; progress có optimistic version |
| P0-05 | Source trust | Client nhận URL, version, checksum và excerpt của snapshot đã pin |
| P0-06 | Term + concept check | Student tự chọn thuật ngữ và nối đúng hai quan hệ khái niệm |
| P0-07 | Submission | Có 5 kết quả test an toàn, idempotency key và trạng thái retry được |
| P0-08 | Socratic AI | Không trả đáp án hoàn chỉnh; hint mở tuần tự 1 → 2 → 3 |
| P0-09 | Evidence | Chỉ complete khi có term, concept pass và submission đạt 5/5; lưu before/after |
| P0-10 | Instructor read-only | Chỉ xem evidence cùng tổ chức và khi student bật teacher visibility |
| P0-11 | Privacy/health | Có health/live, health/ready và yêu cầu xóa dữ liệu; không log secret/hidden output |

### Ngoài phạm vi P0

Pricing/checkout, nhiều course, campus admin đầy đủ, community/leaderboard/hearts,
MOSS đồng bộ thời gian thực, adaptive learning, OAuth production, analytics dashboard,
PostgreSQL runtime bắt buộc, AI provider thật và code runner thực thi mã không nằm trong
critical path local của mốc này. Đây là P1/P2 hoặc adapter thay thế sau khi contract ổn định.

## 2. Use case và luồng chấp nhận

### UC-01 — Student hoàn thành lesson

1. Student đăng nhập demo và đồng ý academic integrity.
2. Backend tạo session, pin lesson/source version và trả progress version.
3. Student đọc source, chọn thuật ngữ, nộp concept answer.
4. Student gửi code; runner trả 4/5 hoặc 5/5 test result đã lọc.
5. Student hỏi AI; policy từ chối đáp án đầy đủ và mở hint theo thứ tự.
6. Khi đạt 5/5, backend tạo immutable evidence before/after.

### UC-02 — Instructor xem evidence được phép

Instructor chỉ nhận được evidence khi cùng organization và consent `teacher_visibility`
đang được grant. Mọi trường hợp khác trả `403` và không lộ raw code ngoài scope.

### UC-03 — Khôi phục và chống gửi trùng

Student có thể GET lại session sau refresh. PATCH progress yêu cầu `expected_version`;
submission lặp cùng `Idempotency-Key` trả lại submission cũ thay vì tạo job mới.

## 3. Contract đã chốt

### API P0

| Method | Endpoint | Mục đích |
|---|---|---|
| GET | `/health/live`, `/health/ready` | Liveness/readiness |
| POST | `/v1/demo/session` | Demo authentication |
| GET | `/v1/lessons/{slug}` | Lesson + pinned source |
| POST | `/v1/learning-sessions` | Tạo session sau consent |
| GET/PATCH | `/v1/learning-sessions/{id}` và `/progress` | Restore/lưu tiến trình |
| POST | `/v1/sessions/{id}/terms` | Lưu thuật ngữ student chọn |
| POST | `/v1/sessions/{id}/concept-answers` | Chấm concept |
| POST/GET | `/v1/sessions/{id}/submissions`, `/v1/submissions/{id}` | Submission/test result |
| POST | `/v1/sessions/{id}/ai-interactions` | Policy Socratic |
| POST | `/v1/ai-interactions/{id}/hints/{level}/open` | Hint ladder |
| POST | `/v1/sessions/{id}/complete` | Tạo evidence |
| GET | `/v1/sessions/{id}/evidence` | Student/instructor read |
| DELETE | `/v1/me/data` | Tạo privacy deletion request |

### Data contract

- Entity/field/relationship/RBAC/lifecycle tiếp tục lấy workbook làm source of truth:
  `01_Entity_Catalog`, `02_Data_Dictionary`, `03_Relationships`, `04_Enums_Rules`,
  `07_RBAC`, `08_Data_Lifecycle`.
- SQL baseline nằm tại `backend/migrations/001_initial.sql` và có bảng identity,
  consent, source/version, lesson/steps, session, attempts, terms, concept,
  submission/test run/result, AI/hint, evidence và audit.
- Sample lesson và demo account nằm tại `backend/app/infrastructure/seed.py`.
- Raw code/AI content vẫn phải áp retention trước production; local adapter không được
  hiểu là bằng chứng deploy production.

## 4. Quyết định khóa phạm vi

1. Chỉ một lesson `deque`; ưu tiên evidence và độ tin cậy hơn số lượng màn hình.
2. Source phải pin version + checksum; không phụ thuộc trang live để replay evidence.
3. Teacher visibility là consent riêng, không suy ra từ academic integrity.
4. PostgreSQL, isolated runner và AI gateway được thiết kế qua port/adapter; test dùng
   in-memory để deterministic, còn profile local mặc định dùng `PersistentRepository`
   snapshot JSON. Cả hai chưa phải PostgreSQL runtime; runner vẫn simulated và AI vẫn
   canned policy.
5. Không có đáp án hoàn chỉnh hoặc hidden expected output trong response client.

## 5. Bằng chứng hoàn tất mốc đầu tiên

- API contract được kiểm tra bằng `backend/scripts/check_contract.py`.
- Backend lint: `ruff check app tests`.
- Backend syntax: `python -m compileall -q app tests`.
- Backend behavior: `python -m pytest`.
- Frontend gates: `npm ci`, `npm run lint`, `npm run build`.
- CI chính thức: `.github/workflows/ci.yml`.

Mọi hạng mục phía trên là gate của mốc scope/contract/repo. Các mục deploy public,
load/security/backup và pilot thuộc các mốc sau, không được đánh dấu “đã triển khai”
chỉ vì đã có file thiết kế.
