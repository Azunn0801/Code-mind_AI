# CodeMind MVP — Pilot Protocol và mẫu báo cáo kết quả

**Phiên bản:** 1.0  
**Ngày lập:** 09/08/2026  
**Trạng thái:** Chưa tuyển cohort / chưa có số liệu. Tài liệu này là protocol, không phải báo cáo traction.

## 1. Mục tiêu và quyết định cần trả lời

Pilot kiểm định một lát cắt học Deque/Python theo learning loop: nguồn chính thức → thuật ngữ → concept → code/test → Socratic hint → evidence. Pilot không nhằm chứng minh toàn bộ 142 frame Figma hay các module roadmap.

| Câu hỏi | Chỉ số | Ngưỡng ra quyết định đề xuất |
|---|---|---:|
| Người mới có đi hết learning loop không? | Lesson completion = completed sessions / started sessions | ≥60% |
| Người học có tự sửa sau khi fail thay vì nhận đáp án? | Self-correction = complete session có fail→pass sau ≥1 attempt và không có full-solution policy breach | ≥50% số phiên hoàn thành |
| Source Reader có được dùng không? | Source engagement = có term selection + concept attempt / started sessions | ≥70% |
| Người học có quay lại không? | D7 = user quay lại ngày 7 ±1 / activated users | ≥20% |
| MVP có cản trở trải nghiệm không? | Critical blocked session / started sessions | <2% |

Các ngưỡng chỉ dùng để quyết định tiếp tục/sửa/thu hẹp cohort, không phải cam kết kết quả.

## 2. Thiết kế pilot

- **Cohort 1:** 30–50 sinh viên năm 1–2 ngành CNTT/kỹ thuật; ưu tiên người chưa học sâu về `deque`.
- **Thời gian:** 7 ngày tính từ lần active đầu tiên; thêm 1 buổi onboarding 10–15 phút, không hướng dẫn đáp án.
- **Tuyển mẫu:** CLB/lớp đối tác hoặc danh sách tự nguyện. Không dùng thông tin điểm số/chấm thi để ép tham gia.
- **Đơn vị phân tích:** người dùng pseudonymous và learning session; không báo cáo tên/email/raw code.
- **Bản release:** ghi URL, commit/image digest, environment, adapter runner/AI, source version, ngày giờ seed và người release vào pilot log.

## 3. Consent và bảo vệ người tham gia

1. Hiển thị mục đích pilot, dữ liệu thu, retention, contact owner và quyền dừng/xóa trước khi dùng.
2. `academic_integrity` là consent riêng cho học tập; `teacher_visibility` là tùy chọn riêng, không là điều kiện tham gia pilot.
3. Không thu password, dữ liệu định danh nhạy cảm hoặc device fingerprint trong P0. Không dùng raw code/prompt cho bài đăng truyền thông.
4. Với người dưới 18 tuổi, cần quy trình consent phù hợp theo chính sách/pháp luật của đơn vị trước khi tuyển; không chạy behavioral ads.
5. Chỉ export aggregate/pseudonymous event. Mọi request access/deletion có owner, mã theo dõi và SLA được công bố.

## 4. Kịch bản và instrumentation

### Happy path bắt buộc

1. Mở URL public bằng Student demo hoặc account pilot riêng.
2. Đồng ý consent cần thiết; bắt đầu lesson Deque/Python 3.12.
3. Chọn `maxlen` trong source đã pin; gửi concept check.
4. Nộp bản 4/5; hỏi AI theo cách riêng; mở hint theo thứ tự.
5. Tự thêm guard, đạt 5/5 và xem evidence.
6. Tùy chọn: bật teacher visibility, để Instructor xác nhận summary read-only không chứa raw code.

### Event tối thiểu

`demo_login_succeeded`, `learning_session_started`, `source_opened`, `term_selected`, `concept_check_submitted`, `submission_queued`, `submission_finished`, `ai_answer_refused`, `hint_opened`, `lesson_completed`, `self_correction_achieved`, `consent_updated`, `instructor_evidence_viewed`, `instructor_access_denied`, `d7_return`.

Mỗi event chỉ mang ID pseudonymous, session ID, lesson/source version, timestamp và property allow-list trong workbook. Không đưa email, raw code, raw prompt, hint text hay expected hidden test vào analytics.

## 5. Bảng log pilot — điền sau mỗi release/cohort

| Trường | Giá trị cần điền |
|---|---|
| URL + version/image digest | `[CHƯA CÓ]` |
| Ngày bắt đầu/kết thúc | `[CHƯA CÓ]` |
| Môi trường, repository/runner/AI mode | `[CHƯA CÓ]` |
| Cỡ cohort mời / active / phân tích | `[CHƯA CÓ]` |
| Tiêu chí loại trừ dữ liệu | `[CHƯA CÓ]` |
| Completion / self-correction / source engagement / D7 | `[CHƯA CÓ]` |
| Số incident và loại recovery | `[CHƯA CÓ]` |
| Consent visibility / instructor allow-deny check | `[CHƯA CÓ]` |
| Phản hồi định tính chủ đề chính | `[CHƯA CÓ]` |
| Giới hạn, bias, owner sign-off | `[CHƯA CÓ]` |

## 6. Triage và tiêu chí dừng/mở rộng

| Tín hiệu | Hành động |
|---|---|
| Có policy breach (AI đưa đáp án hoàn chỉnh) hoặc lộ hidden test/PII | Dừng cohort, vô hiệu hóa feature liên quan, preserve audit, remediation trước khi tiếp tục. |
| Critical blocked session ≥2% | Ưu tiên recovery/reliability, không tăng acquisition. |
| Completion thấp nhưng source engagement tốt | Usability test từng bước; đơn giản copy/transition trước khi thêm gamification. |
| Self-correction thấp | Review hint ladder/prompt, không nới policy thành đưa đáp án. |
| D7 thấp | Phỏng vấn cohort, kiểm tra giá trị bài tiếp theo; không scale marketing/ads. |
| Chỉ số đạt threshold và không có security incident | Mở cohort 100–300 với release note, cost cap và monitoring. |

## 7. Artefact cần lưu cùng kết quả

- File aggregate metrics có định nghĩa công thức, query version và timestamp export.
- Release checklist incognito, E2E/recovery, security/load/backup evidence tương ứng môi trường pilot.
- Danh sách issue đã triage (không PII), owner, severity, decision fix/defer.
- Consent wording/policy version, link privacy request, contact owner.
- Summary kết quả một trang: cohort, số liệu thực, limitations, quyết định roadmap.

Không thay thế các hàng `[CHƯA CÓ]` bằng số ước lượng. Nếu pilot chưa chạy trước hạn nộp, report phải ghi rõ “pilot protocol đã sẵn sàng; chưa có số liệu vận hành” thay vì claim retention/traction.
