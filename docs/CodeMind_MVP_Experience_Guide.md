# CodeMind MVP — Hướng dẫn trải nghiệm và tài khoản demo

**Cập nhật:** 09/08/2026  
**Mục đích:** chuẩn bị phần “đường dẫn trải nghiệm MVP, tài khoản demo và quyền” trong bộ bài Round 3. Đây là tài liệu vận hành phát hành, **không phải** nơi lưu bí mật.

## 1. Trạng thái trung thực trước khi phát hành

- P0 hiện có bằng chứng chạy **local** cho luồng người học: demo auth → consent → nguồn → concept check → mã/test mô phỏng → AI Socratic/hint → evidence.
- Chưa có URL public HTTPS, account production, browser E2E trên deployment, PostgreSQL runtime, runner cô lập hay pilot. Vì vậy không được dùng `localhost`, token local hoặc màn hình catalog Figma làm bằng chứng nộp bài.
- `Student`, `Teacher` và `Admin` trong danh mục Figma phần lớn vẫn là UI/mock. Luồng `/#/demo/access → ... → /demo/evidence` là vertical slice nối API; có màn demo tối thiểu cho Instructor summary và Content admin analytics, còn dashboard Teacher/Admin đầy đủ vẫn chưa là web production.
- Công cụ kiểm thử mã hiện là `SimulatedDequeRunner`: nó kiểm tra mẫu mã theo rule cố định và **không thực thi mã không tin cậy**. Khi demo, phải gọi đúng tên này; không mô tả là sandbox/runner production.

Nếu một hàng trong bảng phát hành dưới đây còn `[CHƯA CÓ]`, trạng thái là **chưa sẵn sàng nộp MVP công khai**.

## 2. Phiếu bàn giao phát hành — điền sau khi deploy

| Hạng mục bắt buộc | Giá trị phát hành | Trạng thái hiện tại | Bằng chứng cần lưu |
|---|---|---|---|
| URL MVP công khai HTTPS | `[CHƯA CÓ — điền URL đã deploy]` | Chưa deploy | URL mở được ở cửa sổ ẩn danh và mạng ngoài đội |
| Thời điểm release / mã phiên bản | `[CHƯA CÓ]` | Chưa release | commit/tag hoặc image digest, người phát hành |
| Môi trường | `[CHƯA CÓ — staging hoặc production]` | Local-only | kết quả `/health/live` và `/health/ready` đã redacted |
| Student demo — email/username | `[CẤP RIÊNG SAU KHI DEPLOY]` | Chưa có account production | owner xác nhận role `student` |
| Student demo — mật khẩu | `[KHÔNG GHI VÀO GIT/TÀI LIỆU CÔNG KHAI]` | Chưa có | gửi qua kênh riêng cho Ban Giám khảo |
| Instructor demo — email/username | `[CẤP RIÊNG SAU KHI DEPLOY]` | Chưa có account production | owner xác nhận role `instructor` |
| Instructor demo — mật khẩu | `[KHÔNG GHI VÀO GIT/TÀI LIỆU CÔNG KHAI]` | Chưa có | gửi qua kênh riêng cho Ban Giám khảo |
| Content admin demo — email/username | `[CẤP RIÊNG SAU KHI DEPLOY]` | Chưa có account production | owner xác nhận role `content_admin` |
| Content admin demo — mật khẩu | `[KHÔNG GHI VÀO GIT/TÀI LIỆU CÔNG KHAI]` | Chưa có | gửi qua kênh riêng cho Ban Giám khảo |
| Người trực hỗ trợ trong thời gian chấm | `[CHƯA CÓ]` | Chưa phân công | tên, kênh liên hệ, múi giờ |

### Danh tính local chỉ để kiểm thử kỹ thuật

Seed local hiện có ba email `student.demo@codemind.local`, `instructor.demo@codemind.local` và `admin.demo@codemind.local`. API local phát token demo được ký HMAC, có hạn dùng, qua `POST /v1/demo/session`; không có mật khẩu. Đây là **adapter demo nội bộ**, không phải thông tin tài khoản để nộp hay cơ chế xác thực production.

Không sao chép token local vào video, PDF, link chia sẻ hoặc ticket của Ban Giám khảo. Khi có auth production, tạo account riêng cho đợt chấm, phân role tối thiểu, đặt thời hạn/khả năng thu hồi và bàn giao bí mật qua kênh riêng.

## 3. Ma trận role và điều có thể kiểm tra

| Role | Điều được phép kiểm tra trong P0 | Giới hạn phải nói rõ | Tiêu chí chấp nhận sau deploy |
|---|---|---|---|
| Student | Tạo phiên học `deque`, đồng ý cam kết, chọn `maxlen`, concept check, nộp mã, hỏi AI Socratic, mở hint 1→3, tạo evidence | Một lesson; runner mô phỏng; AI canned/offline; không phải OAuth/AI provider thật | Hoàn tất 6 bước; reload không làm mất phiên; evidence chỉ xuất hiện sau concept đạt và 5/5 test |
| Instructor | Dùng màn demo read-only để đọc summary API của phiên cùng tổ chức khi người học bật `teacher_visibility` | Catalog Teacher đầy đủ chưa là dashboard production; summary không trả raw code | Đúng role + consent được phép; tắt/không cấp consent phải bị `403` và không lộ evidence |
| Content admin | Dùng màn demo read-only để đọc analytics event đã redacted qua API local | Catalog Admin đầy đủ còn mock; chưa có quản trị campus hay dashboard production | Student không đọc được analytics; event không chứa raw code hoặc full AI question |

Không trình diễn một route `/#/design/...`, `/#/student`, `/#/teacher` hoặc `/#/admin` như bằng chứng đã có backend nếu chưa có release note/test xác nhận route đó đã nối API.

## 4. Kịch bản demo P0 cho Ban Giám khảo — tối đa 3 phút

Kịch bản này được dùng **sau khi** URL, account và checklist ẩn danh ở phần 5 đều đạt. Hãy reset dữ liệu demo trước mỗi lượt và chuẩn bị sẵn mã lỗi/corrected mẫu; không sửa dữ liệu ngay trong lúc chấm.

| Thời lượng | Thao tác thực hiện | Điểm cần nói hoặc quan sát |
|---:|---|---|
| 00:00–00:15 | Mở `[URL MVP công khai]` bằng cửa sổ ẩn danh; đăng nhập Student demo được cấp riêng. | Cho thấy đây là URL HTTPS, không phải localhost. Không đọc mật khẩu/token trên màn hình. |
| 00:15–00:30 | Ở Setup, bật “Tôi cam kết tự thực hiện bài học”; bật `teacher_visibility` **chỉ** nếu muốn kiểm tra Instructor ở bước sau. Bắt đầu lesson. | Cam kết học tập là bắt buộc; quyền giảng viên là lựa chọn tách biệt. |
| 00:30–00:48 | Đi qua Objective và Source; chọn `maxlen`, mở liên kết Python docs. | Liên kết nguồn chính thức phải bấm được. Chỉ gọi source là “đã pin/xác thực” khi release đã có snapshot/checksum được kiểm chứng; seed local hiện chưa là bằng chứng đó. |
| 00:48–01:05 | Ở Concept, chọn `deque → maxlen`, gửi concept check. | Backend hiện chấm hai quan hệ seed của lesson; chỉ chuyển tiếp khi đạt. |
| 01:05–01:30 | Ở Practice, chạy mã lỗi mẫu mặc định. Kết quả dự kiến là 4/5 vì chưa kiểm tra `page` rỗng trước `history.append(page)`. | Nói rõ đây là rule-based simulated runner của P0 local, không phải thực thi code người dùng trong container. |
| 01:30–01:55 | Hỏi “Vì sao history vẫn có thể nhận chuỗi rỗng?”, cho thấy AI trả lời theo hướng gợi mở, link citation và mở Hint 1. | AI không được đưa full answer. Hiển thị quota còn lại; không cố vượt 3 lượt/phiên. |
| 01:55–02:25 | Thêm guard trước append rồi chạy lại: `if not page: return list(history)`. Kết quả dự kiến 5/5; ứng dụng tạo evidence. | Chỉ evidence khi đã có thuật ngữ, concept đạt và 5/5. |
| 02:25–02:45 | Mở Evidence để chỉ before/after, test count, hint levels và selected terms; reload một lần nếu môi trường release đã có persistence được kiểm chứng. | Không nói persistence PostgreSQL nếu release vẫn chạy file adapter. |
| 02:45–03:00 | (Tùy chọn, không thay cho demo Student) đăng nhập Instructor và gọi summary của **chính session đã consent**. | Dùng đúng API/UI đã release. Nếu chỉ có catalog Teacher, nêu rõ phần đó chưa phải chức năng live và dừng ở bằng chứng P0. |

Mã mẫu sửa để tạo 5/5 với runner local:

```python
from collections import deque

history = deque(maxlen=3)

def visit(page):
    if not page:
        return list(history)
    history.append(page)
    return list(history)
```

## 5. Checklist nghiệm thu bằng cửa sổ ẩn danh

Người kiểm tra không dùng session, cache hay quyền của thành viên đội. Đánh dấu ngày, người chạy, URL và ảnh/log kết quả ở release log riêng.

### A. Truy cập và bảo mật tối thiểu

- [ ] URL HTTPS thật, domain công khai, mở được ở cửa sổ ẩn danh và từ mạng không thuộc đội.
- [ ] Không có warning certificate/mixed content, không redirect về `localhost` hay IP private.
- [ ] Không lộ token demo, password, connection string, API key hoặc stack trace trên browser/network response.
- [ ] Bản deploy không bật công cụ debug/Swagger công khai nếu chính sách release không cho phép.
- [ ] CORS chỉ cho phép origin frontend đã phê duyệt; không dùng `*` cùng credential.

### B. Student happy path

- [ ] Student demo đăng nhập được và role hiển thị/được kiểm tra đúng.
- [ ] Không bật `academic_integrity` thì tạo session bị từ chối; bật rồi mới vào lesson.
- [ ] Chọn `maxlen`, gửi concept, nộp mã lỗi 4/5, dùng một AI hint, sửa mã 5/5 và nhận evidence.
- [ ] Refresh ở ít nhất một bước trước khi hoàn tất vẫn khôi phục đúng phiên; ghi rõ adapter persistence đã kiểm chứng.
- [ ] Citation AI mở được link nguồn chính thức; hint 2/3 không mở trước hint trước đó.
- [ ] Lượt hỏi AI thứ tư trong cùng session bị chặn rõ ràng (`429 ai_quota_exceeded`); bài học vẫn tiếp tục được không cần AI.
- [ ] Nộp lại cùng `Idempotency-Key` không sinh kết quả/record trùng.

### C. RBAC, consent và dữ liệu

- [ ] Student không có quyền xem analytics event; request bị từ chối, không lộ dữ liệu.
- [ ] Instructor chỉ xem được summary đúng organization và session có `teacher_visibility=true`; kiểm tra tối thiểu một case bị từ chối.
- [ ] Summary Instructor không chứa `before_code`/`after_code`; Content admin chỉ nhận event đã redacted.
- [ ] Nút/yêu cầu xóa dữ liệu tạo request có mã theo dõi; quy trình xử lý ngoài hệ thống phải có owner và thời hạn trước khi mở pilot.

### D. Ranh giới chứng cứ

- [ ] Nếu runner còn `simulated`, mọi tài liệu/demo gắn nhãn đúng như vậy; không gọi là sandbox thực thi.
- [ ] Nếu `REPOSITORY_MODE=file`, không gọi dữ liệu runtime là PostgreSQL.
- [ ] Nếu `AI_MODE=canned`, không gọi là provider/RAG production hay đưa ra số token/cost thật.
- [ ] Không trích số liệu pilot, D7, load, security scan hoặc backup/restore nếu chưa có log ngày chạy và người xác nhận.

## 6. Quy tắc bàn giao và khôi phục demo

1. Release owner tạo account chấm riêng; không dùng account cá nhân/thành viên.
2. Gửi URL + username + password qua kênh riêng, có ngày hết hạn và cách liên hệ hỗ trợ; PDF công khai chỉ ghi URL và hướng dẫn nhận credential khi cần.
3. Lưu một fixture session trước demo để có thể reset; ghi chính xác adapter dữ liệu đang dùng. Không xóa volume hoặc state file khi chưa sao lưu.
4. Nếu AI/source lỗi, dùng recovery state đã test; nếu lỗi chưa có recovery được kiểm chứng, dừng demo và ghi nhận lỗi thay vì tạo dữ liệu giả.
5. Sau đợt chấm, thu hồi account, export audit cần thiết, thực hiện retention/deletion theo chính sách đã công bố.

## 7. Điều kiện đóng hạng mục “MVP experience”

Chỉ đánh dấu hoàn tất khi có đủ URL public, ba account role thực, evidence ẩn danh của checklist, owner hỗ trợ, bản sao backup/restore đã test và bản mô tả trung thực các giới hạn đang còn. Video và slide không nằm trong phạm vi thực hiện hiện tại theo yêu cầu chủ dự án, nhưng vẫn là yêu cầu chính thức của Ban Tổ chức; không được coi bộ hồ sơ Round 3 chính thức là đủ nếu chưa tự bổ sung/được miễn hai hạng mục đó.
