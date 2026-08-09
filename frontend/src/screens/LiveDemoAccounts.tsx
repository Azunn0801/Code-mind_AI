import { useState } from 'react'
import { PublicHeader } from '../components/Shell'
import { navigate } from '../components/navigation'
import { Banner, Button, Card, Chip, EmptyState, Field, Stat } from '../components/UI'
import { learningApi, type AnalyticsEventList, type Role, type TeacherSessionSummary } from '../learning/api'
import { useLearning } from '../learning/LearningContext'
import { LiveApiRecovery } from './LiveApiRecovery'

type DemoAccount = {
  role: Extract<Role, 'student' | 'instructor' | 'content_admin'>
  email: string
  title: string
  detail: string
  route: string
}

const demoAccounts: DemoAccount[] = [
  {
    role: 'student',
    email: 'student.demo@codemind.local',
    title: 'Người học',
    detail: 'Thực hiện luồng deque 6 bước: mục tiêu, nguồn, khái niệm, mã, gợi ý AI và evidence.',
    route: '/demo/setup',
  },
  {
    role: 'instructor',
    email: 'instructor.demo@codemind.local',
    title: 'Giảng viên',
    detail: 'Chỉ xem bản tóm tắt phiên đã được người học cho phép chia sẻ; không chấm hoặc sửa dữ liệu.',
    route: '/demo/instructor',
  },
  {
    role: 'content_admin',
    email: 'admin.demo@codemind.local',
    title: 'Quản trị nội dung',
    detail: 'Chỉ đọc các sự kiện demo đã được rút gọn; không hiển thị mã nguồn hoặc toàn bộ câu hỏi AI.',
    route: '/demo/admin',
  },
]

function DemoAccessRequired({ title }: { title: string }) {
  return <div className="public-page"><PublicHeader /><main className="public-container page-pad"><EmptyState title={title} action={<Button onClick={() => navigate('/demo/access')}>Chọn tài khoản demo</Button>}>Màn hình này chỉ hoạt động sau khi bạn vào bằng đúng tài khoản demo theo vai trò.</EmptyState></main></div>
}

export function LiveDemoAccessPage() {
  const { enterDemoAccount, busy, error, user } = useLearning()
  const [selectedEmail, setSelectedEmail] = useState(demoAccounts[0].email)
  const selected = demoAccounts.find((account) => account.email === selectedEmail) ?? demoAccounts[0]

  const enter = async () => {
    try {
      await enterDemoAccount(selected.email, selected.role)
      navigate(selected.route)
    } catch {
      // LiveApiRecovery presents a role-aware, actionable message.
    }
  }

  return <div className="public-page"><PublicHeader /><main className="public-container page-pad">
    <span className="eyebrow">TÀI KHOẢN DEMO · MVP LOCAL</span>
    <h1>Chọn vai trò để trải nghiệm MVP</h1>
    <p>Đây là các tài khoản demo được seed sẵn cho BGK. Không cần và không sử dụng mật khẩu; đây không phải luồng đăng nhập production.</p>
    {user && <Banner tone="info" title={`Đang dùng ${user.display_name}`}>Bạn có thể đổi vai trò demo bất cứ lúc nào. Khi đổi, dữ liệu hiển thị của vai trò trước sẽ không được dùng làm dữ liệu production.</Banner>}
    <div className="three-grid">
      {demoAccounts.map((account) => <Card key={account.email} className={selected.email === account.email ? 'selected-source' : ''}>
        <div className="source-meta"><Chip tone={account.role === 'student' ? 'success' : 'info'}>{account.title}</Chip><small>demo</small></div>
        <h2>{account.title}</h2>
        <p>{account.detail}</p>
        <code>{account.email}</code>
        <div className="action-row"><Button tone={selected.email === account.email ? 'primary' : 'secondary'} onClick={() => setSelectedEmail(account.email)}>Chọn vai trò</Button></div>
      </Card>)}
    </div>
    <Card className="payment-card"><span className="eyebrow">BƯỚC TIẾP THEO</span><h2>{selected.title}</h2><p>Tài khoản <code>{selected.email}</code> sẽ được xác thực qua API demo. Không có trường mật khẩu trong MVP này.</p><Button disabled={busy} onClick={() => void enter()}>{busy ? 'Đang vào demo…' : `Vào demo với vai trò ${selected.title}`}</Button></Card>
    {error && <LiveApiRecovery />}
  </main></div>
}

export function LiveInstructorSummaryPage() {
  const { user, token, lastStudentSessionId, busy, error } = useLearning()
  const [sessionId, setSessionId] = useState(lastStudentSessionId ?? '')
  const [summary, setSummary] = useState<TeacherSessionSummary | null>(null)

  if (!user || user.role !== 'instructor' || !token) return <DemoAccessRequired title="Cần tài khoản demo Giảng viên" />

  const loadSummary = async () => {
    if (!sessionId.trim()) return
    try {
      setSummary(await learningApi.teacherSummary(sessionId.trim(), token))
    } catch {
      // LiveApiRecovery explains access, stale session, and network errors.
    }
  }

  return <div className="public-page"><PublicHeader /><main className="public-container page-pad">
    <span className="eyebrow">GIẢNG VIÊN · READ-ONLY MVP</span>
    <h1>Bản tóm tắt phiên học được chia sẻ</h1>
    <p>Màn hình này gọi API summary thật. Chỉ những phiên mà người học đã bật quyền chia sẻ mới có thể được xem.</p>
    <Banner tone="info" title="Không có chức năng chấm hoặc sửa dữ liệu">MVP chỉ cho phép giảng viên đọc tiến trình và evidence summary của một phiên đã được đồng ý chia sẻ.</Banner>
    <Card><Field label="ID phiên học" value={sessionId} onChange={setSessionId} placeholder="Tạo một phiên người học trước, rồi dán ID vào đây" /><div className="action-row"><Button disabled={busy || !sessionId.trim()} onClick={() => void loadSummary()}>{busy ? 'Đang tải…' : 'Xem bản tóm tắt'}</Button><Button tone="secondary" onClick={() => navigate('/demo/access')}>Đổi tài khoản demo</Button></div><small>{lastStudentSessionId ? 'Đã điền phiên người học gần nhất trên trình duyệt này. Phiên đó cần bật quyền chia sẻ cho giảng viên.' : 'Chưa có phiên người học trên trình duyệt này. Hãy chạy demo Người học trước.'}</small></Card>
    {summary && <div className="three-grid"><Stat value={`${summary.current_step} / 6`} label="bước đã ghi nhận" tone="info" /><Stat value={summary.test_passed ? '5 / 5' : 'Chưa đạt'} label="kết quả kiểm thử" tone={summary.test_passed ? 'success' : 'warning'} /><Stat value={String(summary.hint_levels.length)} label="mức gợi ý đã mở" tone="warning" /><Card><h3>Evidence</h3><p>{summary.evidence_available ? 'Evidence trước/sau đã có và chỉ hiển thị qua quyền truy cập phù hợp.' : 'Phiên chưa hoàn thành nên chưa có evidence.'}</p></Card><Card><h3>Khái niệm</h3><p>{summary.concept_passed ? `Đạt ${summary.concept_score} mục tiêu nối khái niệm.` : 'Chưa đạt concept check.'}</p></Card><Card><h3>Trạng thái</h3><p>{summary.status === 'completed' ? 'Đã hoàn thành' : 'Đang học'} · phiên chia sẻ đã được xác minh.</p></Card></div>}
    {error && <LiveApiRecovery />}
  </main></div>
}

export function LiveAdminAnalyticsPage() {
  const { user, token, lastStudentSessionId, busy, error } = useLearning()
  const [sessionId, setSessionId] = useState(lastStudentSessionId ?? '')
  const [data, setData] = useState<AnalyticsEventList | null>(null)

  if (!user || user.role !== 'content_admin' || !token) return <DemoAccessRequired title="Cần tài khoản demo Quản trị nội dung" />

  const loadEvents = async () => {
    try {
      setData(await learningApi.analyticsEvents(token, sessionId.trim() || undefined))
    } catch {
      // LiveApiRecovery keeps the failure and recovery route visible.
    }
  }

  return <div className="public-page"><PublicHeader /><main className="public-container page-pad">
    <span className="eyebrow">QUẢN TRỊ NỘI DUNG · READ-ONLY MVP</span>
    <h1>Sự kiện vận hành đã được rút gọn</h1>
    <p>Màn hình này gọi API analytics thật của MVP. Danh sách chỉ hiển thị tên sự kiện, thời điểm và ID phiên; không đưa mã nguồn hoặc câu hỏi đầy đủ vào giao diện.</p>
    <Card><Field label="Lọc theo ID phiên (không bắt buộc)" value={sessionId} onChange={setSessionId} placeholder="Để trống để xem các sự kiện demo" /><div className="action-row"><Button disabled={busy} onClick={() => void loadEvents()}>{busy ? 'Đang tải…' : 'Tải sự kiện demo'}</Button><Button tone="secondary" onClick={() => navigate('/demo/access')}>Đổi tài khoản demo</Button></div></Card>
    {data && <Card><h2>{data.total} sự kiện</h2>{data.events.length === 0 ? <p>Chưa có sự kiện phù hợp. Hãy chạy một phiên Người học rồi tải lại.</p> : <div className="data-table"><div className="data-table__head"><span>Sự kiện</span><span>Phiên</span><span>Thời điểm</span><span>Nguồn</span></div>{data.events.map((event) => <div key={event.id}><span>{event.event_name}</span><span><code>{event.session_id ?? '—'}</code></span><span>{new Date(event.occurred_at).toLocaleString('vi-VN')}</span><span>{event.source}</span></div>)}</div>}</Card>}
    {error && <LiveApiRecovery />}
  </main></div>
}
