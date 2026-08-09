from ..domain.models import Lesson, LessonStep, SourceVersion, utc_now


def build_demo_lesson() -> Lesson:
    return Lesson(
        slug="deque",
        version=1,
        title="Giữ lịch sử truy cập với deque",
        objective="Tự đọc tài liệu, nối khái niệm và sửa mã để vượt qua 5 bài kiểm tra.",
        source=SourceVersion(
            id="source_version_python312_deque",
            source_id="python_collections_deque",
            version_label="Python 3.12",
            title="collections.deque — Python documentation",
            url="https://docs.python.org/3.12/library/collections.html#collections.deque",
            checksum="sha256:codemind-demo-python312-deque",
            retrieved_at=utc_now(),
            excerpt="deque hỗ trợ thêm/xóa ở hai đầu; maxlen giới hạn số phần tử được giữ lại.",
        ),
        steps=[
            LessonStep(1, "objective", "Mục tiêu", "Biết mình sẽ tạo gì và vì sao bài này hữu ích."),
            LessonStep(2, "source", "Đọc nguồn", "Tự chọn thuật ngữ trong tài liệu chính thức."),
            LessonStep(3, "concept", "Nối khái niệm", "Nối deque, append và maxlen thành một ý hoàn chỉnh."),
            LessonStep(4, "practice", "Thực hành", "Sửa mã và chạy năm bài kiểm tra."),
            LessonStep(5, "ai", "Nhận gợi ý", "Hỏi AI theo cách gợi mở, không nhận đáp án hoàn chỉnh."),
            LessonStep(6, "review", "Xem bằng chứng", "So sánh mã trước/sau và lưu kết quả học."),
        ],
        expected_concept_pairs={
            ("deque", "append", "thêm phần tử"),
            ("deque", "maxlen", "giới hạn số phần tử"),
        },
        hints={
            1: "Hãy kiểm tra cấu trúc dữ liệu đang dùng có giữ được thứ tự thêm vào không.",
            2: "Tìm tham số giới hạn số phần tử trong phần khởi tạo deque.",
            3: "Thử tạo deque(maxlen=3), thêm bốn giá trị rồi quan sát ba giá trị cuối.",
        },
    )
