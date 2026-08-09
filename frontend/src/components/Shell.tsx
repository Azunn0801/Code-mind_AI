import { useState, type ReactNode } from 'react'
import { navigate } from './navigation'
import type { NavItem } from './navigation'

export function PublicHeader() {
  const [isMenuOpen, setMenuOpen] = useState(false)
  const nav: NavItem[] = [
    { label: 'Giới thiệu', path: '/' },
    { label: 'MVP trực tiếp', path: '/demo/access' },
    { label: 'Cách học', path: '/integrity' },
  ]
  const goTo = (path: string) => {
    setMenuOpen(false)
    navigate(path)
  }
  return (
    <header className="public-header">
      <button className="brand" onClick={() => goTo('/')}>CodeMind AI</button>
      <nav aria-label="Điều hướng công khai">
        {nav.map((item) => <button key={item.path} onClick={() => goTo(item.path)}>{item.label}</button>)}
      </nav>
      <div className="public-header__actions">
        <button className="text-link" onClick={() => goTo('/demo/access')}>Tài khoản demo</button>
        <button className="button button--primary" onClick={() => goTo('/demo/access')}>Mở MVP</button>
      </div>
      <button className="mobile-menu" aria-expanded={isMenuOpen} onClick={() => setMenuOpen((current) => !current)}>{isMenuOpen ? 'Đóng' : 'Menu'}</button>
      {isMenuOpen && <nav className="public-header__mobile-menu" aria-label="Điều hướng di động">{nav.map((item) => <button key={item.path} onClick={() => goTo(item.path)}>{item.label}</button>)}<button onClick={() => goTo('/demo/access')}>Tài khoản demo</button></nav>}
    </header>
  )
}

export function AppShell({
  kind,
  badge,
  status,
  nav,
  active,
  children,
}: {
  kind: 'student' | 'teacher' | 'admin'
  badge: string
  status: string
  nav: NavItem[]
  active: string
  children: ReactNode
}) {
  const names = { student: 'CodeMind', teacher: 'CodeMind Campus', admin: 'CodeMind Quản trị' }
  return (
    <div className={`app-shell app-shell--${kind}`}>
      <header className="app-header">
        <div className="app-header__left"><b>{names[kind]}</b><span className="app-badge">{badge}</span><span className="app-badge prototype-badge">Figma prototype · dữ liệu mẫu</span></div>
        <span className="app-header__status">{status}</span>
      </header>
      <div className="app-shell__body">
        <aside className="side-nav">
          <nav aria-label={`Điều hướng ${names[kind]}`}>
            {nav.map((item) => (
              <button key={item.path} className={active === item.path ? 'active' : ''} onClick={() => navigate(item.path)}>
                {item.label}
              </button>
            ))}
          </nav>
          <button className="side-nav__catalog" onClick={() => navigate('/designs')}>142 thiết kế</button>
        </aside>
        <main className="app-content">{children}</main>
      </div>
    </div>
  )
}

const lessonSteps = [
  ['1', 'Mục tiêu', '/demo/objective'],
  ['2', 'Tài liệu', '/demo/source'],
  ['3', 'Khái niệm', '/demo/concept'],
  ['4', 'Luyện tập', '/demo/practice'],
  ['5', 'Trợ giảng AI', '/demo/ai'],
  ['6', 'Xem lại', '/demo/evidence'],
]

export function LessonShell({ step, status, children, mobile = false }: { step: number; status: string; children: ReactNode; mobile?: boolean }) {
  return (
    <div className={`lesson-shell ${mobile ? 'lesson-shell--mobile' : ''}`}>
      <header className="lesson-header">
        {mobile ? <><b>CodeMind</b><span className="lesson-chip">{Math.min(step, 6)} / 6</span><span className="lesson-chip">{status}</span></> : <><b>CodeMind</b><span className="lesson-chip">Bài học: deque</span><nav><span>Hôm nay</span><span>Tài liệu</span><span>Luyện tập</span><span>Bài đánh giá</span><span>Ghi chú</span><span>Cộng đồng</span></nav><span className="lesson-chip">{status}</span></>}
      </header>
      <div className="lesson-shell__body">
        {!mobile && <aside className="lesson-rail">
          <b>TIẾN TRÌNH BÀI HỌC</b>
          {lessonSteps.map(([number, label, path]) => (
            <button key={number} className={step === Number(number) ? 'active' : step > Number(number) ? 'done' : ''} onClick={() => navigate(path)}>
              <span>{number}</span>{label}
            </button>
          ))}
          <small>Nguồn: Python 3.12<br />Lịch sử hỗ trợ: đang lưu<br />Chia sẻ: do bạn kiểm soát</small>
        </aside>}
        <main className="lesson-content">{children}</main>
      </div>
    </div>
  )
}
