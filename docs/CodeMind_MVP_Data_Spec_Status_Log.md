# CodeMind MVP — Data Specification Status Log

**Phiên bản workbook:** v1.1  
**Ngày đồng bộ:** 09/08/2026  
**Phạm vi kiểm tra:** repository, tài liệu `docs/`, frontend/backend chạy cục bộ. Không suy diễn trạng thái deploy, pilot hay dịch vụ bên ngoài từ file cấu hình.

## Quy ước trạng thái

| Trạng thái | Cách hiểu khi xuất hiện trong workbook |
|---|---|
| `Local verified` | Có implementation và bằng chứng kiểm tra cục bộ. Không đồng nghĩa public HTTPS, production, pilot hoặc kiểm thử tải. |
| `Partial` | Đã có một phần code/thiết kế/bằng chứng local, nhưng chưa đạt toàn bộ Definition of Done hoặc còn dependency quan trọng. |
| `Planned` | Chưa có bằng chứng thực thi đủ trong repository; chỉ có kế hoạch, tài liệu hoặc hạ tầng khung. |
| `Deferred` | Chủ động để ngoài P0/current critical path; cam kết sản phẩm vẫn được giữ trong roadmap. |
| `External / owner` | Cần quyền cloud, tài khoản dịch vụ, dữ liệu thực tế hoặc thao tác do đội sở hữu thực hiện; repository không thể tự xác nhận. |

## Bằng chứng hiện có tại thời điểm đồng bộ

- Vertical slice local: demo access, consent, lesson Deque sáu bước, source/concept/practice, evidence và UI instructor/content-admin gọi API.
- Backend local: contract checker ghi nhận **20 route**; suite pytest có **12 test pass**, gồm signed demo token/expiry, consent grant/revoke, source-term validation, idempotency, adapter PostgreSQL/local và readiness; có persistence file, Socratic canned gateway, hint ladder, citation và analytics đã redacted.
- Frontend local: lint/build đã được ghi trong `CodeMind_Progress_Log.md`; các route demo là luồng API-backed. Những catalogue/Figma route ngoài P0 không được dùng làm bằng chứng runtime.

## Điều chưa được phép suy diễn là đã hoàn tất

- Không có URL HTTPS công khai, tài khoản demo production, smoke incognito trên deployment hoặc receipt nộp bài.
- Adapter PostgreSQL và kiểm tra local đã có bằng chứng, nhưng PostgreSQL qua Compose/staging cùng migration runtime, Redis, isolated code runner, AI provider thực, rate limiting, load 50 VU, backup/restore, security scan và pilot/D7 chưa có evidence đóng.
- Video và slide là yêu cầu chính thức của Ban Tổ chức nhưng được chủ dự án loại khỏi scope triển khai hiện tại; vì vậy chúng được ghi `External / owner`, không được hiểu là đã nộp.
- Bản báo cáo chi tiết dùng giới hạn mới **≤60 trang nội dung** (không tính bìa/phụ lục); giới hạn **≤30 MB** từ đề gốc vẫn được giữ. Slide dùng giới hạn **≤20 trang**; video **≤3 phút**.

## Quy tắc cập nhật tiếp theo

Chỉ chuyển sang `Local verified` khi có command/test hoặc thao tác local lặp lại được. Chỉ chuyển sang trạng thái release/deployment sau khi có URL, thời điểm kiểm tra, role/account matrix và bằng chứng browser incognito. Khi claim thay đổi, cập nhật đồng thời `09_Traceability`, `11_Implementation`, `CodeMind_Progress_Log.md` và báo cáo PDF.
