---
name: tool-learner-evaluator
description: Bộ não điều phối chu trình tự học liên tục từ thực tế (Self-Learning from Experience Loop) kết hợp cơ chế tự thực thi lặp cho đến khi đạt chuẩn và tự động ghi Devlog + Push GitHub.
---

# Tool Learner & Evaluator Skill (Bộ Não Điều Phối Tự Học & Tiến Hóa Tool)

Skill này chịu trách nhiệm điều phối toàn bộ chu trình 5 giai đoạn: Thực thi lặp tự động (Autonomous Execution) -> Ghi nhận kinh nghiệm (Experience Trace) -> Thẩm định phản tư (Evaluator) -> Nâng cấp an toàn (Safe Self-Upgrade) -> Tự động ghi Devlog và Push GitHub.

---

## 1. Giai Đoạn 1: Cơ Chế Thực Thi Lặp Cho Đến Khi Đạt Chuẩn (Autonomous Execution Loop)

Khi được giao bất kỳ nhiệm vụ nào yêu cầu chạy tool/script:

### Tiêu Chí Dừng (Exit Criteria)
Chỉ được phép dừng và báo cáo hoàn thành khi:
1. Tool chạy không sinh bất kỳ lỗi runtime/crash nào (`Exit Code = 0`).
2. Dữ liệu/kết quả đầu ra đáp ứng đúng 100% yêu cầu về mặt logic và cấu trúc (không rỗng, không sai format, không mất dữ liệu tiếng Việt/bảng biểu, thời lượng và kích thước hợp lệ).

### Quy Trình Lặp (Max Retries = 5 Lần)
```
  [Bắt đầu nhiệm vụ]
         |
         v
  [Bước 1: Chạy Tool Lần N (N <= 5)]
         |
         v
  [Bước 2: Kiểm Tra Kết Quả Đầu Ra (Verify Output)]
         |
    +----+----+
    |         |
    v (OK)    v (FAIL / CHƯA ỔN)
[DỪNG & LƯU]  +-> [KHÔNG dừng lại hỏi người dùng]
                  [Đọc trực tiếp Traceback / Phân tích nguyên nhân]
                  [Tự điều chỉnh ngay tham số, regex, thuật toán]
                  [Tăng retry_count, chạy lại Bước 1]
```
- Nếu chạm ngưỡng 5 lần mà vẫn chưa giải quyết được, tổng hợp toàn bộ các hướng đã thử và nguyên nhân gốc rễ để báo cáo điểm nghẽn cho người dùng.

---

## 2. Giai Đoạn 2: Cơ Chế Ghi Nhận Kinh Nghiệm (Sau Mỗi Lần Dùng Tool)

Sau mỗi phiên làm việc thực tế với bất kỳ tool nào:
1. **Append một dòng JSON vào `.agents/experience_memory/execution_traces.jsonl`** gồm các trường:
   - `timestamp`: Thời gian thực thi ISO.
   - `tool_name`: Tên tool và bài toán cụ thể vừa giải.
   - `retry_count`: Số lần phải chạy thử lại trước khi thành công.
   - `approach_and_fixes`: Phương pháp đã chọn và các bước tự sửa lỗi qua từng lần thử.
   - `metrics`: Thời gian chạy, kích thước dữ liệu xử lý, số lượng test/kết quả đạt được.
   - `reflection`: Tốc độ ra sao? Có mẹo xử lý nào hay không? Điểm gì đã gây lỗi ở các lần thử đầu?
   - `heuristics_derived`: Quy tắc mới được rút ra.
2. **Cập nhật `.agents/experience_memory/learned_heuristics.md`**:
   - Nếu phát hiện quy tắc hay hoặc cách vượt lỗi (ví dụ: fallback Shorts khi video review >90s, retry 503 Service Unavailable, tránh bóp tương tác kênh mới <1k follower), tự động ghi bổ sung vào mục chuyên đề tương ứng trong sổ tay.

---

## 3. Giai Đoạn 3: Cơ Chế Thẩm Định & Phản Tư (Evaluator)

Khi người dùng yêu cầu "Đánh giá và nâng cấp" hoặc kích hoạt evaluator:
1. Đọc lại toàn bộ:
   - `.agents/experience_memory/execution_traces.jsonl`
   - `.agents/experience_memory/learned_heuristics.md`
   - `.agents/evals/tools_registry.json`
   - `.agents/evals/benchmark_tests.json`
2. Tiến hành phản tư sâu trên mã nguồn:
   - Những lỗi từng khiến tool phải retry nhiều lần đã được xử lý triệt để trong code gốc chưa?
   - Có đoạn code/tham số tinh chỉnh nào đang viết thủ công mà đáng lẽ nên đóng gói thành mặc định trong tool không?
   - Có logic nào bị thừa thãi hoặc gây chậm chạp không?

---

## 4. Giai Đoạn 4: Tự Tái Học Và Nâng Cấp An Toàn (Self-Upgrade)

1. **Khởi tạo Đề xuất (Proposal)**:
   - Xuất file `.agents/evals/proposals/proposal_YYYYMMDD_<tool_name>.md`.
   - Trình bày rõ: Bối cảnh lỗi, phân tích thừa/thiếu, kết quả benchmark, và đoạn Diff code rõ ràng (`-` dòng cũ, `+` dòng mới).
2. **Nguyên Tắc An Toàn Tuyệt Đối**:
   - TUYỆT ĐỐI KHÔNG tự ý ghi đè vào tool gốc khi chưa có xác nhận từ người dùng.
   - Chỉ khi người dùng gõ xác nhận ("Duyệt" / "Merge"), mới hợp nhất bản nâng cấp vào tool gốc.
3. **Kiểm Định Hậu Nâng Cấp**:
   - Chạy lại `test_pipeline.py` và test suite liên quan để đảm bảo không có lỗi hồi quy (regression).

---

## 5. Giai Đoạn 5: Tự Động Ghi Devlog, Commit Và Push Lên GitHub

Mỗi khi hoàn thành một chu kỳ học/nâng cấp tool hoặc giải quyết xong một bài toán khó:
1. **Tạo Devlog**:
   - Tự động ghi file mới tại `docs/devlogs/devlog_YYYY-MM-DD.md` gồm 4 mục chuẩn hóa:
     + **1. Bối cảnh & Vấn đề thực tế (Context)**
     + **2. Bài học rút ra (Learned Heuristics)**
     + **3. Thay đổi kỹ thuật (Changelog & Technical Improvements)**
     + **4. Benchmark & Hiệu năng**
2. **Cập nhật Mục lục**:
   - Tự động thêm liên kết vào `docs/devlogs/README.md`.
3. **Tự động Push lên GitHub (Auto-Sync)**:
   - Chạy script:
     ```bash
     python .agents/skills/tool-learner-evaluator/scripts/sync_to_github.py \
       --title "<Tiêu đề Devlog>" \
       --tool "<Tên tool>" \
       --context "<Bối cảnh>" \
       --heuristics "<Bài học>" \
       --changelog "<Các thay đổi>" \
       --benchmark "<Kết quả benchmark>"
     ```
   - Script tự động:
     + Kiểm tra an toàn: Tuyệt đối không stage file nhạy cảm (`.env`, `chrome_profile/`, video tạm).
     + Chạy `git add docs/devlogs/ .agents/` (và các file tool vừa được duyệt nâng cấp).
     + Chạy `git commit -m "feat(tool-evolution): upgrade <tool-name> and update devlog [YYYY-MM-DD]"`.
     + Chạy `git push origin <current-branch>` (tự động `git pull --rebase` nếu có xung đột).
     + Báo cáo commit hash sau khi hoàn tất.
