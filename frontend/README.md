# CodeMind Beta — MVP Frontend

Frontend React + TypeScript triển khai từ file Figma **Code Mind Beta** cho các luồng Public, Learning Demo, Student, Teacher và Admin.

## Chạy dự án

```bash
npm install
npm run dev
```

Build và kiểm tra mã nguồn:

```bash
npm run lint
npm run build
```

## Điều hướng

Dự án dùng hash routing để có thể chạy độc lập mà không cần cấu hình rewrite trên server.

- `/#/` — Landing page
- `/#/demo/setup` — Bắt đầu luồng học thử
- `/#/student/home` — Student workspace
- `/#/teacher/home` — Teacher workspace
- `/#/admin/home` — Admin console
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

Ứng dụng hiện là frontend tương tác với dữ liệu mẫu tại chỗ. Các form, state machine, loading/error/success và điều hướng đã hoạt động; API, xác thực thật, lưu trữ và backend sẽ được nối ở giai đoạn tiếp theo.
