# Quy Tắc Tự Học Liên Tục Từ Thực Tế (Workspace Rule)

## Nguyên Tắc Bắt Buộc:
1. **Luôn Ghi Nhận Kinh Nghiệm (Continuous Trace Recording)**:
   - Sau bất kỳ thao tác nào chạy tool, thử nghiệm script hoặc kiểm thử (`main.py`, `video_hunter.py`, `ai_brain.py`, `video_editor.py`, `tiktok_uploader.py`), bạn PHẢI tự động ghi nhận một bản ghi vào `.agents/experience_memory/execution_traces.jsonl`.
   - Nếu phát hiện mẹo hay, cách tối ưu mới, hoặc lỗi tiềm ẩn, hãy cập nhật ngay vào `.agents/experience_memory/learned_heuristics.md`.

2. **Chế Độ Kênh Tương Ứng**:
   - Khi chạy ở chế độ **[Xây Kênh Kéo Follow]** (`is_affiliate=False`):
     + Voiceover và caption KHÔNG ĐƯỢC chứa các từ bán hàng/giỏ hàng.
     + Kêu gọi tương tác, thả tim, follow.
   - Khi chạy ở chế độ **[Có Affiliate Bán Hàng]** (`is_affiliate=True`):
     + Kêu gọi giỏ hàng góc trái, đẩy mạnh chuyển đổi.

3. **Quy Trình Nâng Cấp Code (Self-Upgrade Protocol)**:
   - Trước khi sửa mã nguồn lớn của tool, hãy lập bản đề xuất (Proposal) trong `.agents/evals/proposals/`.
   - Sau khi người dùng duyệt, áp dụng thay đổi, chạy lại test suite, và ghi nhận hoàn thành chu kỳ học.
