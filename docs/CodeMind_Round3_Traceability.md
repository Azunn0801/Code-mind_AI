# CodeMind — Ma trận truy vết phạm vi Vòng 3

**Phiên bản:** 1.0  
**Ngày rà soát:** 09/08/2026  
**Nguồn đối chiếu:** Báo cáo Vòng 2 `CodeMind - FundFlow.docx`; Đề bài Vòng 3; thông báo làm rõ của Ban Tổ chức; Figma Code Mind Beta; source code và `CodeMind_MVP_Data_Spec.xlsx`.

## 1. Cách đọc trạng thái

- **Đã chạy trong vertical slice:** có luồng frontend–API và test/local evidence. Đây là phần duy nhất được phép gọi là “đã triển khai” trong báo cáo.
- **Đã có thiết kế/đặc tả:** Figma hoặc data/API spec đã mô tả, nhưng chưa phải chức năng vận hành; không được mô tả như đã hoàn thành.
- **Lộ trình có chủ đích:** vẫn là cam kết sản phẩm từ báo cáo Vòng 2, được giữ nguyên trong roadmap; không xóa, không đổi tên thành chức năng MVP đã có.
- **Cần bằng chứng ngoài repository:** cần quyền cloud, tài khoản dịch vụ, pilot thực tế hoặc dữ liệu do đội cung cấp. Không thể xác nhận chỉ bằng code local.

## 2. Nguyên tắc khóa phạm vi

MVP Round 3 không được thu nhỏ bằng cách bỏ cam kết của Vòng 2. Thay vào đó, đội xác thực **một lát cắt dọc** của cùng learning loop: người học đọc nguồn chính thức, tự làm rõ khái niệm, thực hành code, nhận gợi ý Socratic thay vì đáp án, rồi lưu evidence. Các hạng mục rộng hơn vẫn được giữ nguyên ở roadmap và có điều kiện mở rộng rõ ràng.

Mọi claim trong PDF, README và demo phải dùng đúng trạng thái trong bảng dưới. Nếu một trạng thái thay đổi, cập nhật cả ba nơi trong cùng pull request/release.

## 3. Truy vết cam kết sản phẩm Vòng 2

| Cam kết từ Vòng 2 | Quyết định Round 3 | Trạng thái repository khi rà soát | Bằng chứng/điều kiện đóng |
|---|---|---|---|
| Đọc tài liệu chính thức, giải thích thuật ngữ tiếng Việt theo ngữ cảnh | Giữ trong vertical slice Deque/Python; source được gắn citation | Đã chạy trong vertical slice (nguồn seed + chọn thuật ngữ) | Source snapshot có version/checksum thật; E2E chọn thuật ngữ và citation |
| Hệ thống hóa mental model bằng Mindmap Challenge/Master Graph | Giữ là module tiếp theo của cùng lesson loop; P0 dùng concept check có cấu trúc để kiểm chứng quan hệ khái niệm | Đã có thiết kế/đặc tả, concept check chạy local | Cần graph authoring, matching/scoring và UX mindmap thật trước khi claim Mindmap Challenge hoàn chỉnh |
| Coding lab và AI Socratic, không đưa code sửa sẵn | Bắt buộc ở vertical slice | Đã chạy local (canned Socratic policy, hint 1→3, không trả lời hoàn chỉnh) | Cần AI provider/policy suite và runner cô lập để gọi là production |
| GitHub OAuth + MOSS chống đạo văn hai lớp | Giữ nguyên, không đưa vào đường demo P0 để tránh claim sai | Lộ trình có chủ đích | Cần OAuth app, chính sách consent, MOSS/legal approval, asynchronous similarity review và pilot học thuật |
| VARK: visual/flowchart, auditory/TTS, kinesthetic/code lab | Giữ nguyên cho adaptive learning phase | Đã có thiết kế/đặc tả | Cần preference onboarding, content variants, TTS consent/accessibility và outcome evaluation |
| League, XP, streak, Hearts, skin/avatar/badge | Giữ nguyên cho engagement phase | Các màn hình Figma/catalog tĩnh | Cần thuật toán league/weekly job, ledger XP/Hearts, anti-abuse, quy tắc recovery/conversion và test fairness |
| Community, comment sau bài tập, reputation/upvote | Giữ nguyên cho community phase | Các màn hình Figma/catalog tĩnh | Cần completion gate, moderation, report/appeal, privacy and safety controls |
| Free/Plus/Pro/Campus quota & payment | Giữ nguyên mô hình thương mại; chưa mở checkout trong MVP | Các màn hình pricing/catalog tĩnh; quota hint P0 là quota demo, không phải billing | Cần entitlement ledger, payment provider, invoice/refund, tax/legal và A/B pricing |
| Quảng cáo có rào chắn đạo đức và A/B retention rollback | Giữ nguyên nhưng không chạy quảng cáo trong learning workspace | Chưa triển khai runtime | Cần consent/minor handling, allow-list surface, frequency cap, experiment/rollback, ad-policy review |
| B2B2C/Campus, teacher view | P0 chứng minh teacher read-only dựa trên consent; Campus đầy đủ là phase sau | Có màn demo Instructor summary read-only và Content admin analytics tối thiểu nối API local; dashboard Teacher/Admin đầy đủ vẫn tĩnh | Cần org/class membership, data-processing agreement, dashboard không lộ raw code, audit và pilot trường |
| React + Vite + Tailwind; FastAPI; PostgreSQL; Redis; AI/RAG/citation | Giữ kiến trúc đích; MVP phải diễn giải trung thực adapter nào đang chạy | React/Vite/FastAPI, file persistence và Postgres P0 adapter/migration/readiness đã có bằng chứng local; Redis/RAG/provider và PostgreSQL Compose/staging vẫn cần xác nhận runtime | Migration, DB adapter, health/readiness, secret management, cache/rate-limit, source snapshot/citation, deployment evidence |
| Pilot 30–50 người, completion/self-correction/D7 | Bắt buộc để kiểm chứng after deployment, không được tự điền số | Cần bằng chứng ngoài repository | Pilot protocol, consent, sample/period, export aggregate, limitations và owner review |

## 4. Figma và luồng demo được phép dùng

Figma hiện có 142 frame gồm public/lesson/student/teacher/admin. Chỉ các route sau là **MVP tương tác**:

`/#/demo/access → /setup → /objective → /source → /concept → /practice → /ai → /evidence`

Luồng này dùng một lesson Deque/Python, gồm sáu bước học; `/demo/ai` là chặng hỗ trợ Socratic gọi API giữa thực hành và evidence. Các route `/#/design/...`, Student, Teacher và Admin là **thiết kế tham chiếu/prototype**, trừ khi một release note ghi rõ route đã được nối API và có test. Không sử dụng chúng làm bằng chứng “chức năng đã hoàn thành” trong demo hay PDF.

Các trạng thái recovery từ Figma cần được kiểm thử cho source unavailable, quota exceeded, submission error và note empty. Mỗi trạng thái cần action retry/back/fallback và không làm mất tiến trình đã lưu.

## 5. Yêu cầu Round 3 → artefact phải có

| Yêu cầu | Artefact trong repo | Cách xác nhận |
|---|---|---|
| MVP tương tác, giải quyết pain Vòng 2 | Frontend + FastAPI + demo script | Browser E2E trên URL public, không dùng localhost |
| UI/UX và so sánh với Vòng 2 | Figma audit + ảnh/sơ đồ trong proposal | Review theo luồng 6 bước; label prototype rõ ràng |
| Kiến trúc, ERD, dữ liệu/API | `CodeMind_MVP_Data_Spec.xlsx`, proposal, OpenAPI | Schema/API/role/retention đồng bộ với code |
| Tech stack/DevOps | Dockerfiles, compose, CI, deployment runbook | Container smoke, migration, public release evidence |
| QA/security | test log, policy/risk matrix, backup runbook | Test command/output có ngày; restore and security checks |
| URL, demo accounts, quyền role | `docs/CodeMind_MVP_Experience_Guide.md` | Incognito test trên deployment; không ghi mật khẩu production vào Git |
| Proposal Template | PDF báo cáo chi tiết và nguồn Markdown | ≤60 trang nội dung theo thông báo mới; giữ ≤30MB theo yêu cầu gốc còn hiệu lực |

## 6. Điều kiện “hoàn tất để nộp”

Không tick toàn bộ checklist cho đến khi có đủ: deployment công khai HTTPS, tài khoản demo Student/Instructor/Content admin hoạt động, browser E2E happy path, migration/persistence/backup evidence, URL/role matrix, và pilot hoặc ghi rõ “chưa có số liệu pilot”. Video và slide được chủ sở hữu dự án tạm loại khỏi công việc này, nhưng vẫn là yêu cầu chính thức của Ban Tổ chức; việc ngoại lệ được ghi trong compliance log.
