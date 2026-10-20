# Thư Mục Đề Xuất Nâng Cấp Mã Nguồn (Tool Upgrade Proposals)

Thư mục này lưu trữ các bản thiết kế đề xuất cải tiến mã nguồn được sinh ra từ **Giai đoạn 3 (Tự Tái Học và Nâng Cấp - Self-Upgrade)** của hệ thống *Self-Learning from Experience Loop*.

## Quy Chuẩn Đề Xuất (Proposal Format)
Mỗi đề xuất được đặt tên theo định dạng: `PROPOSAL_CYCLE_{CYCLE_NUMBER}_{TOOL_NAME}_{TIMESTAMP}.md`

Cấu trúc tài liệu đề xuất:
1. **Bối Cảnh & Vấn Đề Thực Tế**:
   - Dẫn chứng từ các bản ghi `execution_traces.jsonl` hoặc bài học trong `learned_heuristics.md`.
2. **Điểm Thừa / Điểm Thiếu / Điểm Gây Chậm**:
   - Phân tích chi tiết đoạn code cần loại bỏ, hàm cần tái cấu trúc hoặc chức năng mới cần bổ sung.
3. **Kết Quả Đối Chiếu Benchmark**:
   - Tác động đo lường đối với các tiêu chí trong `benchmark_tests.json`.
4. **Mã Nguồn Cải Tiến (Diff Block)**:
   - Đoạn code thay đổi rõ ràng (`-` dòng cũ, `+` dòng mới).
5. **Trạng Thái Duyệt**:
   - `[Chờ duyệt]` / `[Đã duyệt & Đã merge vào chu kỳ X]`.
