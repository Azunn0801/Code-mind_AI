import { useEffect, useState, type ReactNode } from 'react'
import { AppShell } from '../components/Shell'
import { navigate, studentNav } from '../components/navigation'
import { Banner, Button, Card, Chip, CodeBlock, EmptyState, Stat } from '../components/UI'

const before = `item = queue[0]
queue = queue[1:]
return item`

const after = `if not queue:
    return None
return queue.popleft()`

const sourceUrl = 'https://docs.python.org/3/library/collections.html'

function SourceLink() {
  return <a className="source-link" href={sourceUrl} target="_blank" rel="noreferrer">Mở tài liệu Python 3.13 ↗</a>
}

function StudentShell({ active, step, children }: { active: string; step: number; children: ReactNode }) {
  const badge = active === '/student' ? 'Bài học: deque' : active.includes('docs') ? 'Tài liệu chính thức' : active.includes('notes') ? 'Ghi chú học tập' : 'Luyện tập: deque'
  return <AppShell kind="student" badge={badge} status={`Bước ${step} / 5`} nav={studentNav} active={active}>{children}</AppShell>
}

export function StudentHome() {
  return <StudentShell active="/student" step={2}>
    <div className="page-heading"><h1>Hôm nay, bạn sẽ làm gì?</h1><p>Chọn đúng bước tiếp theo: đọc nguồn, luyện tập hoặc xem lại điều bạn đã tự sửa.</p></div>
    <div className="student-home-grid">
      <Card className="featured-card"><span className="eyebrow">BÀI HỌC TIẾP THEO</span><h2>Hiểu deque qua một lỗi dễ gặp</h2><p>Đọc một đoạn tài liệu ngắn, hiểu “thread-safe” bằng ví dụ, rồi tự sửa mã sau từng gợi ý.</p><p>3–4 phút &nbsp;&nbsp; 0 / 5 bước</p><div className="action-row"><Button onClick={() => navigate('/student/docs')}>Bắt đầu bài học</Button><Button tone="secondary" onClick={() => navigate('/student/notes')}>Xem ghi chú</Button></div></Card>
      <Card><h3>Kết quả gần nhất</h3><p>Giảng viên chỉ xem khi bạn đã bật quyền hiển thị.</p><strong className="metric-inline text-warning">4 / 5</strong><small>lần kiểm tra đạt</small><strong className="metric-inline">2</strong><small>gợi ý đã dùng</small><strong className="metric-inline text-success">1</strong><small>ghi chú đã lưu</small></Card>
      <Card><h3>Ôn lại hôm nay</h3><p><b>thread-safe</b> nghĩa là thao tác vẫn an toàn khi nhiều luồng cùng truy cập.</p><Button tone="secondary" onClick={() => navigate('/student/docs?state=selected')}>Xem lại giải thích</Button></Card>
      <Card><h3>Cam kết học tập</h3><p>AI đặt câu hỏi; bạn viết, chạy và tự giải thích mã.</p><Chip tone="success">Đang áp dụng</Chip></Card>
    </div>
  </StudentShell>
}

export function StudentDocs({ selected = false }: { selected?: boolean }) {
  const [term, setTerm] = useState(selected)
  return <StudentShell active="/student/docs" step={1}>
    <div className="page-heading"><h1>Đọc nguồn trước khi sửa mã</h1><p>Trước khi viết code, hãy làm rõ một thuật ngữ bạn chưa chắc. Ở bước này, bạn chỉ cần hiểu một ý và liên hệ nó với bài tập.</p></div>
    <Banner tone="success" title="Nguồn đã xác thực">Python 3.13 · URL và phiên bản được lưu cùng bài học.</Banner>
    <div className="content-sidebar-grid">
      <Card><span className="eyebrow">ĐOẠN TÀI LIỆU</span><h2>collections.deque</h2><p>Deque là một hàng đợi hai đầu. Bạn có thể thêm hoặc lấy phần tử ở đầu và cuối với thời gian gần như không đổi.</p><CodeBlock>{`“Deques support thread-safe, memory-efficient appends and pops from either side.”`}</CodeBlock><button className={`term-button ${term ? 'selected' : ''}`} onClick={() => setTerm((current) => !current)}>{term ? 'Ẩn giải thích' : 'Xem giải thích “thread-safe”'}</button><small>Đừng cố học thuộc câu tiếng Anh. Hãy xem nghĩa đơn giản rồi thử dùng nó để giải thích lần kiểm tra.</small></Card>
      <div><Card className="term-explainer"><span className="eyebrow">{term ? 'BẠN ĐANG XEM' : 'BƯỚC 1 / 5'}</span><h3>{term ? 'thread-safe nghĩa là gì?' : 'Chọn một thuật ngữ để bắt đầu'}</h3>{term ? <><Chip>thread-safe</Chip><p>“Thread-safe” nghĩa là nhiều luồng có thể cùng dùng thao tác mà không làm hỏng trạng thái của hàng đợi.</p><p><b>Trong bài này:</b> append và pop của deque được thiết kế để dùng an toàn ở từng thao tác. Nếu bạn làm nhiều bước liên tiếp — kiểm tra rồi mới thay đổi dữ liệu — hãy bảo vệ cả chuỗi bước đó.</p><Banner tone="info" compact title="Liên hệ với bài tập">Hãy để ý xem lần kiểm tra có kiểm tra dữ liệu đầu vào trước khi append hay chưa.</Banner></> : <p>Bấm “Xem giải thích” ở đoạn tài liệu. Sau đó, hãy tự nói lại ý nghĩa bằng một câu của bạn.</p>}</Card><Card><span className="eyebrow">NGUỒN CHÍNH THỨC</span><h3>Python 3.13 · collections.deque</h3><SourceLink /><small>Trang tài liệu chính thức của Python.</small></Card></div>
    </div>
    {term && <Banner tone="success" title="Bạn đã làm rõ thuật ngữ">“thread-safe” được gắn với Python 3.13 và sẽ xuất hiện trong ghi chú học tập.</Banner>}
    <div className="page-actions"><Button disabled={!term} onClick={() => navigate('/student/concept')}>Tôi đã hiểu, chuyển sang kiểm tra</Button></div>
  </StudentShell>
}

export function StudentConcept({ state = 'initial' }: { state?: string }) {
  const [answer, setAnswer] = useState(state === 'wrong' ? 'size' : state === 'correct' ? 'ops' : '')
  const checked = Boolean(answer)
  const correct = answer === 'ops'
  return <StudentShell active="/student/concept" step={2}>
    <div className="page-heading"><h1>Kiểm tra mình đã hiểu</h1><p>Chọn câu giải thích đúng trước khi viết code. Không cần nhớ công thức; hãy nhìn vào hành vi của deque.</p></div>
    {checked && <Banner tone={correct ? 'success' : 'danger'} title={correct ? 'Đúng — bạn đã nối được ý chính' : 'Chưa đúng — thử phân biệt “nhanh” và “số lượng”'}>{correct ? 'append và pop ở hai đầu thường chạy gần O(1), nghĩa là thời gian xử lý gần như không đổi khi hàng đợi lớn hơn.' : 'O(1) nói về thời gian thực hiện thao tác, không có nghĩa deque chỉ chứa một phần tử.'}</Banner>}
    <Card className="quiz-card"><span className="eyebrow">CÂU 1 / 1</span><h2>Điều gì làm append và pop ở hai đầu deque nhanh?</h2><div className="answer-list"><button className={answer === 'ops' ? 'selected' : ''} onClick={() => setAnswer('ops')}><b>Deque xử lý thêm và lấy phần tử ở hai đầu gần như trong cùng một khoảng thời gian</b><small>Đây là ý nghĩa thực tế của “gần O(1)” trong bài.</small></button><button className={answer === 'size' ? 'selected' : ''} onClick={() => setAnswer('size')}><b>O(1) nghĩa là deque luôn chỉ có một phần tử</b><small>Nhầm giữa thời gian xử lý và số lượng phần tử.</small></button><button className={answer === 'thread' ? 'selected' : ''} onClick={() => setAnswer('thread')}><b>Thread-safe nghĩa là mọi chương trình đều chạy song song</b><small>Thread-safe chỉ nói về việc bảo vệ trạng thái khi nhiều luồng cùng truy cập.</small></button></div><div className="action-row"><Button tone="secondary" onClick={() => navigate('/student/docs')}>Đọc lại thuật ngữ</Button><Button disabled={!correct} onClick={() => navigate('/student/practice')}>Tôi đã hiểu, bắt đầu luyện tập</Button></div></Card>
  </StudentShell>
}

export function StudentPractice({ initial = 'idle' }: { initial?: string }) {
  const [state, setState] = useState(initial)
  useEffect(() => { if (state === 'loading') { const id = setTimeout(() => setState('fail'), 900); return () => clearTimeout(id) } }, [state])
  const result = state === 'pass' ? ['5 / 5 đạt', 'success'] : state === 'fail' || state === 'hint' ? ['4 / 5 đạt', 'warning'] : ['Chưa chạy', 'muted']
  return <StudentShell active="/student/practice" step={3}>
    <div className="page-heading"><h1>Luyện tập: tự sửa một lỗi</h1><p>Đọc đề bài, viết code, chạy từng lần kiểm tra rồi sửa đúng dòng gây lỗi.</p></div>
    <Banner title={state === 'loading' ? 'Đang chạy kiểm tra' : state === 'pass' ? 'Bạn đã tự sửa thành công' : 'Sẵn sàng chạy'}>{state === 'pass' ? 'Năm lần kiểm tra đều đạt; mã trước và sau đã được ghi lại.' : 'Bạn sẽ thấy kết quả của từng lần kiểm tra. Chưa có dữ liệu nào được ghi trước khi bấm chạy.'}</Banner>
    <div className="practice-layout student-practice"><Card><span className="eyebrow">ĐỀ BÀI</span><h3>Lấy phần tử đầu và cập nhật chính deque</h3><p>Viết hàm <code>consume(queue)</code> trả về phần tử đầu. Nếu hàng đợi rỗng, trả về <code>None</code>.</p><p>✓ Hàng đợi rỗng → None<br />✓ Trả về phần tử đầu<br />✓ Cập nhật đúng hàng đợi ban đầu<br />✓ Không lấy đáp án từ AI</p><CodeBlock>{`Nguồn
Python 3.13 · collections.deque`}</CodeBlock></Card><Card className="editor-card"><div className="tabs"><button className="active">Mã của bạn</button><button>Kiểm tra</button><button>Trợ giảng AI</button></div><CodeBlock>{state === 'pass' ? after : before}</CodeBlock><p>Mã bạn đang viết sẽ không bị mất khi có lỗi.</p><Button disabled={state === 'loading'} onClick={() => setState('loading')}>{state === 'loading' ? 'Đang chạy…' : 'Chạy 5 lần kiểm tra'}</Button></Card><Card><span className="eyebrow">KẾT QUẢ</span><h3 className={`text-${result[1]}`}>{result[0]}</h3>{state === 'loading' ? <div className="progress"><i /></div> : state === 'idle' ? <p>Năm lần kiểm tra đang chờ. Bấm “Chạy 5 lần kiểm tra” để bắt đầu.</p> : state === 'pass' ? <><p>✓ Hàng đợi rỗng</p><p>✓ Trả về phần tử đầu</p><p>✓ Cập nhật đúng hàng đợi</p><Button onClick={() => navigate('/student/review')}>Xem bằng chứng</Button></> : <><p>✓ 4 lần kiểm tra đã đạt</p><p className="text-danger">× Hàm tạo list mới thay vì cập nhật hàng đợi ban đầu.</p><Button onClick={() => setState('hint')}>Mở gợi ý đầu tiên</Button>{state === 'hint' && <Banner title="Gợi ý đầu tiên">Phép cắt <code>queue[1:]</code> tạo một list mới. Phương thức nào thay đổi chính deque?</Banner>}<Button onClick={() => setState('pass')}>Tôi đã sửa, chạy lại</Button></>}</Card></div>
  </StudentShell>
}

export function StudentReview() {
  return <StudentShell active="/student/review" step={4}><div className="page-heading"><h1>Xem lại lần tự sửa</h1><p>Mã trước và sau, các lần kiểm tra và gợi ý được đặt cạnh nhau để bạn tự giải thích tiến bộ.</p></div><Banner tone="success" title="Đạt sau khi tự sửa">5 / 5 lần kiểm tra · 2 gợi ý · nguồn Python 3.13.</Banner><div className="before-after"><Card className="danger-outline"><span className="text-danger">TRƯỚC</span><CodeBlock>{before}</CodeBlock><p>Gán <code>queue = queue[1:]</code> tạo list mới; hàng đợi ban đầu không đổi.</p></Card><Card className="success-outline"><span className="text-success">SAU</span><CodeBlock>{after}</CodeBlock><p>Dùng <code>popleft()</code> để lấy phần tử và cập nhật chính deque.</p></Card></div><div className="three-grid"><Stat value="4 → 5/5" label="Lần kiểm tra" tone="success" /><Stat value="2" label="Gợi ý đã dùng" tone="warning" /><Stat value="1" label="Quyết định sửa" tone="info" /></div><div className="page-actions"><Button onClick={() => navigate('/student/notes')}>Lưu thành ghi chú</Button></div></StudentShell>
}

export function StudentNotes({ empty = false }: { empty?: boolean }) {
  const [isEmpty, setEmpty] = useState(empty)
  if (isEmpty) return <StudentShell active="/student/notes" step={5}><EmptyState title="Chưa có ghi chú học tập" action={<Button onClick={() => setEmpty(false)}>Tạo từ lần tự sửa gần nhất</Button>}>Sau khi xác định lỗi và tự sửa, bạn có thể lưu lại điều đã học để ôn đúng thời điểm.</EmptyState></StudentShell>
  return <StudentShell active="/student/notes" step={5}><div className="page-heading"><h1>Ghi chú học tập</h1><p>Lỗi, thuật ngữ và quyết định sửa mã được giữ lại để bạn ôn lại đúng lúc.</p></div><Banner tone="success" title="Đã lưu ghi chú">Ghi chú từ bài deque đã được thêm vào lịch ôn ngày mai.</Banner><div className="content-sidebar-grid"><Card><span className="eyebrow">THAY ĐỔI TRẠNG THÁI · DEQUE</span><h2>Cập nhật hàng đợi ban đầu, không chỉ đổi một biến tạm</h2><p>Khi viết <code>queue = queue[1:]</code>, bạn tạo một list mới và không cập nhật hàng đợi ban đầu. Với deque, <code>popleft()</code> vừa lấy phần tử đầu vừa thay đổi đúng đối tượng cần lưu.</p><div className="before-after compact"><CodeBlock>{before}</CodeBlock><CodeBlock tone="success">{after}</CodeBlock></div><CodeBlock>{`Nguồn: Python 3.13 · collections.deque
Tạo từ: lỗi thay đổi trạng thái · 1 gợi ý · 5/5 lần kiểm tra`}</CodeBlock></Card><Card><h3>Lịch ôn</h3><h2 className="text-info">Ngày mai · 09:00</h2><p>Câu hỏi ôn: phương thức nào vừa lấy phần tử trái vừa cập nhật deque?</p><Chip>deque</Chip> <Chip>thay đổi trạng thái</Chip><Button onClick={() => navigate('/student')}>Về trang Hôm nay</Button><Button tone="secondary" onClick={() => setEmpty(true)}>Xem trạng thái trống</Button></Card></div></StudentShell>
}
