# CodeMind Round 3 MVP

## Trạng thái hiện tại — 09/08/2026

**Stage hiện tại:** **P0 local release candidate**; MVP sáu bước, ba role demo tối thiểu, API contract/RBAC/consent, persistence adapter và artefact proposal đã được kiểm thử local. Chưa đủ bằng chứng để gọi là staging/production hoặc bộ bài nộp chính thức hoàn chỉnh.

Quy ước: `[x]` = đã có code và bằng chứng local; `[~]` = chỉ local/một phần; `[ ]` = chưa triển khai hoặc chưa có bằng chứng.

## Checklist theo mốc kế hoạch

| Mốc | Trạng thái | Kết luận kiểm tra |
|---|---:|---|
| Scope freeze, use case, data/API contract | `[x]` | Có scope freeze, data spec, API routes và traceability trong `docs/`. |
| Repository, migration đầu, contract checker, CI | `[~]` | Có migration SQL, 20-route contract checker và workflow CI; repository vẫn cần được track/commit/push trước khi có CI remote evidence. |
| Vertical slice demo access → consent → source → concept → code → AI → evidence | `[x]` | Student live six-step flow, Instructor summary read-only và Content admin analytics đều gọi API local; JSON persistence phục hồi session sau restart. |
| PostgreSQL runtime và phục hồi sau restart | `[~]` | `PostgresRepository`, migration `application_state`, readiness và test persistence local đã có; chưa chạy Compose/staging/restore thực tế. |
| AI gateway, quota, citation, analytics events | `[x]` | Gateway canned local, quota 3 lượt/phiên, citation, redacted analytics và HMAC demo token/consent/RBAC có test. Provider thật/observability production còn pending. |
| Isolated runner, security, performance, E2E, backup/restore | `[~]` | Có contract/RBAC/recovery UI và test local; runner vẫn simulated, chưa có browser E2E/load/security scan/backup restore evidence. |
| Public deploy và pilot 5–10 người | `[ ]` | Chưa có URL public, demo accounts production hoặc pilot log. |

## Bằng chứng gần nhất

- Gate local được dùng làm mốc hiện hành ngày 09/08/2026: backend Ruff, compile, contract **20 route bắt buộc**, **12 test pass**; frontend **ESLint và production build pass**. Build đã được chạy lại tại đúng thư mục MVP gốc sau khi sửa canonical Vite root cho đường dẫn junction/D:.
- Test xác nhận signed demo token/expiry, consent grant/revoke, term source validation, idempotency, quota AI, citation/policy metadata, analytics/RBAC, teacher summary, persistence file/PostgreSQL adapter và readiness.
- CI khai báo các gate tại [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Chạy local

Backend dùng cổng `8765`; frontend live flow bắt đầu ở `/#/demo/access`. Các route `/#/design/...` và workspace catalog vẫn là Figma prototype tĩnh.

## Tài liệu làm chuẩn

- [Progress log cho team](docs/CodeMind_Progress_Log.md)
- [Kế hoạch vòng 3 và Section 9](docs/CodeMind_Round3_MVP_Plan.md)
- [Scope freeze](docs/CodeMind_MVP_Scope_Freeze.md)
- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [Data specification workbook](docs/CodeMind_MVP_Data_Spec.xlsx)
- [Data-spec status log](docs/CodeMind_MVP_Data_Spec_Status_Log.md)
- [Pilot protocol](docs/CodeMind_Pilot_Protocol.md)
- [Biên bản kiểm chứng local](docs/CodeMind_Validation_Report.md)
- [Proposal PDF](<deliverables/%5BKHOINGUYEN%20-%20VONG%203%5D%20-%20CodeMind.pdf>)

Chỉ đánh dấu `[x]` khi có code/config và bằng chứng kiểm tra tương ứng. Figma, migration hoặc stub chưa đủ để đánh dấu hoàn tất.

## Nhật ký lịch sử — Stage 2 (đã được thay thế bởi gate hiện hành)

**Stage 2 local DoD:** `[x]` đã hoàn tất. Backend hiện lưu session/progress/submission/evidence vào snapshot JSON nguyên tử và có test xác nhận đọc lại sau khi dựng app lần hai.

**Bản ghi tại thời điểm Stage 2:** backend Ruff, compile, API contract **16 route**, pytest **6 passed**; frontend ESLint và production build từng pass ở commit/mốc khi đó. Các số liệu này chỉ lưu lịch sử, **không phải** gate hiện hành và đã được thay thế bởi mốc 20 route/12 test ở phần “Bằng chứng gần nhất”; trạng thái production build hiện tại cần được kiểm tra riêng. Phần còn thiếu để gọi là staging vẫn là public URL, PostgreSQL production, runner cô lập và pilot.

## Nhật ký lịch sử — Stage 3 local (đã được thay thế bởi gate hiện hành)

`[x]` Gateway AI local đã tách khỏi route qua `AIGateway`/`CannedSocraticGateway`, lưu policy decision, model, latency, quota cost và citation source. Mỗi phiên có tối đa 3 lượt hỏi; quá quota trả lỗi `429` có details rõ ràng.

`[x]` Analytics event được redacted, lưu bền vững cùng snapshot và chỉ `content_admin` đọc qua `GET /v1/analytics/events`. Teacher summary read-only kiểm tra role + organization + consent và không trả raw code.

`[x]` Live practice frontend có luồng hỏi AI → mở gợi ý 1–3 theo thứ tự → mở link nguồn chính thức.

`[~]` Provider AI thật, Compose/staging PostgreSQL, runner cô lập, security/performance/E2E staging, monitoring, backup/restore và public deploy vẫn là scope tiếp theo.

## Gói nộp Round 3 và trạng thái release

Thông báo làm rõ mới hơn của Ban Tổ chức cho phép **báo cáo chi tiết tối đa 60 trang nội dung** (không tính bìa/phụ lục). Giới hạn dung lượng an toàn **30 MB** trong đề gốc vẫn được giữ. Báo cáo chỉ được mô tả một hạng mục là “đã triển khai” khi có code và bằng chứng chạy tương ứng.

- [ ] URL MVP public HTTPS, account demo theo role và nghiệm thu cửa sổ ẩn danh: chưa có.
- [ ] Compose/staging PostgreSQL, runner cô lập, provider AI thật, browser E2E, security/load và backup/restore staging: chưa có bằng chứng.
- [~] PDF báo cáo chi tiết: đã render QA **22 trang vật lý**, khoảng **185 KB**, có cover/user-flow/architecture/ERD/API/QA/business/finance/roadmap; cấu trúc nằm dưới giới hạn **≤60 trang nội dung** (không tính bìa/phụ lục) và **≤30 MB**. Cần điền team/mentor/member, URL public và dữ liệu pilot thật trước nộp.
- Theo phạm vi công việc hiện tại của chủ dự án, **không thực hiện slide và video**. Tuy nhiên đây vẫn là hai yêu cầu chính thức của Ban Tổ chức, nên không được coi là bộ bài nộp chính thức đầy đủ nếu chưa tự bổ sung hoặc được miễn.

Tài liệu vận hành trước release:

- [Hướng dẫn trải nghiệm, tài khoản demo và checklist ẩn danh](docs/CodeMind_MVP_Experience_Guide.md)
- [Deployment runbook và ranh giới Docker/PostgreSQL](docs/CodeMind_Deployment_Runbook.md)
- [Traceability từ Vòng 2, đề bài và Figma](docs/CodeMind_Round3_Traceability.md)
