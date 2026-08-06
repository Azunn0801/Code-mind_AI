export type NavItem = { label: string; path: string }

export function navigate(path: string) {
  window.location.hash = `#${path}`
}

export const studentNav: NavItem[] = [
  { label: 'Hôm nay', path: '/student' },
  { label: 'Tài liệu', path: '/student/docs' },
  { label: 'Khái niệm', path: '/student/concept' },
  { label: 'Luyện tập', path: '/student/practice' },
  { label: 'Xem lại', path: '/student/review' },
  { label: 'Ghi chú', path: '/student/notes' },
]

export const teacherNav: NavItem[] = [
  { label: 'Trang chủ', path: '/teacher' },
  { label: 'Lớp học', path: '/teacher/classes' },
  { label: 'Học viên', path: '/teacher/roster' },
  { label: 'Bài tập', path: '/teacher/assignments' },
  { label: 'Tạo bài', path: '/teacher/builder' },
  { label: 'Chấm bài', path: '/teacher/review' },
]

export const adminNav: NavItem[] = [
  { label: 'Tổng quan', path: '/admin' },
  { label: 'Nguồn', path: '/admin/sources' },
  { label: 'Thuật ngữ', path: '/admin/glossary' },
  { label: 'Phê duyệt', path: '/admin/approval/microtask' },
  { label: 'Hỗ trợ', path: '/admin/support' },
  { label: 'Nội dung', path: '/admin/feedback' },
  { label: 'Bảo mật', path: '/admin/security' },
]
