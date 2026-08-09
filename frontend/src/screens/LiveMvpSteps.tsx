import { useState } from 'react'
import { Banner, Button, Card, Chip, CodeBlock, EmptyState } from '../components/UI'
import { LessonShell } from '../components/Shell'
import { navigate } from '../components/navigation'
import { useLearning } from '../learning/LearningContext'
import { LiveApiRecovery } from './LiveApiRecovery'

function NoSession({ step }: { step: number }) {
  return <LessonShell step={step} status="Chưa có phiên"><EmptyState title="Chưa có phiên học" action={<Button onClick={() => navigate('/demo/access')}>Chọn tài khoản demo</Button>}>Hãy vào bằng tài khoản demo Người học và tạo phiên trước khi đi tiếp.</EmptyState></LessonShell>
}

export function LiveAiPage() {
  const { session, lastSubmission, aiInteraction, openedHints, askAi, openHint, busy, error } = useLearning()
  const [question, setQuestion] = useState('Vì sao history vẫn có thể nhận chuỗi rỗng?')

  if (!session) return <NoSession step={5} />
  if (!lastSubmission) return <LessonShell step={5} status="Chờ bài làm"><EmptyState title="Hãy chạy mã trước" action={<Button onClick={() => navigate('/demo/practice')}>Quay lại bước luyện tập</Button>}>Trợ giảng AI chỉ xuất hiện sau khi bạn đã gửi một lần chạy kiểm thử của mình.</EmptyState></LessonShell>

  const ask = async () => {
    try {
      await askAi(question)
    } catch {
      // The recovery panel below keeps API failures actionable.
    }
  }
  const showHint = async (level: number) => {
    try {
      await openHint(level)
    } catch {
      // Hint ordering is explained by the mapped recovery state.
    }
  }
  const nextHint = openedHints.length + 1

  return <LessonShell step={5} status={aiInteraction ? `Đã hỏi · ${openedHints.length}/3 gợi ý` : 'Chờ câu hỏi'}>
    <div className="lesson-heading"><span>BƯỚC 5 / 6 · LIVE SOCRATIC COACH</span><h1>Nhận gợi ý để tự tìm chỗ cần sửa</h1><p>Đây là bước live gọi API AI của MVP. Trợ giảng chỉ đặt câu hỏi, trích nguồn chính thức và mở gợi ý theo thứ tự; không trả lời làm hộ.</p></div>
    <div className="ai-layout"><Card className="conversation"><div><b>Điểm đang mắc</b><p>{lastSubmission.passed_count} / {lastSubmission.total_count} kiểm thử đạt. Kết quả này là ngữ cảnh cho câu hỏi của bạn.</p></div>{aiInteraction ? <><div><b>Trợ giảng AI</b><p>{aiInteraction.message}</p><small>Chính sách: {aiInteraction.policy_decision} · {aiInteraction.model_id}</small></div>{openedHints.map((hint) => <div key={hint.level}><b className="text-info">Gợi ý mức {hint.level}</b><p>{hint.hint}</p></div>)}</> : <div><b>Trợ giảng AI</b><p>Hãy mô tả điều bạn chưa hiểu trong lần chạy vừa rồi. Bạn sẽ nhận được gợi ý theo hướng Socratic.</p></div>}</Card><Card className="ai-coach-card"><span className="eyebrow">HỎI THEO CÁCH CỦA BẠN</span><h3>Hãy thử diễn đạt điểm bạn đang vướng</h3><div className="action-row"><input value={question} onChange={(event) => setQuestion(event.target.value)} aria-label="Câu hỏi cho AI" placeholder="Bạn đang vướng ở đâu?" /><Button disabled={busy || !question.trim()} onClick={() => void ask()}>{busy ? 'Đang hỏi…' : 'Hỏi AI'}</Button></div>{aiInteraction && <><a className="source-link" href={aiInteraction.citation.url} target="_blank" rel="noreferrer">{aiInteraction.citation.title} · {aiInteraction.citation.version_label} ↗</a><p>AI còn {aiInteraction.quota_remaining} lượt hỏi trong phiên này.</p><div className="hint-actions">{[1, 2, 3].map((level) => <Button key={level} tone={openedHints.some((hint) => hint.level === level) ? 'secondary' : 'primary'} disabled={busy || (!openedHints.some((hint) => hint.level === level) && level !== nextHint)} onClick={() => void showHint(level)}>{openedHints.some((hint) => hint.level === level) ? `Đã mở gợi ý ${level}` : `Mở gợi ý ${level}`}</Button>)}</div>{openedHints.length === 3 && <Banner tone="success" title="Đã đủ gợi ý để tự sửa">Quay lại mã, tự thêm điều kiện kiểm tra rồi chạy lại bộ kiểm thử.</Banner>}</>}</Card></div>
    {error && <LiveApiRecovery />}
    <div className="lesson-actions"><Button tone="secondary" onClick={() => navigate('/demo/source')}>Xem lại nguồn</Button><Button onClick={() => navigate('/demo/practice')}>Quay lại mã để tự sửa</Button></div>
  </LessonShell>
}

export function LiveEvidencePage() {
  const { evidence, session } = useLearning()
  if (!session || !evidence) return <LessonShell step={6} status="Chưa có evidence"><EmptyState title="Chưa có evidence" action={<Button onClick={() => navigate('/demo/practice')}>Quay lại luyện tập</Button>}>Hãy đạt 5/5 ở bước luyện tập để tạo bằng chứng.</EmptyState></LessonShell>

  return <LessonShell step={6} status="Đã hoàn thành"><div className="lesson-heading"><span>BƯỚC 6 / 6 · EVIDENCE</span><h1>Quá trình tự sửa đã được lưu</h1><p>Evidence này được tạo bởi backend sau khi phiên đạt đủ điều kiện hoàn thành.</p></div><div className="four-grid evidence-stats"><Card><b className="text-success">{evidence.passed_count} / {evidence.total_count}</b><p>Ca kiểm thử đạt</p></Card><Card><b className="text-warning">{evidence.hint_levels.length}</b><p>Mức hỗ trợ đã dùng</p></Card><Card><b className="text-info">{evidence.selected_terms.join(', ')}</b><p>Khái niệm đã làm rõ</p></Card><Card><b className="text-success">{session.status === 'completed' ? '✓' : '—'}</b><p>Phiên hoàn tất</p></Card></div><div className="before-after"><Card><h3>Mã trước</h3><CodeBlock>{evidence.before_code}</CodeBlock></Card><Card><h3>Mã sau</h3><CodeBlock tone="success">{evidence.after_code}</CodeBlock></Card></div><Card className="evidence-timeline"><h3>Điều backend đã ghi nhận</h3><p>✓ Source version đã pin<br />✓ Thuật ngữ đã chọn: {evidence.selected_terms.join(', ')}<br />✓ Concept check đạt<br />✓ Submission đạt {evidence.passed_count}/{evidence.total_count}<br />✓ Evidence before/after đã tạo</p><Chip tone="success">Có thể tải lại trang để xem lại</Chip></Card><div className="lesson-actions"><Button tone="secondary" onClick={() => navigate('/demo/setup')}>Tạo phiên mới</Button><Button onClick={() => navigate('/demo/access')}>Quay về tài khoản demo</Button></div></LessonShell>
}
