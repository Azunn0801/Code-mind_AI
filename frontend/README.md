# CodeMind Beta — MVP Frontend

Frontend React + TypeScript triển khai từ file Figma **Code Mind Beta** cho các luồng Public, Learning Demo, Student, Teacher và Admin.

## Chạy dự án

```bash
npm install
npm run dev
```

Để chạy vertical slice live, hãy khởi động backend trước tại
`http://127.0.0.1:8765`, sau đó chạy frontend. Vite proxy `/api` tới backend nên
không cần thêm CORS khi phát triển local.

- `/#/demo/access` — chọn role demo; Student đi qua flow live 6 bước, Instructor/Content admin có màn read-only tối thiểu nối API
- Các route Figma trong `/#/design/...` vẫn giữ state tĩnh để xem catalog thiết kế.

Build và kiểm tra mã nguồn:

```bash
npm run lint
npm run build
```

## Điều hướng

Dự án dùng hash routing để có thể chạy độc lập mà không cần cấu hình rewrite trên server.

- `/#/` — Landing page
- `/#/demo/access` — Bắt đầu MVP bằng tài khoản demo
- `/#/demo/setup` — Setup của một phiên Student đã xác thực
- `/#/demo/instructor` — Instructor summary read-only của phiên đã consent
- `/#/demo/admin` — Content admin analytics đã redacted
- `/#/student`, `/#/teacher`, `/#/admin` — catalog prototype/dữ liệu mẫu, không phải dashboard MVP live
- `/#/designs` — Danh mục toàn bộ thiết kế Figma đã ánh xạ
- `/#/design/10402-2018` — Mở trực tiếp thiết kế theo node ID Figma

Danh mục hiện ánh xạ **142 frame/state** từ Figma, gồm 70 thiết kế public/lesson, 28 student, 16 teacher và 28 admin. Các frame mobile được mở trong khung preview mobile tương ứng.

## Cấu trúc chính

- `src/designs.ts` — catalog node Figma → route/state/viewport
- `src/components/` — UI primitives, shell và navigation dùng chung
- `src/screens/PublicPages.tsx` — public, auth, commerce và legal
- `src/screens/LearningDemo.tsx` — luồng học 6 bước và các trạng thái lỗi
- `src/screens/StudentPages.tsx` — dashboard, tài liệu, luyện tập, AI và ghi chú
- `src/screens/TeacherPages.tsx` — lớp học, assignment builder, review và settings
- `src/screens/AdminPages.tsx` — quản trị nguồn, người dùng, analytics, security và support

## Phạm vi MVP

Ứng dụng hiện có hai lớp:

- `/#/demo/access` và các route `/#/demo/...` là live vertical slice gọi FastAPI qua Vite proxy `/api`: chọn account demo, consent, source, concept check, code/test, AI Socratic/citation/hint ladder, progress và evidence. Instructor summary và Content admin analytics là UI read-only tối thiểu.
- Các route Figma catalog và workspace Student/Teacher/Admin đầy đủ còn dùng state/mock UI để đối chiếu thiết kế, luôn phải được xem là prototype.

Xác thực production, PostgreSQL qua Compose/staging, runner cô lập, provider AI thật, E2E và deploy HTTPS chưa được đánh dấu hoàn tất. Xem [progress log](../docs/CodeMind_Progress_Log.md) để biết điều kiện chuyển sang staging.

## Tiến độ thực tế — 09/08/2026

- `[x]` 142 frame/state Figma đã có route catalog.
- `[x]` Live demo flow, chọn ba role demo, Instructor summary và Content admin analytics đã nối API với loading/error/recovery state.
- `[x]` Vite proxy, ESLint và production build đã pass sau khi nối API client/context cho AI interaction và hint ladder; Vite root đã được canonical hóa để build đúng từ cả junction làm việc và thư mục D: gốc.
- `[~]` Chỉ vertical slice và hai màn read-only tối thiểu dùng API; các workspace/catalog còn lại chưa nối backend production.
- `[x]` Backend local persistence đã giữ session/progress qua lần khởi động lại app.
- `[ ]` Chưa có staging URL, E2E browser, auth thật hoặc persistence production.

## Cập nhật Stage 2 — persistence local

Live flow vẫn dùng localStorage để phục hồi giao diện và nay backend profile mặc định cũng giữ session/progress qua lần khởi động lại app bằng snapshot JSON. Test backend đã xác nhận luồng này; các workspace Student/Teacher/Admin vẫn là catalog/mock và chưa được đánh dấu backend production.

## Cập nhật Stage 3 — AI coach local

Màn hình luyện tập có panel AI Coach thân thiện: gửi câu hỏi, nhận phản hồi Socratic kèm link nguồn chính thức, sau đó mở gợi ý 1 → 2 → 3. Frontend hiển thị quota còn lại và không mở mức tiếp theo khi chưa mở mức trước; provider thật và streaming vẫn để sau staging.
