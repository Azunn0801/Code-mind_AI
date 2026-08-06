import { useState } from 'react'
import { Banner, Button, Card, Chip, CodeBlock, Field } from '../components/UI'
import { PublicHeader } from '../components/Shell'
import { navigate } from '../components/navigation'

const steps = [
  ['1', 'Đọc và làm rõ', 'Đọc đúng đoạn Python 3.12 và làm rõ “maxlen”.'],
  ['2', 'Chạy mã', 'Viết mã, chạy năm ca kiểm thử và thấy rõ lỗi chuỗi rỗng.'],
  ['3', 'Nhận hỗ trợ', 'Hệ thống xác định điểm mắc và hỗ trợ theo từng mức.'],
  ['4', 'Tự sửa', 'Tự sửa lên 5/5; mã trước–sau và ghi chú được lưu.'],
]

export function HomePage({ mobile = false }: { mobile?: boolean }) {
  const problems = mobile
    ? [['Học liệu thiếu cấu trúc', 'Khó biết đâu là phần thật sự cần hiểu.'], ['Bài tập đến trước khi hiểu', 'Người học dễ phải tìm AI bên ngoài để kịp nộp bài.']]
    : [['Học liệu thiếu cấu trúc', 'Nội dung dài và lan man khiến người học khó biết đâu là điều cần hiểu.'], ['Nguồn khó kiểm chứng', 'Kiến thức bị xào lại nhiều lớp, tách khỏi tài liệu chính thức và ngữ cảnh bài tập.'], ['Bài tập đến trước khi hiểu', 'Khi chưa có nền tảng mà vẫn phải nộp bài, tìm AI bên ngoài trở thành cách đối phó dễ hiểu.']]
  const evidence = mobile
    ? [['4 → 5 / 5', 'Kiểm thử trước và sau khi sửa.', 'text-success'], ['3 mức hỗ trợ', 'Lưu lại câu hỏi, vị trí cần xem và khung giả mã đã dùng.', 'text-warning'], ['1 ghi chú', 'Được lưu từ lỗi và hiển thị cho giảng viên.', 'text-success']]
    : [['1 thuật ngữ', 'Được chọn từ nguồn đã xác thực.', 'text-info'], ['4 → 5 / 5', 'Ca kiểm thử trước và sau khi sửa.', 'text-success'], ['3 mức hỗ trợ', 'Câu hỏi, vị trí cần xem và khung giả mã được mở dần theo nhu cầu.', 'text-warning'], ['1 ghi chú', 'Đúc kết từ lỗi; chỉ chia sẻ khi người học cho phép.', 'text-success']]
  return (
    <div className={`public-page home-page ${mobile ? 'home-page--mobile' : ''}`}>
      <PublicHeader />
      <section className="hero-section public-container">
        <div className="hero-copy">
          <span className="eyebrow">{mobile ? 'HỌC QUA THỰC HÀNH' : 'HỌC LẬP TRÌNH QUA THỰC HÀNH'}</span>
          <h1>Hiểu từ nguồn chuẩn.<br />Tự viết và sửa mã.</h1>
          <p>{mobile ? 'CodeMind chọn đúng phần cần học từ tài liệu chính thức, nối với thực hành và kiểm thử. AI chỉ hỗ trợ đúng chỗ bạn đang mắc.' : 'CodeMind biến tài liệu chính thức thành bài học ngắn, có mục tiêu rõ và nối thẳng với thực hành. Kết quả do bộ kiểm thử xác định; AI chỉ hỗ trợ đúng chỗ bạn đang mắc.'}</p>
          <div className="action-row">
            <Button onClick={() => navigate('/demo/setup')}>Trải nghiệm một bài học</Button>
            <Button tone="secondary" onClick={() => navigate('/integrity')}>Xem cách học đúng</Button>
          </div>
          <small>Demo dùng Python collections.deque · khoảng 3–4 phút</small>
        </div>
        {!mobile && <Card className="hero-flow">
          <h3>Một bài học, bốn bước rõ ràng</h3>
          {steps.map(([num, title, copy], index) => (
            <button key={num} onClick={() => navigate(['/demo/source', '/demo/practice', '/demo/ai', '/demo/evidence'][index])}>
              <span>{num}</span><div><b>{title}</b><small>{copy}</small></div>
            </button>
          ))}
        </Card>}
      </section>

      <section className="public-section public-section--raised public-container">
        <span className="eyebrow">VẤN ĐỀ CODEMIND GIẢI QUYẾT</span>
        <h2>{mobile ? 'Nội dung nhiều chưa chắc giúp người học hiểu' : 'Nội dung nhiều không đồng nghĩa với người học hiểu.'}</h2>
        <div className={mobile ? 'two-grid' : 'three-grid'}>
          {problems.map(([title, copy]) => <Card key={title}><h3>{title}</h3><p>{copy}</p></Card>)}
        </div>
        {!mobile && <div className="step-strip">{['Nguồn chuẩn', 'Làm rõ', 'Hiểu', 'Luyện tập', 'Hỗ trợ', 'Xem lại'].map((item, index) => <span key={item}><b>{index + 1}</b>{item}</span>)}</div>}
      </section>

      <section className="public-section public-container">
        <span className="eyebrow">{mobile ? 'DEMO CỤ THỂ' : 'MỘT TÌNH HUỐNG CỤ THỂ'}</span>
        <h2>{mobile ? 'Từ 4/5 đến tự sửa 5/5' : 'Từ hiểu đúng nguồn đến tự sửa đạt 5/5'}</h2>
        <p>{mobile ? 'Đề bài, lỗi và hỗ trợ được nối liền để người học tự tìm đúng chỗ cần sửa.' : 'Một bài học ngắn với deque(maxlen=3): đọc đúng phần cần thiết, áp dụng ngay và kiểm chứng bằng bộ kiểm thử.'}</p>
        {mobile ? <Card className="mobile-demo-card"><div><span className="eyebrow">Đề bài</span><p>Lưu tối đa ba trang gần nhất. Không thêm chuỗi rỗng vào lịch sử.</p></div><div><span className="eyebrow">Mã</span><CodeBlock>{`main.py\ndef visit(page):\n  history.append(page)`}</CodeBlock><p><b className="text-danger">Ca không đạt</b><br />Chuỗi rỗng vẫn được thêm.</p></div><div className="message-stack"><p><b>Hỗ trợ theo điểm mắc</b><br />Từ câu hỏi đến khung giả mã, mở dần theo nhu cầu.</p><p className="text-success"><b>Sau gợi ý</b><br />Tự thêm điều kiện bảo vệ · 5 / 5.</p></div></Card> : <div className="demo-triple"><Card><h3>Đề bài</h3><p>Lưu tối đa ba trang gần nhất. Không thêm chuỗi rỗng vào lịch sử.</p><Chip tone="warning">Ca không đạt</Chip><p><code>visit('')</code> vẫn được thêm.</p></Card><Card><h3>Mã</h3><CodeBlock>{`main.py\ndef visit(page):\n  history.append(page)`}</CodeBlock><Banner tone="success" compact title="Sau khi xác định điểm mắc">Người học thêm điều kiện bảo vệ, chạy lại và đạt 5/5.</Banner></Card><Card><h3>Hỗ trợ</h3><div className="message-stack"><p><b>Hỗ trợ đúng điểm mắc</b><br />“Hãy kiểm tra dữ liệu trước khi thay đổi history.”</p><p><b>Hỗ trợ mức 1</b><br />Điều kiện nào cho biết đầu vào không hợp lệ?</p><p className="text-success"><b>Kết quả</b><br />Tự sửa mã · 5 / 5 · 1 ghi chú đã lưu</p></div></Card></div>}
      </section>

      <section className="public-section public-section--raised public-container">
        <span className="eyebrow">NHỮNG GÌ ĐƯỢC GHI LẠI</span>
        <h2>Có thể xem lại toàn bộ quá trình tự sửa</h2>
        <div className={mobile ? 'three-grid' : 'four-grid'}>
          {evidence.map(([title, copy, tone]) => <Card key={title}><b className={tone}>{title}</b><p>{copy}</p></Card>)}
        </div>
      </section>

      <section className="public-container final-cta">
        <div><h2>Thử một bài học được thiết kế để hiểu</h2><p>Đọc đúng nguồn, nắm khái niệm, áp dụng, kiểm thử và tự sửa trong một luồng ngắn.</p></div>
        <Button onClick={() => navigate('/demo/setup')}>Trải nghiệm bài học deque</Button>
      </section>
      <PublicFooter />
    </div>
  )
}

function PublicFooter() {
  return <footer className="public-footer"><span>Quyền riêng tư</span><span>CodeMind học với AI</span><span>Minh bạch quá trình học</span><span>Điều khoản sử dụng</span></footer>
}

export function AuthPage({ mode, state }: { mode: 'login' | 'register'; state?: string }) {
  const [accepted, setAccepted] = useState(state === 'ready')
  const [error, setError] = useState(state === 'error')
  const isLogin = mode === 'login'
  return (
    <div className="public-page"><PublicHeader />
      <main className="auth-layout public-container">
        <section><h1>{isLogin ? 'Tiếp tục bài học đang dở.' : 'Tạo tài khoản học có trách nhiệm.'}</h1><p>Tài liệu, kết quả kiểm thử, gợi ý và ghi chú gần nhất đều được giữ lại.</p>
          <Card><h3>Trước khi vào ứng dụng</h3><p>✓ Một phiên học hoạt động tại một thời điểm.</p><p>✓ Trợ giảng AI chỉ gợi ý; người học tự giải thích.</p><p>✓ URL, phiên bản và trạng thái nguồn được giữ lại.</p><p>✓ Cam kết và quyền giảng viên là hai quyết định riêng.</p></Card>
        </section>
        <Card className="auth-card"><h2>{isLogin ? 'Đăng nhập' : 'Tạo tài khoản'}</h2><p>Dùng tài khoản học tập của bạn.</p>
          <Field label="Email" value="student@codemind.ai" />
          <Field label="Mật khẩu" value="••••••••" type="password" />
          {!isLogin && <label className="consent-inline"><input type="checkbox" checked={accepted} onChange={(e) => setAccepted(e.target.checked)} /><span><b>Tôi đồng ý với cam kết học tập</b><small>AI chỉ gợi ý; bài nộp và phần giải thích là của tôi.</small></span></label>}
          {error && <Banner tone="danger" compact title="Không thể đăng nhập">Kiểm tra lại email hoặc mật khẩu rồi thử lại.</Banner>}
          <Button disabled={!isLogin && !accepted} onClick={() => isLogin ? navigate('/student') : navigate('/demo/setup')}>{isLogin ? 'Đăng nhập và tiếp tục học' : 'Tạo tài khoản'}</Button>
          {isLogin && <Button tone="secondary" onClick={() => setError(!error)}>Xem trạng thái lỗi</Button>}
          <p className="form-foot">{isLogin ? 'Chưa có tài khoản?' : 'Đã có tài khoản?'} <button className="text-link" onClick={() => navigate(isLogin ? '/register' : '/login')}>{isLogin ? 'Tạo tài khoản' : 'Đăng nhập'}</button></p>
        </Card>
      </main><PublicFooter />
    </div>
  )
}

export function PricingPage() {
  const plans = [
    ['Miễn phí', 'Dành cho người muốn kiểm tra phương pháp học.', ['Đọc nguồn chính thức và bảng thuật ngữ', 'Một bài học mẫu có kiểm thử', 'Ghi chú học tập cơ bản'], 'Trải nghiệm bài học'],
    ['Pro Student', 'Dành cho sinh viên học thường xuyên.', ['Tài liệu → luyện tập → xem lại', 'Nhiều lượt dùng trợ giảng AI', 'Lịch ôn và ghi chú từ lỗi'], 'Tạo tài khoản'],
    ['Trường học', 'Dành cho lớp học và thử nghiệm có kiểm soát.', ['Tạo bài tập và ca kiểm thử', 'Chỉ chia sẻ dữ liệu khi người học đồng ý', 'Phản hồi và can thiệp của giảng viên'], 'Xem giải pháp trường học'],
  ]
  return <div className="public-page"><PublicHeader /><main className="public-container page-pad"><h1>Học thử trước khi chọn gói.</h1><p>Xem rõ quyền lợi và hạn mức của từng gói. Bạn vẫn có thể học thử trước khi quyết định.</p><Banner title="Hạn mức hiển thị trước khi dùng">Khi AI tạm hết hạn mức, người học vẫn đọc nguồn và sửa mã.</Banner><div className="pricing-grid">{plans.map(([title, copy, items, action], index) => <Card key={String(title)} className={index === 1 ? 'plan plan--featured' : 'plan'}><h3>{title}</h3><p>{copy}</p><ul>{(items as string[]).map(item => <li key={item}>✓ {item}</li>)}</ul>{index === 1 && <Chip>Đành cho học cá nhân</Chip>}<Button tone={index === 1 ? 'primary' : 'secondary'} onClick={() => navigate(index === 2 ? '/campus' : index === 1 ? '/register' : '/demo/setup')}>{action}</Button></Card>)}</div><Card className="principles"><h3>Nguyên tắc sử dụng hợp lý</h3><div className="three-grid"><p><b className="text-info">Hết hạn mức AI</b><br />Người học vẫn đọc nguồn, chạy kiểm thử và tự sửa mã.</p><p><b className="text-info">Không bán dữ liệu</b><br />Nội dung trò chuyện và dữ liệu học tập không được bán cho nhà quảng cáo.</p><p><b className="text-info">Không ép mua gói</b><br />Demo và Trung tâm trợ giúp luôn truy cập được.</p></div></Card></main><PublicFooter /></div>
}

export function CampusPage() {
  return <div className="public-page"><PublicHeader /><main className="public-container page-pad"><span className="eyebrow">CODEMIND CAMPUS</span><h1>Quan sát quá trình học, không chỉ điểm cuối.</h1><p>Giảng viên chỉ xem dữ liệu mà người học đã chủ động chia sẻ.</p><div className="three-grid"><Card><h3>Tạo bài từ nguồn chính thức</h3><p>Khóa phiên bản tài liệu, thuật ngữ, ca kiểm thử và tiêu chí phản hồi.</p></Card><Card><h3>Phản hồi có căn cứ</h3><p>Xem mã trước/sau, số lần chạy kiểm thử và mức gợi ý đã dùng.</p></Card><Card><h3>Quyền hiển thị rõ ràng</h3><p>Cam kết học tập và quyền giảng viên luôn là hai lựa chọn tách biệt.</p></Card></div><Banner title="Dữ liệu có mục đích">Không có xếp hạng tính cách hay theo dõi bí mật.</Banner><div className="action-row"><Button onClick={() => navigate('/teacher')}>Mở bản Campus</Button><Button tone="secondary" onClick={() => navigate('/contact')}>Liên hệ thử nghiệm</Button></div></main><PublicFooter /></div>
}

const legalCopy: Record<string, [string, string, string[]]> = {
  about: ['Về CodeMind AI', 'Một môi trường học lập trình đặt bằng chứng và quyền tự quyết của người học ở trung tâm.', ['Học từ nguồn có phiên bản', 'AI không cung cấp lời giải hoàn chỉnh', 'Mọi gợi ý và thay đổi đều có dấu vết']],
  privacy: ['Quyền riêng tư', 'Thu thập tối thiểu và hiển thị rõ mục đích của từng loại dữ liệu.', ['Dữ liệu tài khoản và consent', 'Tiến trình, mã và gợi ý theo retention', 'Quyền truy cập, xuất và xóa dữ liệu']],
  terms: ['Điều khoản sử dụng', 'Quy định phạm vi sử dụng CodeMind cho học tập, thử nghiệm và Campus.', ['Không lạm dụng code runner', 'Không chia sẻ tài khoản', 'Tôn trọng quyền nguồn tài liệu']],
  ai: ['Chính sách học với AI', 'AI đặt câu hỏi, gợi ý theo tầng và viện dẫn nguồn; không làm bài thay người học.', ['Từ chối đáp án hoàn chỉnh', 'Ba mức gợi ý có thứ tự', 'Citations gắn với source version']],
  integrity: ['Trung thực học tập', 'Mục tiêu là chứng minh người học đã tự đọc, thử, sai và sửa.', ['Cam kết trước khi học', 'Mã trước/sau và test evidence', 'Quyền chia sẻ với giảng viên là tùy chọn']],
}

export function LegalPage({ kind }: { kind: keyof typeof legalCopy }) {
  const [title, intro, sections] = legalCopy[kind]
  return <div className="public-page"><PublicHeader /><main className="public-container legal-page page-pad"><h1>{title}</h1><p>{intro}</p><nav className="legal-toc">{sections.map((item, index) => <a key={item} href={`#section-${index}`}>{index + 1}. {item}</a>)}</nav>{sections.map((item, index) => <Card key={item}><h2 id={`section-${index}`}>{item}</h2><p>CodeMind ghi lại mục đích, phiên bản và thời điểm của quyết định liên quan. Quyền truy cập được kiểm tra theo vai trò và consent; thay đổi quan trọng có audit log.</p><p>Trong MVP, dữ liệu chỉ được dùng để cung cấp bài học, phục hồi tiến trình và tạo bằng chứng học tập có thể giải thích.</p></Card>)}</main><PublicFooter /></div>
}

export function HelpPage({ article = false, offline = false }: { article?: boolean; offline?: boolean }) {
  if (article) return <div className="public-page"><PublicHeader /><main className="public-container page-pad help-article"><span className="eyebrow">ĐỘ TIN CẬY NGUỒN</span><h1>Khi nguồn chính thức tạm thời không khả dụng</h1>{offline && <Banner tone="warning" title="Đang dùng bản nguồn đã lưu">Tiến trình và thuật ngữ bạn đã chọn vẫn được giữ nguyên.</Banner>}<Card><h2>CodeMind pin phiên bản như thế nào?</h2><p>Mỗi bài học lưu URL chuẩn, nhãn phiên bản, checksum và bản snapshot đã kiểm duyệt. Khi trang ngoài lỗi, hệ thống không tự thay nội dung bằng nguồn khác.</p></Card><Card><h2>Bạn có thể làm gì?</h2><p>Thử tải lại nguồn mới nhất hoặc tiếp tục bằng bản đã lưu. Cả hai lựa chọn đều được ghi vào dấu vết học tập.</p><Button onClick={() => navigate('/demo/error?state=source')}>Mở tình huống thử nghiệm</Button></Card></main><PublicFooter /></div>
  return <div className="public-page"><PublicHeader /><main className="public-container page-pad"><h1>Trung tâm trợ giúp</h1><p>Tìm câu trả lời theo đúng phần bạn đang làm.</p><div className="three-grid"><Card><h3>Tài khoản</h3><p>Đăng nhập, consent và phiên thiết bị.</p></Card><Card><h3>Nguồn và bài học</h3><p>Phiên bản, trạng thái nguồn và phục hồi.</p><Button tone="secondary" onClick={() => navigate('/help/source-reliability')}>Xem bài viết</Button></Card><Card><h3>AI và hạn mức</h3><p>Thang gợi ý, quota và chính sách không làm hộ.</p></Card></div></main><PublicFooter /></div>
}

export function ContactPage({ submitted = false }: { submitted?: boolean }) {
  const [sent, setSent] = useState(submitted)
  return <div className="public-page"><PublicHeader /><main className="public-container page-pad"><h1>Liên hệ đúng ngữ cảnh</h1><p>Chọn mục đích, gửi bối cảnh cần thiết và không gửi mật khẩu hay dữ liệu nhạy cảm.</p><div className="three-grid"><Card><h3>Hỗ trợ</h3><p>Tài khoản, nguồn, hạn mức hoặc thiết bị.</p></Card><Card><h3>Trường học</h3><p>Thử nghiệm, SSO, quyền giảng viên và quản lý nguồn.</p></Card><Card><h3>Nghiên cứu</h3><p>Học với AI, đọc tài liệu và trung thực học tập.</p></Card></div><Card className="contact-form"><h2>Gửi yêu cầu</h2>{sent ? <Banner tone="success" title="Đã gửi yêu cầu">Mã theo dõi CM-204. Chúng tôi sẽ phản hồi theo email đã cung cấp.</Banner> : <><Field label="Chủ đề" value="Nguồn không tải" /><Field label="Email" value="student@codemind.ai" /><label className="field"><span>Bối cảnh</span><textarea defaultValue="Bước gặp lỗi: Tài liệu → Luyện tập; đang dùng Python 3.13; đã thử tải lại hai lần." /></label><Button onClick={() => setSent(true)}>Gửi yêu cầu</Button></>}<Button tone="secondary" onClick={() => navigate('/help')}>Mở Trung tâm trợ giúp</Button></Card></main><PublicFooter /></div>
}

export function CheckoutPage() {
  return <div className="public-page"><PublicHeader /><main className="public-container checkout-layout page-pad"><section><h1>Hoàn tất gói Pro Student</h1><p>Xem lại quyền lợi, giá và điều khoản trước khi thanh toán.</p><Card><h3>Pro Student</h3><p>79.000đ / tháng</p><p>✓ Nhiều lượt gợi ý hơn</p><p>✓ Lịch ôn và ghi chú</p><p>✓ Quyền hiển thị giảng viên tùy chọn</p></Card></section><Card className="checkout-card"><h2>Thông tin thanh toán</h2><Field label="Tên chủ thẻ" value="Nguyễn Minh Anh" /><Field label="Số thẻ" value="4242 4242 4242 4242" /><div className="two-grid"><Field label="MM/YY" value="08/28" /><Field label="CVC" value="123" /></div><Button onClick={() => navigate('/payment/success')}>Thanh toán 79.000đ</Button><Button tone="secondary" onClick={() => navigate('/payment/failed')}>Mô phỏng thất bại</Button></Card></main><PublicFooter /></div>
}

export function PaymentPage({ success }: { success: boolean }) {
  return <div className="public-page"><PublicHeader /><main className="public-container centered-page"><Card className="payment-card"><span className={`payment-icon ${success ? 'success' : 'danger'}`}>{success ? '✓' : '!'}</span><h1>{success ? 'Thanh toán thành công' : 'Thanh toán chưa hoàn tất'}</h1><p>{success ? 'Gói Pro Student đã sẵn sàng. Tiến trình học của bạn không thay đổi.' : 'Không có khoản phí nào được ghi nhận. Bạn có thể thử lại hoặc tiếp tục gói miễn phí.'}</p><Button onClick={() => navigate(success ? '/student' : '/checkout')}>{success ? 'Về trang học' : 'Thử lại thanh toán'}</Button><Button tone="secondary" onClick={() => navigate('/pricing')}>Xem bảng giá</Button></Card></main><PublicFooter /></div>
}
