"""Generate the CodeMind Round 3 detailed proposal PDF.

This source intentionally keeps unverified submission fields as placeholders instead
of inventing a public URL, team roster, pilot result, or production credential.
Run from the MVP root with the bundled workspace Python:

  python docs/generate_round3_proposal.py
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "deliverables"
OUT_PATH = OUT_DIR / "[KHOINGUYEN - VONG 3] - CodeMind.pdf"

NAVY = HexColor("#0B1F3A")
BLUE = HexColor("#1D4ED8")
TEAL = HexColor("#0F766E")
MINT = HexColor("#E6FFFB")
SKY = HexColor("#EFF6FF")
SLATE = HexColor("#334155")
MUTED = HexColor("#64748B")
LINE = HexColor("#CBD5E1")
PALE = HexColor("#F8FAFC")
AMBER = HexColor("#FFF7ED")
AMBER_TEXT = HexColor("#9A3412")


def register_fonts() -> None:
    fonts = Path("C:/Windows/Fonts")
    pdfmetrics.registerFont(TTFont("Arial", str(fonts / "arial.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Bold", str(fonts / "arialbd.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Italic", str(fonts / "ariali.ttf")))


def make_styles():
    base = getSampleStyleSheet()
    return {
        "cover_kicker": ParagraphStyle(
            "cover_kicker", parent=base["Normal"], fontName="Arial-Bold", fontSize=11,
            leading=15, textColor=TEAL, alignment=TA_CENTER, spaceAfter=18,
        ),
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Title"], fontName="Arial-Bold", fontSize=30,
            leading=37, textColor=NAVY, alignment=TA_CENTER, spaceAfter=12,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle", parent=base["Normal"], fontName="Arial", fontSize=14,
            leading=21, textColor=SLATE, alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Arial-Bold", fontSize=18,
            leading=24, textColor=NAVY, spaceBefore=4, spaceAfter=12, keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Arial-Bold", fontSize=13.5,
            leading=18, textColor=BLUE, spaceBefore=14, spaceAfter=7, keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "h3", parent=base["Heading3"], fontName="Arial-Bold", fontSize=11,
            leading=15, textColor=TEAL, spaceBefore=10, spaceAfter=5, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "body", parent=base["BodyText"], fontName="Arial", fontSize=9.2,
            leading=14.2, textColor=SLATE, alignment=TA_JUSTIFY, spaceAfter=6,
        ),
        "body_small": ParagraphStyle(
            "body_small", parent=base["BodyText"], fontName="Arial", fontSize=8.1,
            leading=11.2, textColor=SLATE, alignment=TA_LEFT, spaceAfter=3,
        ),
        "body_tiny": ParagraphStyle(
            "body_tiny", parent=base["BodyText"], fontName="Arial", fontSize=7.35,
            leading=9.5, textColor=SLATE, alignment=TA_LEFT,
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"], fontName="Arial-Italic", fontSize=7.8,
            leading=10.5, textColor=MUTED, alignment=TA_CENTER, spaceBefore=4, spaceAfter=8,
        ),
        "callout": ParagraphStyle(
            "callout", parent=base["BodyText"], fontName="Arial", fontSize=9,
            leading=13.2, textColor=NAVY, alignment=TA_LEFT,
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"], fontName="Arial", fontSize=7.5,
            leading=9, textColor=MUTED, alignment=TA_CENTER,
        ),
    }


S = None


def P(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def h1(text: str) -> list:
    return [P(text, "h1")]


def h2(text: str) -> list:
    return [P(text, "h2")]


def h3(text: str) -> list:
    return [P(text, "h3")]


def bullet(text: str) -> Paragraph:
    return Paragraph(f"• {text}", S["body"])


def note(text: str, warning: bool = False) -> Table:
    bg = AMBER if warning else SKY
    fg = AMBER_TEXT if warning else NAVY
    paragraph = Paragraph(text, ParagraphStyle("callout_variant", parent=S["callout"], textColor=fg))
    table = Table([[paragraph]], colWidths=[17.1 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.55, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def table(headers: list[str], rows: list[list[str]], widths: list[float] | None = None, tiny: bool = False) -> Table:
    st = "body_tiny" if tiny else "body_small"
    content = [[P(cell, st) for cell in headers]] + [[P(cell, st) for cell in row] for row in rows]
    widths = widths or [17.1 * cm / len(headers)] * len(headers)
    t = Table(content, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def process_row(label: str, detail: str, color: colors.Color = SKY) -> Table:
    t = Table([[P(label, "body_small"), P(detail, "body_small")]], colWidths=[3.25 * cm, 13.85 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), color),
        ("BOX", (0, 0), (-1, -1), 0.35, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def _box(d: Drawing, x: float, y: float, w: float, h: float, title: str, body: str, fill=SKY) -> None:
    d.add(Rect(x, y, w, h, rx=8, ry=8, fillColor=fill, strokeColor=LINE, strokeWidth=0.7))
    d.add(String(x + w / 2, y + h - 17, title, fontName="Arial-Bold", fontSize=8.3,
                 fillColor=NAVY, textAnchor="middle"))
    lines = body.split("\n")
    for index, line in enumerate(lines):
        d.add(String(x + w / 2, y + h - 31 - (index * 10), line, fontName="Arial", fontSize=6.9,
                     fillColor=SLATE, textAnchor="middle"))


def _arrow(d: Drawing, x1: float, y1: float, x2: float, y2: float, color=TEAL) -> None:
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.25))
    dx, dy = x2 - x1, y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    size = 6
    d.add(Polygon([
        x2, y2,
        x2 - ux * size + px * size * 0.55, y2 - uy * size + py * size * 0.55,
        x2 - ux * size - px * size * 0.55, y2 - uy * size - py * size * 0.55,
    ], fillColor=color, strokeColor=color))


def user_flow_diagram() -> Drawing:
    d = Drawing(485, 164)
    steps = [
        (8, "1. Setup", "Demo role\nconsent"),
        (88, "2. Objective", "Goal +\nsession"),
        (168, "3. Source", "Pinned docs\nterm"),
        (248, "4. Concept", "Relation\ncheck"),
        (328, "5. Practice/AI", "Test +\nSocratic"),
        (408, "6. Evidence", "Before/after\ncomplete"),
    ]
    for x, title, body in steps:
        _box(d, x, 83, 70, 54, title, body, MINT if title.startswith("5") else SKY)
    for x, _, _ in steps[:-1]:
        _arrow(d, x + 70, 110, x + 79, 110)
    _box(d, 92, 10, 145, 40, "Recovery", "source unavailable · retry · no progress loss", AMBER)
    _box(d, 255, 10, 145, 40, "Access control", "RBAC + org + teacher visibility consent", MINT)
    _arrow(d, 165, 83, 165, 52, AMBER_TEXT)
    _arrow(d, 327, 83, 327, 52, TEAL)
    return d


def architecture_diagram() -> Drawing:
    d = Drawing(485, 276)
    _box(d, 179, 222, 126, 42, "React / Vite client", "Student · Instructor\nprototype routes separated", SKY)
    _box(d, 179, 150, 126, 45, "FastAPI API", "RBAC · consent · session\nOpenAPI · audit", MINT)
    _box(d, 15, 75, 105, 46, "PostgreSQL", "system of record\ntransaction + backup", SKY)
    _box(d, 135, 75, 100, 46, "Redis", "rate limit · cache\nqueue context", PALE)
    _box(d, 250, 75, 105, 46, "Runner worker", "isolated job\nresource limits", AMBER)
    _box(d, 370, 75, 100, 46, "AI gateway", "policy · quota\ncitation/RAG", MINT)
    _box(d, 68, 8, 117, 40, "Source snapshot", "official docs version\nSHA-256 / fallback", SKY)
    _box(d, 298, 8, 117, 40, "Observability", "redacted logs · metrics\naudit · backup", PALE)
    _arrow(d, 242, 222, 242, 196)
    _arrow(d, 242, 150, 67, 122)
    _arrow(d, 242, 150, 185, 122)
    _arrow(d, 242, 150, 302, 122)
    _arrow(d, 242, 150, 420, 122)
    _arrow(d, 420, 75, 185, 48)
    _arrow(d, 302, 75, 355, 48)
    _arrow(d, 67, 75, 126, 48)
    _arrow(d, 242, 150, 355, 48)
    return d


def erd_diagram() -> Drawing:
    d = Drawing(485, 282)
    _box(d, 9, 216, 102, 44, "Users / Consents", "identity · org\nvisibility", SKY)
    _box(d, 130, 216, 102, 44, "Lessons / Sources", "versioned steps\npinned snapshot", MINT)
    _box(d, 251, 216, 102, 44, "Learning session", "progress · term\nconcept", SKY)
    _box(d, 372, 216, 102, 44, "Assessment", "submission · run\nfiltered result", AMBER)
    _box(d, 74, 105, 115, 47, "AI interaction / hints", "policy · model\ncitation · quota", MINT)
    _box(d, 208, 105, 115, 47, "Learning evidence", "before/after · hash\ncompleted_at", SKY)
    _box(d, 342, 105, 115, 47, "Audit / analytics", "allow/deny\npseudonymous events", PALE)
    _box(d, 156, 20, 175, 45, "Lifecycle / deletion request", "retention · encryption · export/anonymize", PALE)
    _arrow(d, 111, 238, 130, 238)
    _arrow(d, 232, 238, 251, 238)
    _arrow(d, 353, 238, 372, 238)
    _arrow(d, 302, 216, 132, 153)
    _arrow(d, 302, 216, 266, 153)
    _arrow(d, 423, 216, 266, 153)
    _arrow(d, 302, 216, 400, 153)
    _arrow(d, 131, 105, 241, 66)
    _arrow(d, 266, 105, 245, 66)
    _arrow(d, 399, 105, 285, 66)
    return d


def footer(c: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    c.saveState()
    width, _ = A4
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    c.line(1.5 * cm, 1.28 * cm, width - 1.5 * cm, 1.28 * cm)
    c.setFont("Arial", 7.2)
    c.setFillColor(MUTED)
    c.drawString(1.5 * cm, 0.78 * cm, "CodeMind — Đề án phát triển sản phẩm Vòng 3")
    c.drawRightString(width - 1.5 * cm, 0.78 * cm, f"Trang {doc.page}")
    c.restoreState()


def cover_footer(c: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    c.saveState()
    c.setFont("Arial", 7.2)
    c.setFillColor(MUTED)
    c.drawCentredString(A4[0] / 2, 1.0 * cm, "Bản proposal chi tiết — cập nhật 09/08/2026")
    c.restoreState()


def build_story() -> list:
    story: list = []

    # Cover
    story += [Spacer(1, 3.0 * cm), P("CUỘC THI Ý TƯỞNG ĐỔI MỚI SÁNG TẠO 2026 — KHỞI NGUYÊN", "cover_kicker")]
    story += [P("CODEMIND", "cover_title"), P("ĐỀ ÁN PHÁT TRIỂN SẢN PHẨM VÒNG 3", "cover_title")]
    story += [Spacer(1, 0.35 * cm), P("Nền tảng học lập trình AI-first giúp sinh viên hiểu tài liệu chính thống, tự sửa code và lưu bằng chứng học tập", "cover_subtitle")]
    story += [Spacer(1, 1.0 * cm)]
    cover_rows = [
        ["Tên đội", "[BỔ SUNG TỪ ĐỘI TRƯỚC KHI NỘP]"],
        ["Mentor", "[BỔ SUNG TỪ ĐỘI TRƯỚC KHI NỘP]"],
        ["Thành viên & vai trò", "[BỔ SUNG: Tech / Business / Product]"],
        ["Lĩnh vực", "EdTech — AI hỗ trợ học lập trình có trách nhiệm"],
        ["Phiên bản tài liệu", "1.0 — 09/08/2026"],
    ]
    story += [table(["Thông tin", "Nội dung"], cover_rows, [4.5 * cm, 12.6 * cm]), Spacer(1, 0.5 * cm)]
    story += [note("<b>Lưu ý trước khi nộp:</b> Các trường tên đội/mentor/thành viên, URL public và số liệu pilot chưa được cung cấp trong repository nên được giữ ở trạng thái cần điền. Tài liệu không tự tạo số liệu hoặc credential để tránh claim không có bằng chứng.", True)]
    story += [PageBreak()]

    # Contents and compliance
    story += h1("Mục lục và nguyên tắc nộp bài")
    toc_rows = [
        ["I", "Tổng quan dự án — Executive Summary"],
        ["II", "Kiến trúc sản phẩm và MVP: đặc tả, UX/UI, hệ thống/dữ liệu, tech stack, QA/security, trải nghiệm"],
        ["III", "Business model & implementation plan: Lean Canvas, doanh thu, customer journey, marketing, đo lường"],
        ["IV", "Tài chính và roadmap: Capex/Opex, doanh thu, hòa vốn, 3/6/12 tháng"],
        ["Phụ lục", "API, data dictionary rút gọn, traceability, checklist release và nguồn"],
    ]
    story += [table(["Phần", "Nội dung"], toc_rows, [2.1 * cm, 15 * cm])]
    story += h2("Quy ước tuân thủ")
    story += [P("Bản đề bài gốc ghi giới hạn 20 trang cho báo cáo, trong khi thông báo làm rõ sau đó quy định <b>báo cáo chi tiết tối đa 60 trang</b> (không tính bìa và phụ lục). Bản này áp dụng mốc 60 trang mới hơn, đồng thời giữ mục tiêu dung lượng dưới 30 MB theo yêu cầu gốc còn hiệu lực. Slide và video không được tạo theo yêu cầu của chủ sở hữu dự án; đây vẫn là hai hạng mục chính thức cần đội tự bổ sung/được Ban Tổ chức chấp thuận ngoại lệ.")]
    story += [note("<b>Nguyên tắc bằng chứng:</b> “Đã triển khai” chỉ dùng cho luồng có code và kiểm thử local được ghi nhận. “Định hướng/lộ trình” là cam kết sản phẩm Vòng 2 chưa có bằng chứng runtime. Các số liệu thị trường và tài chính giữ vai trò giả định cần pilot xác thực.")]
    story += h2("Bộ artefact đi kèm")
    story += [table(["Artefact", "Vai trò"], [
        ["CodeMind_MVP_Data_Spec.xlsx", "Data dictionary, entity catalog, RBAC, lifecycle, API contracts, event tracking và traceability."],
        ["CodeMind_Round3_Traceability.md", "Bản đồ từ cam kết Vòng 2/Figma sang mức triển khai, roadmap và điều kiện đóng."],
        ["CodeMind_MVP_Experience_Guide.md", "Hướng dẫn người chấm, role matrix, kịch bản demo và checklist incognito."],
        ["CodeMind_Deployment_Runbook.md", "Cách triển khai, migration, backup/restore, rollback và thao tác vận hành."],
    ], [6.0 * cm, 11.1 * cm])]
    story += [PageBreak()]

    # I
    story += h1("I. TỔNG QUAN DỰ ÁN — EXECUTIVE SUMMARY")
    story += [P("CodeMind giải quyết bốn điểm nghẽn lặp lại của người học lập trình tại Việt Nam: đọc tài liệu kỹ thuật tiếng Anh rời rạc; thiếu mental model để nối các khái niệm; nhận phản hồi code không đúng mức độ; và xu hướng sao chép đáp án từ AI thay vì tự debug. Sản phẩm tổ chức một learning loop có thể kiểm chứng: <b>nguồn chính thức → chọn thuật ngữ → kiểm tra quan hệ khái niệm → thực hành code → gợi ý Socratic → evidence trước/sau</b>.")]
    story += [P("MVP Round 3 tập trung vào một lesson Deque/Python có sáu bước. Việc giảm breadth không xóa các cam kết Vòng 2; các module Mindmap Challenge, VARK, integrity GitHub/MOSS, gamification, community, Campus và billing được bảo toàn trong roadmap và được gắn nhãn trung thực. Lát cắt dọc này được chọn để chứng minh cơ chế khác biệt của CodeMind: AI không làm hộ, nội dung bám nguồn, tiến bộ có thể xem lại và dữ liệu học tập chỉ chia sẻ khi có consent.")]
    story += [table(["Yếu tố", "Tóm tắt"], [
        ["Khách hàng ưu tiên", "Sinh viên năm 1–2 ngành CNTT/kỹ thuật tại Việt Nam; tiếp theo là career switcher và trường/đơn vị đào tạo theo B2B2C."],
        ["Value proposition", "Biến tài liệu chính thống thành đường học có hướng dẫn, phản hồi Socratic và bằng chứng tự sửa thay vì câu trả lời copy-paste."],
        ["USP", "Source Trust + Socratic policy + evidence trước/sau + consent-based instructor view trong cùng một learning loop."],
        ["Mục tiêu ngắn hạn", "Triển khai public một lesson ổn định, chạy pilot 30–50 người, đo completion/self-correction/D7 trước khi mở rộng content và thương mại hóa."],
        ["Mục tiêu tài chính", "Kiểm định đơn vị kinh tế đã giả định ở Vòng 2 bằng quota AI, gói Free/Plus/Pro/Campus và các bề mặt quảng cáo có rào chắn."],
    ], [4.1 * cm, 13 * cm])]
    story += h2("Vấn đề, cơ chế giải pháp và giả thuyết cần kiểm chứng")
    story += [table(["Vấn đề", "Cơ chế CodeMind", "Chỉ số xác thực pilot"], [
        ["Tài liệu tiếng Anh gây đứt mạch học", "Nguồn đã pin phiên bản; người học tự chọn thuật ngữ, AI giải thích theo ngữ cảnh và trích dẫn nguồn.", "≥70% phiên bắt đầu có source engagement."],
        ["Kiến thức phân mảnh", "Concept check P0; roadmap Master Graph/Mindmap Challenge để thấy lỗ hổng mental model.", "Completion concept step; accuracy theo rule version."],
        ["Debug lệ thuộc AI", "Câu hỏi phản biện + hint 1→3, không cung cấp bản sửa hoàn chỉnh.", "≥50% phiên hoàn thành tự sửa sau lần fail."],
        ["Thiếu evidence cho người học/giảng viên", "Evidence hash gồm before/after, số hint, test result; teacher chỉ đọc khi có consent.", "Tỷ lệ consent visibility, review usefulness survey."],
    ], [4.0 * cm, 8.1 * cm, 5.0 * cm], True)]
    story += [PageBreak()]

    # II 2.1
    story += h1("II. KIẾN TRÚC SẢN PHẨM VÀ MVP")
    story += h2("2.1. MVP Specification — phạm vi, chức năng lõi và user flow")
    story += [P("Đơn vị triển khai của Round 3 là <b>một vertical slice có thể thao tác</b>, không phải 142 frame Figma. Luồng live gồm Deque/Python 3.12 và sáu bước: mục tiêu, nguồn, concept, thực hành, AI Socratic, evidence. Các route catalog Figma, Student, Teacher, Admin không nối API phải được gắn nhãn “prototype/roadmap” và không dùng trong demo chấm.")]
    story += h3("Chức năng core trong lát cắt MVP")
    story += [table(["Mã", "Chức năng", "Quy tắc nghiệp vụ / acceptance"], [
        ["FR-01", "Demo identity & consent", "Role demo Student/Instructor/Content admin. Cam kết academic integrity là điều kiện tạo session; teacher visibility là tùy chọn và có thể revoke."],
        ["FR-02", "Official source reader", "Lesson chỉ dùng source version đã pin; hiển thị publisher/version/checksum/citation. Không suy đoán thuật ngữ cá nhân của người học."],
        ["FR-03", "Concept check", "Người học nối quan hệ khái niệm theo rule version. Kết quả do server tính và lưu attempt/evidence."],
        ["FR-04", "Practice & test", "Nộp code bằng idempotency key; trả kết quả đã lọc (ví dụ 4/5, 5/5), không lộ hidden expected output."],
        ["FR-05", "Socratic AI", "Policy từ chối đáp án hoàn chỉnh; chỉ câu hỏi/hint tuần tự 1→3; có quota, prompt/model/policy/citation metadata."],
        ["FR-06", "Evidence & review", "Chỉ complete khi đạt invariant; tạo snapshot before/after, hint count, passed count và hash. Instructor chỉ xem summary khi đúng role/org/consent."],
    ], [1.45 * cm, 3.3 * cm, 12.35 * cm], True)]
    story += h3("Luồng người học và điểm kiểm soát")
    flow_rows = [
        ["1. Setup", "Chọn tài khoản demo, đọc mục đích xử lý dữ liệu, xác nhận integrity, tùy chọn chia sẻ cho instructor."],
        ["2. Objective", "Hiểu mục tiêu lesson và tiêu chí hoàn thành; hệ thống khởi tạo learning session có version."],
        ["3. Source", "Đọc source Python đã pin, chọn `maxlen`/thuật ngữ; nhận giải thích có link nguồn chính thức."],
        ["4. Concept", "Trả lời quan hệ khái niệm; server lưu kết quả theo rule version."],
        ["5. Practice + AI", "Nộp code, thấy test đã lọc; khi chưa đạt, AI đặt câu hỏi và mở hint 1→3 theo quota."],
        ["6. Evidence", "Sau 5/5, tạo evidence bất biến; người học xem before/after và quyền chia sẻ."],
    ]
    story += [table(["Bước", "Hành vi & dữ liệu tạo ra"], flow_rows, [3.1 * cm, 14.0 * cm])]
    story += [Spacer(1, 0.18 * cm), user_flow_diagram(), P("Sơ đồ 1. User flow MVP sáu bước và hai kiểm soát ngang: recovery, RBAC/consent.", "caption")]
    story += [note("<b>Điểm khác với mock:</b> Figma có một màn AI riêng (Step 5). Release MVP cần hiển thị đây là bước live riêng hoặc mô tả dứt khoát rằng AI là panel thuộc Practice; không để rail sáu bước nhưng thực tế nhảy từ Step 4 sang Evidence.")]
    story += [PageBreak()]

    story += h2("2.1.1. So sánh UX/UI: từ mockup Vòng 2 đến MVP vận hành")
    story += [table(["Nội dung Vòng 2/Figma", "Quyết định MVP", "Lý do & bằng chứng cần có"], [
        ["Official Docs Reader", "Có trong source step với citation." , "Giữ pain lớn nhất: không hiểu tài liệu chính thống. Cần source snapshot/checksum thật."],
        ["Mindmap Challenge", "Thay bằng concept check có cấu trúc ở P0." , "Giảm khó khăn chấm graph khi chỉ có một lesson; không claim là mindmap hoàn chỉnh."],
        ["Code lab 4/5 → 5/5", "Có practice, idempotency, evidence." , "Cần runner thực hoặc adapter được công bố rõ; không chạy code untrusted trong process API."],
        ["Socratic hints", "Hint 1→3 và refusal policy." , "Khác biệt sư phạm cốt lõi; cần policy/adversarial suite trước production."],
        ["Teacher/Admin workspace", "Màn chọn demo, Instructor summary read-only và Content admin analytics tối thiểu nối API; catalog Teacher/Admin đầy đủ vẫn là prototype." , "Không để mock 5-step/Python 3.13/thực hành thread-safe thay cho lesson live 6-step/Python 3.12."],
        ["Recovery frames", "Map source unavailable, quota, submission error, empty evidence thành state thao tác được." , "Không chỉ banner chung; retry/back/fallback phải bảo toàn progress."],
    ], [4.2 * cm, 5.0 * cm, 7.9 * cm], True)]
    story += h3("Non-functional requirements")
    story += [table(["Nhóm", "Yêu cầu P0", "Tiêu chí release"], [
        ["Usability", "Hành trình happy path hoàn thành trong thời lượng demo; copy tiếng Việt thân thiện, link nguồn tương tác.", "E2E desktop + mobile smoke; keyboard/focus/error announcement."],
        ["Reliability", "Session/progress không mất khi refresh/restart; retry không tạo duplicate submission.", "Persistent store, optimistic version, idempotency 24h, recovery states."],
        ["Security", "RBAC + consent trước teacher view; hidden tests không lộ; no secret in client/log.", "Deny audit, security scan, reviewed CORS/auth configuration."],
        ["Performance", "API thường phản hồi nhanh; job code/AI tách khỏi request lifecycle.", "Load 50 VU, P95 API <500ms (không gồm LLM/runner), error <2%."],
        ["Observability", "Event/policy/latency được ghi không lộ raw code/question ra analytics.", "Dashboard/export aggregate + incident/runbook."],
    ], [3.2 * cm, 7.3 * cm, 6.6 * cm], True)]
    story += [PageBreak()]

    # 2.2
    story += h2("2.2. System & Database Design")
    story += h3("Kiến trúc logic và luồng dữ liệu")
    architecture_rows = [
        ["React 19 + Vite + TypeScript", "Render six-step UI, giữ token trong memory/storage theo policy, gọi HTTPS API; không giữ hidden test hoặc secret."],
        ["FastAPI API", "Auth/demo identity, lesson/session/progress, consent/RBAC, evidence, audit, API contract/OpenAPI."],
        ["PostgreSQL", "System of record cho user, consent, session, source version, submission/evidence, audit và event. Transactional constraints tại server."],
        ["Redis", "Rate limit, short-lived context/cache/job state; mất Redis không làm mất tiến trình học."],
        ["Runner worker cô lập", "Nhận job qua queue; container/image allowlist, network deny, CPU/RAM/time/output limits; trả result đã lọc."],
        ["AI gateway + RAG", "Route model theo chi phí/risk, policy Socratic, quota, retry/fallback; retrieval chỉ từ source/version đã pin và citation bắt buộc."],
        ["Object storage/observability", "Lưu source snapshot/raw diagnostic có TTL; log/metrics/audit tách và redaction; backup encrypted."],
    ]
    story += [table(["Thành phần", "Trách nhiệm"], architecture_rows, [4.8 * cm, 12.3 * cm])]
    story += h3("Luồng xử lý end-to-end")
    story += [process_row("A. Khởi tạo", "Student xác thực demo → API xác định role/org → ghi consent version → tạo learning session gắn lesson/source version.", MINT)]
    story += [process_row("B. Học & thực hành", "Term/concept attempt được ghi append-only. Submission có content hash + idempotency key; runner chỉ trả pass/fail/safe message, không trả hidden expected output.", SKY)]
    story += [process_row("C. AI", "API gửi context tối thiểu cho AI gateway; policy quyết định refuse/question/hint; response lưu metadata/citation nhưng không lưu chain-of-thought.", MINT)]
    story += [process_row("D. Hoàn tất & review", "Server kiểm invariant (progress, test pass, consent context) → tạo evidence hash → teacher summary chỉ mở khi role + org + visibility consent hợp lệ; mọi allow/deny vào audit.", SKY)]
    story += [Spacer(1, 0.16 * cm), architecture_diagram(), P("Sơ đồ 2. Kiến trúc logic: client, API, database, cache, runner, AI/source và observability.", "caption")]
    story += [P("Kiến trúc đích này giữ đúng stack đã mô tả ở Vòng 2. Repository hiện có adapter P0 lưu aggregate snapshot vào PostgreSQL và readiness/migration test local; file persistence cũng tồn tại cho local profile. Tuy nhiên Compose/staging public chưa được xác nhận, còn canned AI và simulated runner chỉ là fallback local, không được mô tả là RAG/runner production.")]
    story += [PageBreak()]

    story += h3("ERD lõi (mức logical)")
    story += [erd_diagram(), P("Sơ đồ 3. ERD logical rút gọn; danh sách field/key/retention đầy đủ trong workbook data specification.", "caption")]
    erd_rows = [
        ["Identity & consent", "users → auth_identities; users ↔ organization_memberships ↔ organizations; users → user_consents", "Xác thực, role theo tổ chức, consent learning/instructor visibility tách riêng."],
        ["Content & source", "courses → lessons → lesson_steps/coding_exercises; sources → source_versions → lesson_sources", "Version/pin source để replay evidence và xử lý source unavailable."],
        ["Learning", "users + lessons → learning_sessions → step_attempts/term_selections/concept_answers", "Session là aggregate root; bước có sequence/rule version."],
        ["Assessment", "learning_sessions → code_submissions → test_runs → test_results", "Idempotency, server-side hidden tests, trạng thái queued/running/passed/failed/error/timeout."],
        ["AI & evidence", "learning_sessions → ai_interactions → ai_hints; learning_sessions → learning_evidence", "Policy/citation/quota metadata và snapshot before/after bất biến."],
        ["Governance", "audit_events; analytics_events; quota_ledger; deletion_requests", "Audit allow/deny, metrics pseudonymous, retention/SLA/privacy."],
    ]
    story += [table(["Nhóm entity", "Quan hệ chính", "Mục đích"], erd_rows, [3.4 * cm, 7.0 * cm, 6.7 * cm], True)]
    story += h3("Ràng buộc dữ liệu bắt buộc")
    story += [table(["Ràng buộc", "Cách áp dụng"], [
        ["Source Trust", "Mỗi lesson publish pin `source_version_id`; source có canonical HTTPS URL, publisher, trust status, content SHA-256, retrieved_at và availability status."],
        ["Tính toàn vẹn tiến trình", "Session có version optimistic locking; `lesson_steps.sequence_no` unique; attempt/evidence không ghi đè; evidence chỉ có một record cho session complete."],
        ["An toàn assessment", "Code tối đa 100KB; idempotency key unique trong cửa sổ 24h; hidden expected data chỉ ở server; raw output có object reference + TTL."],
        ["AI safety", "AI interaction ghi policy decision/prompt version/model/citation/latency; hint level unique và chỉ mở tuần tự; không lưu chain-of-thought."],
        ["Privacy", "Email/display name là PII hạn chế; code/question có thể chứa PII; encryption at rest, access purpose, retention job và deletion request phải theo lifecycle."],
    ], [4.0 * cm, 13.1 * cm])]
    story += [PageBreak()]

    story += h3("Data lifecycle và quyền truy cập")
    story += [table(["Loại dữ liệu", "Phân loại / retention", "Ai truy cập và điều kiện"], [
        ["Hồ sơ user", "Restricted PII; thời hạn account + 30 ngày", "Chủ thể; security service. Instructor không có quyền xem email ngoài scope."],
        ["Consent evidence", "Restricted PII; 3 năm", "User/privacy owner; record version, granted/revoked time, không thay thế bằng toggle client."],
        ["Learning session/evidence", "Confidential; 2 năm, sau đó anonymize metric", "Student; instructor cùng org nếu teacher visibility=true; content admin theo need-to-know."],
        ["Raw code / AI content", "Confidential/potential PII; raw 180 ngày, metadata 2 năm", "Student và hạn chế theo policy; không đưa vào analytics/export hoặc teacher summary mặc định."],
        ["Audit events", "Confidential; 2 năm", "Security/content admin theo role; append-only, không secret/full payload."],
        ["Analytics events", "Pseudonymous; raw 13 tháng, aggregate lâu hơn", "Product analytics; user pseudo ID, không email/raw code/question."],
    ], [3.4 * cm, 5.8 * cm, 7.9 * cm], True)]
    story += [note("Workbook <b>CodeMind_MVP_Data_Spec.xlsx</b> là nguồn chi tiết cho 28 entity, enum/rule, API contract, event catalog, RBAC và sample data. Code/migration phải được update cùng workbook để tránh trường hợp workbook nói “covered” nhưng runtime chưa có adapter/test tương ứng.")]
    story += [PageBreak()]

    # 2.3
    story += h2("2.3. Tech Stack & Deployment")
    story += [table(["Layer", "Lựa chọn", "Lý do / tiêu chuẩn"], [
        ["Frontend", "React 19, Vite, TypeScript, Tailwind", "Phù hợp component/state của Figma; build static nhanh; accessibility và responsive được kiểm thử riêng."],
        ["Backend", "FastAPI async, Pydantic, SQLAlchemy/Alembic", "API contract rõ, validation server-side, OpenAPI, migration có version."],
        ["Database", "PostgreSQL", "Nguồn sự thật transactional; constraint/transaction/backup; không dùng cache làm persistence."],
        ["Cache/queue", "Redis", "Rate limit/cache/context/job state tạm; graceful degradation nếu unavailable."],
        ["Code execution", "Worker/container tách API", "Không thực thi code người học trong FastAPI; egress deny, resource limits, image allow-list."],
        ["AI", "Gateway provider-agnostic + RAG/citation", "Route cheap/simple request đến model tiết kiệm; request code/mindmap dùng model phù hợp hơn; quota/cost/fallback."],
        ["DevOps", "Docker Compose local/staging, CI, secret manager, monitoring", "Reproduce environment, scan/test/build gate, release migration, runbook rollback."],
    ], [3.2 * cm, 5.0 * cm, 8.9 * cm], True)]
    story += h3("Quy trình triển khai")
    story += [table(["Pha", "Bước có kiểm soát", "Artefact/evidence"], [
        ["Build", "Lint, type/compile, unit/API contract, frontend production build, secret/dependency scan.", "CI run ID, lockfiles, SBOM/scan output."],
        ["Release", "Build immutable image, inject secret qua environment manager, run Alembic migration, seed demo content không chứa mật khẩu production.", "Image digest, migration version, deployment log."],
        ["Verify", "Health/readiness check DB/Redis/worker/AI fallback; browser incognito test 3 roles + happy path/recovery.", "Checklist có timestamp, screenshots/log redacted."],
        ["Operate", "Metrics/alerts, daily encrypted DB backup, retention jobs, rollback app/migration plan, incident record.", "Backup restore rehearsal, on-call owner, RTO/RPO."],
    ], [2.4 * cm, 9.1 * cm, 5.6 * cm], True)]
    story += [P("Deployment công khai không được thay bằng localhost hoặc máy cá nhân theo yêu cầu đề bài. Repository hiện chỉ có thể được xem là release-ready khi URL HTTPS, migration/runtime dependency, demo credentials và incognito test được ghi nhận. Chưa có URL cloud nào được đưa vào tài liệu này vì đội chưa cung cấp quyền deploy.")]
    story += [PageBreak()]

    story += h3("API contract rút gọn")
    story += [table(["Method", "Endpoint", "Role", "Tác vụ/response chính"], [
        ["POST", "/v1/demo/session", "Demo role", "Tạo demo token/session có TTL thật; không mô phỏng login production."],
        ["GET", "/v1/lessons/{slug}", "Public/authenticated", "Lesson published, steps và pinned source metadata."],
        ["POST", "/v1/learning-sessions", "Student", "Khởi tạo session sau consent; trả session/version."],
        ["PATCH", "/v1/me/consents/{purpose}", "Student", "Grant/revoke purpose có policy version; audit thay đổi."],
        ["PATCH", "/v1/learning-sessions/{id}/progress", "Owner", "Lưu step optimistic version; reject transition trái state machine."],
        ["POST", "/v1/sessions/{id}/terms | concept-answers", "Owner", "Lưu term từ pinned source / server-score concept relation."],
        ["POST", "/v1/sessions/{id}/submissions", "Owner", "Queue runner với idempotency key; trả 201/202 theo contract."],
        ["POST", "/v1/sessions/{id}/ai-interactions", "Owner", "Socratic response + policy/citation/quota metadata; 429 khi quota exceeded."],
        ["POST", "/v1/ai-interactions/{id}/hints/{level}/open", "Owner", "Mở hint tuần tự, ghi event/usage."],
        ["POST/GET", "/v1/sessions/{id}/complete | evidence", "Owner/authorized instructor", "Tạo/read immutable evidence sau invariant."],
        ["GET", "/v1/instructor/sessions/{id}/summary", "Instructor", "Read-only summary sau role + org + consent check; không raw code."],
        ["DELETE", "/v1/me/data", "User", "Tạo privacy export/deletion request có status/SLA, không xóa im lặng."],
    ], [1.25 * cm, 5.55 * cm, 2.7 * cm, 7.6 * cm], True)]
    story += [PageBreak()]

    # 2.4
    story += h2("2.4. QA & Security")
    story += h3("Mô hình quyền, consent và bảo vệ dữ liệu")
    story += [table(["Actor", "Được phép", "Không được phép"], [
        ["Student", "Tạo/đọc session của mình; term/concept/submission/AI/evidence; grant/revoke consent; yêu cầu export/deletion.", "Xem session/evidence người khác, hidden tests, audit/admin analytics."],
        ["Instructor", "Đọc summary/evidence được consent của student trong cùng org/class; xem aggregate theo policy.", "Viết/sửa code của học viên; xem private session/raw code mặc định; vượt org scope."],
        ["Content admin", "Quản lý content/source version theo workflow; xem analytics/audit đã redaction theo quyền.", "Đọc secret, credential, raw PII không cần thiết; bypass consent cho teacher view."],
        ["System worker", "Chạy job tách biệt với token ngắn hạn; trả kết quả đã lọc; ghi audit/metrics.", "Egress internet tùy ý; truy cập database rộng hơn job/queue cần thiết."],
    ], [2.5 * cm, 7.35 * cm, 7.25 * cm], True)]
    story += [P("Các kiểm soát tối thiểu: HTTPS; secret chỉ qua environment manager; token TTL/rotation; CORS allow-list; rate-limit server-side; authorization kiểm role + resource owner + organization + consent; audit allow/deny/error; encryption at rest/in transit; log redaction; backup encryption; periodic dependency/secret scan. Password production không nằm trong Git; demo identity phải được ghi rõ là demo để không tạo ấn tượng đây là authentication production.")]
    story += h3("Ma trận QA trước release")
    story += [table(["Nhóm test", "Case chính", "Bằng chứng cần lưu"], [
        ["Unit/domain", "State transition 6 bước, scoring, hint ladder, quota, idempotency, consent/RBAC policies.", "Test result + coverage focus vào policy/transition."],
        ["Integration", "Migration up/down, Postgres persistence/restart, Redis unavailable, source fallback, runner timeout, AI retry/fallback.", "Compose log, DB test fixture, API contract status codes."],
        ["Browser E2E", "Student happy path 4/5→hint→5/5→evidence; refresh; 429; source unavailable; submission retry; instructor deny/allow.", "Video/screenshot optional nhưng test log/trace bắt buộc."],
        ["Security", "OWASP baseline, auth expiry, authorization negative paths, rate limit, CORS, secret/dependency scan, hidden-test leak review.", "Scan report triaged, deny audit, remediation record."],
        ["Performance", "≥50 virtual users, queue behavior, P95 normal API, error rate, memory/CPU limits runner.", "Load report with environment/config and p95/p99/error."],
        ["Recovery", "Backup restore to isolated DB, reset demo data, rollback app/migration, feature flag AI fallback.", "Restore timestamp, RTO/RPO actual, owner sign-off."],
    ], [3.0 * cm, 8.0 * cm, 6.1 * cm], True)]
    story += [PageBreak()]

    story += h3("Risk register")
    story += [table(["Rủi ro", "Tác động", "Kiểm soát/owner", "Release gate"], [
        ["AI hallucination / làm hộ", "Mất niềm tin học thuật", "Pinned RAG citation, Socratic policy, adversarial 20 prompts, sampled review — AI owner.", "Không có full-solution leak; policy test pass."],
        ["Code execution độc hại", "RCE/lộ dữ liệu/chi phí", "Worker container, egress deny, CPU/RAM/time/output caps, image allow-list — Platform.", "Sandbox negative test and timeout pass."],
        ["Teacher xem sai dữ liệu", "Privacy/B2B2C risk", "Role + membership + consent + audit deny/allow, minimal summary — Backend/Privacy.", "Negative RBAC test; consent revoke takes effect."],
        ["Source drift/URL lỗi", "Giải thích sai / demo đứt", "Snapshot, SHA-256, availability state, cached fallback — Content.", "Replay source and source-unavailable recovery."],
        ["AI cost spike", "Unit economics âm", "Quota ledger, model routing, budget alert, fallback canned/disable AI — Product/AI.", "Cost dashboard and cap configured."],
        ["Overclaim từ Figma mock", "Giám khảo đánh giá sai phạm vi", "Prototype badge, judge flow links only to live routes, traceability doc — Product.", "Incognito walkthrough never enters mock."],
    ], [3.1 * cm, 3.4 * cm, 6.1 * cm, 4.5 * cm], True)]
    story += [note("<b>Trạng thái kiểm chứng hiện tại:</b> các gate local (lint/build/API contract/unit test) là bằng chứng phát triển, không thay thế E2E public, security/load, backup/restore hoặc pilot. Những gate chưa có artifact phải ở trạng thái pending trong README/progress log và proposal.", True)]
    story += [PageBreak()]

    # 2.5
    story += h2("2.5. Real MVP Experience")
    story += [P("Đề bài yêu cầu URL trải nghiệm mở công khai, video demo và tài khoản demo theo nhóm quyền. Theo yêu cầu của chủ sở hữu, tài liệu này không sản xuất slide/video; tuy nhiên URL và demo accounts vẫn là điều kiện MVP cần được thực hiện trước khi nộp. Không dùng localhost/personal machine thay URL public.")]
    story += [table(["Hạng mục", "Trạng thái trong tài liệu", "Việc phải chốt trước khi nộp"], [
        ["URL MVP", "Chưa có URL public được cung cấp.", "Deploy HTTPS; ghi URL; mở cửa sổ incognito/mạng khác xác nhận."],
        ["Student demo", "Tài khoản demo seed dùng cho P0.", "Chốt email/password hoặc one-time access public; reset seed trước chấm; không commit secret."],
        ["Instructor demo", "Màn summary read-only tối thiểu nối API local.", "Chốt sample session consent=true và test negative consent=false trên deployment."],
        ["Content admin demo", "Chỉ expose analytics/content scope thật sự vận hành.", "Không dùng admin mock làm bằng chứng; giới hạn data/PII và audit access."],
        ["Video ≤3 phút", "Ngoài phạm vi được yêu cầu trong task này.", "Đội tự quay sau deploy hoặc xin xác nhận ngoại lệ với BTC."],
    ], [3.3 * cm, 5.5 * cm, 8.3 * cm], True)]
    story += h3("Kịch bản thao tác cho giám khảo (mục tiêu ≤3 phút)")
    story += [table(["Thời lượng", "Thao tác", "Điểm cần chứng minh"], [
        ["0:00–0:20", "Mở URL incognito, chọn Student demo, xem consent learning và teacher visibility tách biệt.", "Scope dữ liệu, integrity, role rõ ràng."],
        ["0:20–0:55", "Đọc nguồn Python đã pin, chọn `maxlen`, mở link nguồn chính thức/citation.", "Source Trust và hỗ trợ tiếng Việt theo ngữ cảnh."],
        ["0:55–1:25", "Hoàn thành concept check; vào practice có sẵn lần nộp 4/5 hoặc tạo lỗi có kiểm soát.", "Mental model, state machine, safe test feedback."],
        ["1:25–2:05", "Mở AI step/panel, xem câu hỏi Socratic và hint 1→3 không có full solution.", "AI guardrail và quota/citation."],
        ["2:05–2:30", "Nộp bản 5/5, xem evidence before/after/hint count/source version.", "Self-correction evidence."],
        ["2:30–3:00", "Đổi Instructor demo, chỉ xem session đã consent; thử session không consent bị deny (hoặc checklist).", "RBAC, consent, teacher read-only."],
    ], [2.4 * cm, 8.5 * cm, 6.2 * cm], True)]
    story += [PageBreak()]

    # III
    story += h1("III. BUSINESS MODEL & IMPLEMENTATION PLAN")
    story += h2("3.1. Lean Canvas")
    canvas_rows = [
        ["Problem", "Rào cản tiếng Anh; knowledge fragmentation; feedback code không đúng mức; answer-copying từ AI; giảng viên thiếu evidence/consent view."],
        ["Customer segments", "Core B2C: sinh viên năm 1–2 CNTT/kỹ thuật. Secondary: career switcher 22–28. B2B2C: trường/bootcamp."],
        ["Unique value proposition", "Học từ nguồn chính thống, AI gợi mở thay vì làm hộ, và bằng chứng tự sửa có thể xem lại."],
        ["Solution", "Docs Reader + concept/mindmap progression + code lab + Socratic AI + integrity/teacher consent roadmap."],
        ["Channels", "CLB IT, lớp nhập môn, nội dung short-form học thuật, campus pilot, referral sau lesson completion."],
        ["Revenue", "Free quota; Student Plus/Pro; Campus pool/license; ad/affiliate có rào chắn, không đặt trong bề mặt tập trung học."],
        ["Cost structure", "AI/runner variable cost, cloud/DB/observability, content review, acquisition/community, support/compliance."],
        ["Key metrics", "Activation source→concept, completion, self-correction, D7, cost per completed lesson, paid conversion, consent-safe instructor use."],
        ["Unfair advantage", "Sự kết hợp source trust + Socratic policy + evidence + safe unit economics trong bối cảnh người học Việt Nam."],
    ]
    story += [table(["Khối", "Nội dung"], canvas_rows, [4.2 * cm, 12.9 * cm])]
    story += [P("Các số liệu TAM/SAM/SOM và giả định tài chính bên dưới kế thừa báo cáo Vòng 2. Chúng là giả thuyết vận hành, không phải traction đã đạt. Pilot bắt buộc cung cấp cohort, thời gian quan sát, định nghĩa metric và limitations trước khi dùng trong thuyết trình/đàm phán.")]
    story += h2("3.2. Revenue model và unit economics")
    story += [table(["Gói", "Quota Vòng 2", "Giá trị/điều kiện"], [
        ["Free", "10 giải thích tài liệu; 2 mindmap; 2 code hint/tháng", "Onboarding và validation; tuyệt đối không đổi ads lấy Hearts/hint."],
        ["Student Plus", "80 giải thích; 15 mindmap; 25 code hint/tháng", "Giá sinh viên, quota cứng để kiểm soát COGS AI."],
        ["Pro", "200 giải thích; 40 mindmap; 60 code hint/tháng", "Nhóm học sâu/career switcher; công khai fair-use và cost cap."],
        ["Campus", "Shared pool theo đơn vị", "B2B2C: org/role/data governance, invoice/license; rollout sau pilot."],
    ], [3.0 * cm, 5.8 * cm, 8.3 * cm])]
    story += [P("Nguồn quảng cáo chỉ được xem là phụ trợ: không có tại coding workspace, AI chat, quiz, mindmap hoặc video; chỉ dashboard, docs footer sau >60% scroll, summary và resource hub. Tối đa 2 ad request/session, cách nhau ≥90 giây; không watch-ad-for-reward; chặn ad gian lận học thuật/cờ bạc/làm giàu nhanh; người dùng nhỏ tuổi chỉ contextual/non-personalized; rollback A/B nếu D7 giảm >3%.")]
    story += [PageBreak()]

    story += h2("3.3. Digital Customer Journey Map")
    story += [table(["Giai đoạn", "Touchpoint", "Nỗi đau / rủi ro", "Phản hồi UX và KPI"], [
        ["Awareness", "Video ngắn/CLB/lớp nhập môn", "AI bị xem là máy làm bài; thiếu niềm tin vào nội dung.", "Minh họa 4/5→Socratic→5/5; CTR, landing conversion."],
        ["Consideration", "Landing, source example, FAQ privacy", "Sợ khó dùng/AI sai/thu dữ liệu quá mức.", "Hiển thị source/citation, policy no-answer, consent tách purpose; signup rate."],
        ["Activation", "Demo lesson Deque", "Không hiểu English hoặc bị kẹt ở code.", "Docs reader, concept check, safe error, hints; source→practice rate."],
        ["Learning", "Practice/AI/evidence", "Thử-sai vô thức, copy code, mất progress.", "Hint ladder, state persistence, before/after evidence; completion/self-correction."],
        ["Retention", "Streak/league/community roadmap", "Mất động lực sau 1 tuần.", "Nội dung tiếp theo, reminder đúng consent; D7/D30."],
        ["Referral", "Share evidence/resource hub", "Chia sẻ có thể lộ code/PII.", "Share aggregate/opt-in, no raw code default; referral rate."],
    ], [2.6 * cm, 4.0 * cm, 5.0 * cm, 5.5 * cm], True)]
    story += h2("3.4. Digital marketing strategy: 100 → 1.000 người dùng đầu")
    story += [table(["Giai đoạn", "Mục tiêu", "Kênh / hoạt động chi phí thấp", "KPI quyết định đi tiếp"], [
        ["0–100", "Problem/UX validation", "5–10 usability sessions; 30–50 student pilot qua CLB/lớp; interview sau lesson.", "Completion, self-correction, source engagement, qualitative friction."],
        ["100–300", "Cohort retention", "Campus/CLB partner, weekly mini challenge dựa trên source, referral sau completion.", "D7, cost/completed lesson, error/recovery rate."],
        ["300–1.000", "Repeatable acquisition", "Creator nội dung “đọc docs + debug”, SEO resource hub, ambassador program có disclosure.", "CAC proxy, activation, referral, paid intent; không scale ads nếu retention chưa đạt."],
    ], [2.4 * cm, 3.5 * cm, 6.2 * cm, 5.0 * cm], True)]
    story += [PageBreak()]

    story += h2("3.5. Content plan & measurement")
    story += [table(["Nội dung", "Mục tiêu", "Đo lường và nguyên tắc"], [
        ["Official docs micro-explainers", "Giảm anxiety khi gặp English technical docs.", "Completion source step; citation click; review nội dung bởi owner/human reviewer."],
        ["Debug diary 4/5→5/5", "Chứng minh self-correction thay answer-copying.", "Evidence complete rate; hint distribution; không công khai raw code của learner."],
        ["Campus pilot workshop", "Thu feedback từ student/instructor và data governance.", "Cohort consent, attendance, D7; report aggregate, no fabricated claim."],
        ["Resource hub/affiliate", "Tạo giá trị sau lesson, không chèn vào workspace tập trung.", "Click-through disclosure; ad/affiliate policy compliance."],
    ], [4.5 * cm, 5.3 * cm, 7.3 * cm])]
    story += [note("Bộ event analytics tối thiểu: lesson_started, source_viewed, term_selected, concept_answered, submission_created, test_resulted, ai_interaction, hint_opened, evidence_completed, consent_changed và instructor_summary_viewed. Properties chỉ dùng dữ liệu pseudonymous/aggregate; không đưa email, raw code hay full AI question vào product analytics.")]
    story += [PageBreak()]

    # IV
    story += h1("IV. FINANCIAL & ROADMAP")
    story += h2("4.1. Khung tài chính năm đầu")
    story += [P("Báo cáo Vòng 2 đã đưa ra mô hình unit economics với quota AI, phân tầng B2C/B2B2C và nguồn thu quảng cáo/affiliate có rào chắn. Để không giả định traction mới, bảng dưới thể hiện <b>khung kiểm định</b>; đội cần điền số liệu supplier/cloud hiện hành và cohort pilot trước khi nộp bản chốt. Các con số Vòng 2 như chi phí AI Free khoảng 4,31 triệu VND/tháng, ad revenue khoảng 1,25 triệu VND/tháng, và hòa vốn khoảng 173 paid users chỉ được ghi là giả định lịch sử cần xác minh bằng giá provider hiện tại.")]
    story += [table(["Nhóm", "Nội dung tính", "Công thức/điểm kiểm soát"], [
        ["Capex (one-off)", "Thiết kế/UX, thiết lập CI/CD/cloud, security review, content seed, pilot material.", "Tách cash và labor; owner ký cost sheet; không double-count tài sản/lương."],
        ["Opex cố định/tháng", "Compute/API/DB/object storage/monitoring, domain/email, tool team, support/compliance.", "Theo invoice; reserve cho backup/observability, không chỉ server app."],
        ["COGS biến đổi", "Token AI theo model, runner minute, payment fee, customer support per active user.", "Quota ledger × unit price; alert theo cohort/gói; compare provider before scale."],
        ["Doanh thu", "Student Plus/Pro, Campus license/shared pool, permitted ad/affiliate.", "Active paid × net ARPU; churn/refund/tax; ads không dùng làm bù lỗ giả tạo."],
        ["Break-even", "Fixed Opex ÷ contribution margin per paid user (sau COGS/fees).", "Công bố base/downside/upside; không lấy GMV thay revenue."],
    ], [3.6 * cm, 6.5 * cm, 7.0 * cm], True)]
    story += h3("Ba kịch bản vận hành cần chốt bằng spreadsheet")
    story += [table(["Kịch bản", "Giả định", "Quyết định quản trị"], [
        ["Downside", "D7 thấp, free usage cao, paid conversion thấp, AI/runner cost cao.", "Đóng bề mặt tốn cost, giảm quota/feature flag, không scale paid acquisition."],
        ["Base", "Pilot đạt completion/self-correction gate, COGS trong quota, conversion theo giả định Vòng 2.", "Mở cohort tiếp, thử pricing/marketing nhỏ, theo dõi margin."],
        ["Upside", "Retention/referral tốt và Campus partner xác nhận nhu cầu.", "Thêm content/teacher governance trước payment/broad rollout; tăng capacity có load test."],
    ], [3.1 * cm, 7.3 * cm, 6.7 * cm])]
    story += [PageBreak()]

    story += h2("4.2. Roadmap 3 tháng / 6 tháng / 1 năm")
    story += [table(["Thời điểm", "Outcome", "Hạng mục / gate"], [
        ["0–3 tháng", "MVP đáng tin và pilotable", "Public HTTPS; one Deque/Python lesson; source snapshot; actual persistence; safe runner adapter; Socratic policy; consent/RBAC; E2E/security/load/backup; pilot 30–50 với no invented metrics."],
        ["3–6 tháng", "Củng cố learning loop và integrity", "Mindmap/Master Graph, multi-lesson/OOP anchor, VARK experiments, GitHub OAuth/MOSS review, teacher/Campus governance, cohort analytics; validate Student Plus/Pro."],
        ["6–12 tháng", "Scale có kiểm soát", "League/XP/Hearts/recovery, community moderation, checkout/Campus contract, ads/affiliate allow-list A/B, provider optimization, multi-tenant compliance, seed funding readiness."],
    ], [2.6 * cm, 4.4 * cm, 10.1 * cm])]
    story += h3("Điều kiện mở rộng")
    story += [table(["Mở rộng", "Chỉ mở khi"], [
        ["Nhiều course/content", "Một vertical slice đạt ổn định, source authoring/review/versioning và lesson evidence pipeline có owner."],
        ["Gamification/community", "Có anti-abuse/moderation/completion gate; không khuyến khích copy answer hoặc dark pattern."],
        ["Payment/Campus", "Data governance, DPA/contract, invoice/refund/tax, security review, support runbook và clear entitlement."],
        ["Ads/affiliate", "Consent/minor safety, allowed surfaces, frequency cap/blacklist, retention rollback và policy review hoạt động."],
        ["AI scale", "Cost observability, provider comparison, quota ledger, fallback, latency/SLO và red-team result."],
    ], [5.0 * cm, 12.1 * cm])]
    story += [PageBreak()]

    # Appendices
    story += h1("PHỤ LỤC A. Traceability và trạng thái triển khai")
    story += [P("Ma trận đầy đủ nằm trong <b>CodeMind_Round3_Traceability.md</b>. Tóm tắt: không có capability Vòng 2 nào bị xóa; mỗi capability được phân loại thành P0 live, design/spec hay roadmap có điều kiện. Sự phân loại này giữ nguyên tinh thần phân tích thiết kế và hệ thống thông tin: process, data, role, control và bằng chứng phải đi cùng nhau.")]
    story += [table(["Nhóm", "Trạng thái được phép ghi trong release"], [
        ["P0 live", "Demo identity/consent, lesson/source/term/concept/practice/Socratic/evidence, teacher read-only summary — chỉ khi route/UI/test runtime có bằng chứng."],
        ["P1 hardening", "Quota ledger, source fallback, retry/recovery, analytic dashboard/seed content, privacy workflow — release note cần tách rõ “code” và “verified deployment”."],
        ["P2 roadmap", "Mindmap đầy đủ, VARK, GitHub OAuth/MOSS, gamification/community, pricing/checkout, Campus full, ads/affiliate runtime."],
        ["External evidence", "Public URL, demo role credentials, deployment config, pilot/D7, provider costs, legal/policy approval; không thể được suy ra từ Figma hoặc file local."],
    ], [4.3 * cm, 12.8 * cm])]
    story += h2("Compliance log")
    story += [table(["Yêu cầu", "Cách xử lý"], [
        ["Proposal PDF", "Đã tạo theo heading Template: I/II/III/IV; tối đa 60 trang nội dung theo thông báo mới; kiểm byte/page count sau generate."],
        ["Dung lượng", "Mục tiêu <30 MB theo đề bài gốc. PDF chỉ chứa vector/text, không nhúng asset nặng."],
        ["Filename", "`[KHOINGUYEN - VONG 3] - CodeMind.pdf`; đổi `CodeMind` nếu tên đội chính thức khác."],
        ["MVP URL/accounts", "Không bịa URL/password. Phải điền sau deploy và test incognito."],
        ["Video/slide", "Chủ sở hữu dự án yêu cầu không tạo trong task này; vẫn là hạng mục chính thức theo BTC và cần người chịu trách nhiệm xử lý."],
    ], [3.6 * cm, 13.5 * cm])]
    story += [PageBreak()]

    story += h1("PHỤ LỤC B. Checklist xác nhận trước khi gọi là “hoàn tất để nộp”")
    checklist = [
        ["MVP public", "URL HTTPS mở từ anonymous/incognito; không dùng localhost/máy cá nhân; frontend/backend/API response ổn định."],
        ["Demo role", "Student/Instructor/Content admin thao tác được bằng UI; role matrix, reset account/demo seed và các deny path đã test."],
        ["Happy path", "Official source → concept → code 4/5 → Socratic/hint → 5/5 → evidence chạy end-to-end."],
        ["No overclaim", "Mọi screen static Figma/catalog có badge prototype/roadmap; không đưa vào judge demo như chức năng live."],
        ["Architecture", "Runtime thực khớp diagram/ERD/API; Postgres/Redis/runner/AI adapter được mô tả đúng, migration/health/pass."],
        ["Privacy/security", "RBAC+consent+deny audit, token/secret/CORS/rate limit, lifecycle/deletion, hidden test protection, security evidence."],
        ["Reliability", "E2E/recovery, load 50 VU, backup/restore, rollback, monitoring/log redaction có artifact."],
        ["Pilot", "Cohort/consent/date/definitions/limitations documented; nếu chưa chạy thì ghi thẳng chưa có số liệu, không dùng số giả."],
        ["Proposal", "Đã điền team/mentor/members/URL; render QA, page/dung lượng check, link mở public, filename đúng cú pháp."],
    ]
    story += [table(["Gate", "Definition of Done"], checklist, [4.0 * cm, 13.1 * cm])]
    story += [note("Chỉ khi mọi gate trên có bằng chứng mới được ghi “dự án hoàn chỉnh để nộp”. Việc source code compile hoặc Figma đủ frame không tự động đóng gate deployment, security, role experience hay pilot.", True)]
    story += h2("Nguồn nội bộ đã dùng")
    story += [P("(1) `CodeMind - FundFlow.docx` — báo cáo Vòng 2 của đội; (2) `[KHỞI NGUYÊN] ĐỀ BÀI VÒNG 3.pdf`; (3) thông báo làm rõ của Ban Tổ chức do chủ sở hữu dự án cung cấp; (4) Figma Code Mind Beta, các frame/mapping được kiểm tra qua Figma MCP; (5) repository MVP, README/progress log, data specification workbook. Không có số liệu web mới được tự thêm vào báo cáo này.")]
    return story


def main() -> None:
    global S
    register_fonts()
    S = make_styles()
    OUT_DIR.mkdir(exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT_PATH), pagesize=A4, rightMargin=1.45 * cm, leftMargin=1.45 * cm,
        topMargin=1.55 * cm, bottomMargin=1.65 * cm, title="CodeMind — Đề án phát triển sản phẩm Vòng 3",
        author="CodeMind team", subject="Khởi Nguyên 2026 — Round 3 detailed proposal",
    )
    doc.build(build_story(), onFirstPage=cover_footer, onLaterPages=footer)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
