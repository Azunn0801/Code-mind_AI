import { useEffect, useState } from 'react'
import { Banner, Button, Card, Chip, CodeBlock, EmptyState } from '../components/UI'
import { LessonShell } from '../components/Shell'
import { navigate } from '../components/navigation'

type LessonFrameProps = { mobile?: boolean }

const codeBefore = `from collections import deque

history = deque(maxlen=3)

def visit(page):
    history.append(page)
    return list(history)`

const codeAfter = `from collections import deque

history = deque(maxlen=3)

def visit(page):
    if not page:
        return list(history)
    history.append(page)
    return list(history)`

export function SetupPage({ initial = 'required' }: { initial?: string }) {
  const [committed, setCommitted] = useState(initial !== 'required')
  const [visible, setVisible] = useState(initial === 'visible')
  return <div className="setup-page"><header className="setup-header"><b>CodeMind</b><span className="lesson-chip">Bài học: deque</span><span>{committed ? visible ? '3 / 3' : '2 / 3' : '1 / 3'}</span></header><main><Card className="setup-card"><h1>Thiết lập trước khi học</h1><p>Hai quyết định dưới đây có mục đích khác nhau. Cam kết là điều kiện vào bài; quyền hiển thị cho giảng viên là lựa chọn riêng.</p><label className={`decision-row ${committed ? 'selected' : ''}`}><input type="checkbox" checked={committed} onChange={(event) => setCommitted(event.target.checked)} /><span><b>Tôi cam kết tự thực hiện bài học</b><small>AI chỉ gợi ý từng bước; bài nộp và phần giải thích là của tôi.</small></span><Chip tone="warning">Bắt buộc</Chip></label><label className={`decision-row ${visible ? 'selected' : ''}`}><input type="checkbox" role="switch" checked={visible} onChange={(event) => setVisible(event.target.checked)} /><span><b>Cho phép giảng viên xem quá trình làm bài</b><small>Bao gồm nguồn đã đọc, lần chạy kiểm thử, hỗ trợ đã dùng và bài nộp.</small></span><Chip tone="muted">Tùy chọn</Chip></label><Banner title={committed ? visible ? 'Sẵn sàng và có chia sẻ' : 'Đã cam kết' : 'Chưa thể bắt đầu'}>{committed ? visible ? 'Giảng viên có thể xem bằng chứng của phiên học này.' : 'Bạn có thể bắt đầu; quyền giảng viên vẫn đang tắt.' : 'Cam kết trung thực là bắt buộc. Quyền hiển thị là tùy chọn.'}</Banner><div className="action-row centered"><Button tone="secondary" onClick={() => navigate('/')}>Quay lại Home</Button><Button disabled={!committed} onClick={() => navigate('/demo/objective')}>Bắt đầu bài học</Button></div></Card></main></div>
}

export function ObjectivePage({ mobile = false }: LessonFrameProps) {
  if (mobile) return <LessonShell mobile step={1} status="Chưa bắt đầu"><section className="mobile-lesson-intro"><span className="eyebrow">BÀI HỌC DEQUE</span><h1>Hiểu deque bằng một lỗi có thật</h1><p>Bạn sẽ đọc nguồn, chạy mã, gặp một lỗi biên và tự sửa sau gợi ý.</p><Card><h3>Mục tiêu</h3><p>Dùng <b>deque(maxlen=3)</b> để lưu ba trang gần nhất và không thêm chuỗi rỗng.</p><h3>Những gì sẽ được lưu</h3><p>Chọn thuật ngữ · chạy kiểm thử · tự sửa mã · lưu ghi chú.</p><h3>Thời lượng</h3><p>Khoảng 3–4 phút cho bản demo.</p><Button onClick={() => navigate('/demo/source')}>Bắt đầu từ tài liệu</Button></Card></section></LessonShell>
  return <LessonShell step={1} status="Chưa bắt đầu"><div className="lesson-heading"><span>BƯỚC 1 / 6</span><h1>Hiểu deque và dùng maxlen để quản lý lịch sử gần nhất</h1><p>Kết thúc bài học, bạn giải thích được maxlen, áp dụng nó và tự xử lý một lỗi đầu vào.</p></div><div className="lesson-grid"><Card><h3>Mục tiêu có thể kiểm chứng</h3><h3>Tự cài đặt bộ nhớ ba trang gần nhất bằng collections.deque(maxlen=3).</h3>{[['Mốc 1', 'Đọc đúng đoạn tài liệu và làm rõ “maxlen” trong ngữ cảnh deque.'], ['Mốc 2', 'Chạy bộ kiểm thử, xác định một lỗi biên và tự sửa mã.'], ['Mốc 3', 'Lưu điều đã hiểu và chỉ chia sẻ tiến trình khi bạn cho phép.']].map(([title, copy]) => <Card key={title} className="milestone"><b>{title}</b><p>{copy}</p></Card>)}</Card><Card><h3>Phiên học này</h3><Card><code>12 phút tập trung</code><p>Một mục tiêu, một nguồn chính thức và một bài thực hành liên kết trực tiếp.</p></Card><Card><h3>Hỗ trợ theo điểm mắc</h3><p>Thiếu nền tảng thì quay về nguồn; áp dụng sai thì nhận câu hỏi gợi mở.</p></Card><Card><h3>Nguồn đã xác thực</h3><p>docs.python.org · Python 3.12</p></Card></Card></div><div className="lesson-actions"><Button onClick={() => navigate('/demo/source')}>Bắt đầu từ nguồn chính thức</Button></div></LessonShell>
}

export function SourcePage({ selected = false, mobile = false }: { selected?: boolean; mobile?: boolean }) {
  const [term, setTerm] = useState(selected)
  return <LessonShell mobile={mobile} step={2} status={term ? 'Đã chọn' : 'Đang đọc'}><div className="lesson-heading"><span>BƯỚC 2 / 6</span><h1>Đọc đúng phần về deque có giới hạn</h1><p>Tập trung vào maxlen: điều nó làm, điều nó không làm và cách áp dụng vào bài.</p></div><div className="source-layout"><Card className="source-document"><div className="source-meta"><Chip tone="success">Nguồn đã xác thực</Chip><span>docs.python.org · 3.12</span></div><h2>collections.deque(maxlen)</h2><p className="source-quote">Deque có thể đặt độ dài tối đa bằng maxlen. Khi đã đầy, thêm phần tử mới sẽ loại phần tử ở đầu đối diện.</p><button className={`term-button ${term ? 'selected' : ''}`} onClick={() => setTerm((current) => !current)}>maxlen</button><p>Chọn “maxlen” để xem ý nghĩa, giới hạn và ví dụ gắn với bài tập.</p></Card><Card className="term-panel"><h3>Điều cần làm rõ</h3>{term ? <><Chip>maxlen</Chip><h3>Giới hạn số phần tử</h3><p>maxlen chỉ giữ tối đa ba phần tử. Nó không tự xác thực page hay bỏ chuỗi rỗng trước khi append.</p><CodeBlock>{`history = deque(maxlen=3)
history.append(page)`}</CodeBlock></> : <p>Chưa chọn khái niệm nào.</p>}<small>Chỉ lưu những khái niệm bạn đã mở và xác nhận là hữu ích.</small></Card></div><div className="lesson-actions"><Button tone="secondary" onClick={() => navigate('/demo/objective')}>Quay lại</Button><Button disabled={!term} onClick={() => navigate('/demo/concept')}>Chọn “maxlen” để tiếp tục</Button></div></LessonShell>
}

export function ConceptPage({ initial = 'initial', mobile = false }: { initial?: string; mobile?: boolean }) {
  const correctRelation = 'kiểm tra page → trước append'
  const [relation, setRelation] = useState(initial === 'linked' ? correctRelation : '')
  const options = ['deque → maxlen=3', 'maxlen=3 → giới hạn số phần tử', correctRelation]
  return <LessonShell mobile={mobile} step={3} status={relation === correctRelation ? 'Đã nối' : 'Chưa hoàn thành'}><div className="lesson-heading"><span>BƯỚC 3 / 6</span><h1>Nối khái niệm với hành vi của chương trình</h1><p>Chọn quan hệ giải thích vì sao maxlen không thể tự loại chuỗi rỗng.</p></div><Card className="concept-card"><div className="concept-nodes"><Card><h3>deque</h3><p>Lưu phần tử theo thứ tự</p></Card><Card><h3>maxlen=3</h3><p>Giữ tối đa ba phần tử</p></Card><Card><h3>Kiểm tra đầu vào</h3><p>Loại chuỗi rỗng trước append</p></Card></div><h3>Quan hệ đúng cho bài này</h3><div className="choice-row">{options.map((option) => <button key={option} className={relation === option ? 'selected' : ''} onClick={() => setRelation(option)}>{option}</button>)}</div><p>Chọn quan hệ thứ ba để xác định nơi xử lý chuỗi rỗng.</p></Card><div className="lesson-actions"><Button tone="secondary" onClick={() => navigate('/demo/source')}>Quay lại thuật ngữ</Button><Button disabled={relation !== correctRelation} onClick={() => navigate('/demo/practice')}>Nối kiểm tra page trước append</Button></div></LessonShell>
}

export function PracticePage({ initial = 'ready', mobile = false }: { initial?: string; mobile?: boolean }) {
  const [state, setState] = useState(initial)
  useEffect(() => { if (state === 'loading') { const timer = window.setTimeout(() => setState('fail'), 1000); return () => window.clearTimeout(timer) } }, [state])
  const isLoading = state === 'loading'
  const fail = state === 'fail'
  return <LessonShell mobile={mobile} step={4} status={isLoading ? 'Đang chạy' : fail ? '4 / 5 đạt' : 'Chưa chạy'}><div className="lesson-heading"><span>BƯỚC 4 / 6</span><h1>Tự cài đặt lịch sử ba trang gần nhất</h1><p>Dùng deque(maxlen=3), nhưng chủ động bỏ qua chuỗi rỗng trước khi thêm vào lịch sử.</p></div><div className="practice-layout"><Card><span className="eyebrow">ĐỀ BÀI</span><h3>Lịch sử truy cập gần nhất</h3><p>Viết visit(page): bỏ qua chuỗi rỗng, giữ tối đa ba trang và trả về lịch sử hiện tại.</p><p><b>Nguồn liên quan</b><br />Python 3.12 · collections.deque(maxlen)</p></Card><Card className="editor-card"><div className="tabs"><button className="active">Mã nguồn</button><button>Bộ kiểm thử</button><button>Trợ giảng AI</button></div><CodeBlock>{codeBefore}</CodeBlock><p>Mã bạn đang viết sẽ không bị mất khi có lỗi.</p><Button onClick={() => setState('loading')} disabled={isLoading}>{isLoading ? 'Đang chạy kiểm thử…' : 'Chạy bộ kiểm thử'}</Button></Card><Card><span className="eyebrow">BỘ KIỂM THỬ</span>{isLoading ? <><h3>Đang chạy</h3><div className="progress"><i /></div><p>Đang cô lập môi trường và thực thi năm ca kiểm thử.</p></> : fail ? <><h3 className="text-warning">4 / 5 đạt</h3><p>✓ 4 ca đạt</p><p className="text-danger">× Chuỗi rỗng vẫn được thêm.</p><Button onClick={() => navigate('/demo/ai?state=question')}>Hỏi trợ giảng AI</Button></> : <><h3>0 / 5 đạt</h3><p>Năm ca đang chờ. Không có dữ liệu được ghi trước khi bạn bấm chạy.</p></>}</Card></div><div className="lesson-actions"><Button tone="secondary" onClick={() => navigate('/demo/concept')}>Quay lại khái niệm</Button>{fail && <Button onClick={() => navigate('/demo/ai?state=question')}>Mở hỗ trợ</Button>}</div></LessonShell>
}

const hintCopy = [
  'Khi page là chuỗi rỗng, dòng nào vẫn thay đổi history?',
  'maxlen chỉ giới hạn số phần tử. Hãy nhìn history.append(page): bước kiểm tra nên xuất hiện trước hay sau dòng này?',
  'Thêm một điều kiện bảo vệ: nếu page rỗng thì trả lại history hiện tại, rồi mới append khi đầu vào hợp lệ.',
]

export function AIPage({ initial = 'question', mobile = false }: { initial?: string; mobile?: boolean }) {
  const initialLevel = initial === 'hint2' ? 2 : initial === 'hint3' || initial === 'pass' ? 3 : initial === 'hint1' || initial === 'wrong' ? 1 : 0
  const [level, setLevel] = useState(initialLevel)
  const [passed, setPassed] = useState(initial === 'pass')
  return <LessonShell mobile={mobile} step={5} status={passed ? 'Đã nộp' : `Gợi ý ${level} / 3`}><div className="lesson-heading"><span>BƯỚC 5 / 6</span><h1>{passed ? 'Bạn đã tự sửa mã và đạt năm trên năm' : 'Xác định vì sao chuỗi rỗng vẫn được thêm'}</h1><p>{passed ? 'Mã trước/sau được giữ lại để chứng minh người học đã sửa lỗi sau hỗ trợ.' : 'Bộ kiểm thử đã chỉ ra hành vi sai; hãy đối chiếu với dòng đang thay đổi history.'}</p></div>{passed ? <div className="before-after"><Card className="danger-outline"><span className="text-danger">TRƯỚC</span><CodeBlock>{codeBefore}</CodeBlock><Banner tone="danger" compact title="Lỗi">Chuỗi rỗng vẫn được thêm.</Banner></Card><Card className="success-outline"><span className="text-success">SAU</span><CodeBlock>{codeAfter}</CodeBlock><Banner tone="success" compact title="Kết quả">5 / 5 ca kiểm thử đạt.</Banner><Chip tone="success">Tự sửa sau 3 mức hỗ trợ</Chip></Card></div> : <div className="ai-layout"><Card className="conversation"><div><b>Trợ giảng AI</b><p>{level ? 'maxlen chỉ giới hạn số phần tử. Hãy nhìn history.append(page): bước kiểm tra nên xuất hiện trước hay sau dòng này?' : 'Khi page là chuỗi rỗng, dòng nào vẫn thay đổi history?'}</p></div><div><b>Bạn</b><p>Mình nghĩ maxlen sẽ tự bỏ qua giá trị rỗng.</p></div>{level > 0 && hintCopy.slice(0, level).map((copy, index) => <div key={copy}><b className="text-info">Hỗ trợ mức {index + 1}</b><p>{copy}</p></div>)}</Card><Card><h3>Chọn phản hồi của bạn</h3><button className="hint-level active" onClick={() => setLevel((current) => Math.max(current, 1))}><b>Trước history.append(page)</b><small>Điều kiện phải xuất hiện trước khi thay đổi history.</small></button><button className="hint-level" onClick={() => setLevel((current) => Math.max(current, 1))}><b>Sau khi append</b><small>Thử đối chiếu với ca chuỗi rỗng.</small></button><button className="hint-level" onClick={() => navigate('/demo/source')}><b>Mình chưa chắc, cho xem lại nguồn</b><small>Lựa chọn và lần quay lại nguồn được lưu trong tiến trình học.</small></button>{level < 3 ? <Button onClick={() => setLevel((current) => Math.max(1, current + 1))}>Mở hỗ trợ mức {Math.max(1, level + 1)}</Button> : <Button onClick={() => setPassed(true)}>Tự sửa và chạy lại</Button>}</Card></div>}<div className="lesson-actions"><Button tone="secondary" onClick={() => navigate('/demo/practice?state=fail')}>Quay lại mã</Button>{passed && <Button onClick={() => navigate('/demo/evidence')}>Nộp bài và xem lại</Button>}</div></LessonShell>
}

export function EvidencePage({ mobile = false }: LessonFrameProps) {
  return <LessonShell mobile={mobile} step={6} status="Đã nộp"><div className="lesson-heading"><span>BƯỚC 6 / 6</span><h1>Quá trình tự sửa trong bài học</h1><p>Phần xem lại hiển thị nguồn, thay đổi mã, kiểm thử, mức hỗ trợ và ghi chú đã lưu.</p></div><div className="four-grid evidence-stats"><Card><b className="text-success">5 / 5</b><p>Ca kiểm thử đạt</p></Card><Card><b className="text-warning">3</b><p>Mức hỗ trợ đã dùng</p></Card><Card><b className="text-info">maxlen</b><p>Khái niệm đã làm rõ</p></Card><Card><b className="text-success">1</b><p>Ghi chú đã lưu</p></Card></div><div className="before-after"><Card><h3>Mã trước</h3><CodeBlock>{codeBefore}</CodeBlock></Card><Card><h3>Mã sau</h3><CodeBlock tone="success">{codeAfter}</CodeBlock></Card></div><Card className="evidence-timeline"><h3>Lịch sử học tập</h3><p>✓ Làm rõ “maxlen” từ Python 3.12<br />✓ Phân biệt giới hạn kích thước và kiểm tra đầu vào<br />✓ Phát hiện lỗi chuỗi rỗng bằng bộ kiểm thử<br />✓ Xem lại đúng dòng cần thay đổi<br />✓ Tự thêm điều kiện bảo vệ<br />✓ Nộp mã đạt 5/5</p><CodeBlock>{'“Kiểm tra đầu vào trước khi thay đổi cấu trúc dữ liệu. maxlen chỉ giới hạn kích thước, không xác thực giá trị.”'}</CodeBlock><Chip tone="success">Chia sẻ với giảng viên: đang bật</Chip></Card><div className="lesson-actions"><Button tone="secondary" onClick={() => navigate('/demo/ai?state=pass')}>Học lại từ đầu</Button><Button onClick={() => navigate('/student')}>Mở bài tiếp theo</Button></div></LessonShell>
}

export function ErrorPage({ state, mobile = false }: { state: string; mobile?: boolean }) {
  const copy: Record<string, [string, string, string, string]> = {
    source: ['Nguồn tạm thời không khả dụng', 'Không thể tải bản mới nhất. Dữ liệu đã nhập vẫn được giữ; bạn có thể dùng bản nguồn đã lưu.', 'Dùng bản đã lưu', '/demo/source'],
    quota: ['Đã dùng hết hạn mức AI hôm nay', 'Bạn vẫn có thể đọc nguồn, chạy kiểm thử và tự sửa mã. Hạn mức không khóa bài học.', 'Quay lại luyện tập', '/demo/practice'],
    submission: ['Không thể gửi bài lúc này', 'Mã vẫn được lưu trên thiết bị. Thử lại sẽ dùng cùng idempotency key để tránh tạo hai bài nộp.', 'Thử gửi lại', '/demo/practice?state=fail'],
    notes: ['Chưa có ghi chú nào', 'Ghi chú chỉ được tạo sau khi bạn xác định lỗi và ghi lại quyết định sửa.', 'Về bước hỗ trợ', '/demo/ai?state=hint1'],
  }
  const [title, body, action, path] = copy[state] ?? copy.source
  return <LessonShell mobile={mobile} step={state === 'notes' ? 6 : 4} status="Tình huống phục hồi"><EmptyState title={title} action={<><Button onClick={() => navigate(path)}>{action}</Button><Button tone="secondary" onClick={() => navigate('/demo/objective')}>Quay lại luồng</Button></>}>{body}</EmptyState></LessonShell>
}
