# Devlog: Hệ Thống Google Flow Affiliate Director & Bộ Lọc Lách Kiểm Duyệt TikTok

- **Ngày ghi nhận**: 2026-10-21
- **Công cụ trọng tâm**: `affiliate_director.py`, `anti_detection_rules.md`
- **Hệ thống**: TikTok Affiliate Producer & AI Content Director (Google Flow)

---

## 1. Bối Cảnh & Vấn Đề Thực Tế (Context)
- Thuật toán TikTok ngày càng siết chặt các video re-up, cắt ghép từ Douyin hoặc YouTube Shorts, gắn cờ vi phạm *"Nội dung không nguyên bản / Unoriginal Content"* và bóp tương tác về 0 view, thậm chí hủy quyền gắn link TikTok Shop.
- Yêu cầu đặt ra: Xây dựng một quy trình sản xuất video hoàn toàn độc bản (Zero Re-up) bắt đầu từ **hình ảnh sản phẩm thực tế** được người dùng cung cấp.

---

## 2. Bài Học Rút Ra (Learned Heuristics)
- **Heuristic 1 (Phá vỡ Perceptual Hash - pHash)**: Thêm một lớp noise vi mô ngẫu nhiên (`noise=alls=6:allf=t+u`) kết hợp chỉnh nhẹ độ tương phản và bão hòa màu (`eq=contrast=1.05:saturation=1.06`) giúp mắt thường nhìn sản phẩm nổi bật hơn, đồng thời làm sai lệch hoàn toàn mã băm so khớp hình ảnh tĩnh của AI TikTok.
- **Heuristic 2 (Dynamic Ken Burns)**: Biến đổi ảnh tĩnh 2D thành chuỗi chuyển động camera 9:16 (1080x1920) với các góc cận, góc toàn và nhịp chuyển cảnh 2.5s-3.5s giúp duy trì tỷ lệ giữ chân người xem (Retention rate) cao.
- **Heuristic 3 (Metadata Cleanse)**: Cờ `-map_metadata -1` trong FFmpeg là bắt buộc để triệt tiêu mọi dấu vết metadata, EXIF và thông tin phần mềm sinh ảnh.
- **Heuristic 4 (TikTok Policy Compliance)**: Kịch bản tuyệt đối không dùng từ cam kết quá đà (*"100% hết bệnh", "chữa khỏi vĩnh viễn"*); tập trung vào Hook 3s đánh trúng nỗi đau thực tế và CTA giục giã bấm vào giỏ hàng góc trái màn hình.

---

## 3. Thay Đổi Kỹ Thuật (Changelog & Technical Improvements)
- Khởi tạo kiến trúc chống quét TikTok:
  + `.agents/tiktok_affiliate_evals/anti_detection_rules.md`: Bảng quy chuẩn kỹ thuật lách kiểm duyệt.
  + `.agents/tiktok_affiliate_evals/execution_traces.jsonl`: Lưu vết lịch sử xử lý ảnh sản phẩm và prompt GenAI.
  + `.agents/skills/tiktok-affiliate-director/SKILL.md`: Bộ não điều phối nhận ảnh, gọi Google Flow và kiểm định.
- Triển khai động cơ sản xuất:
  + `affiliate_director.py`: Module phân tích ảnh đa thể thức (Gemini 2.5 Vision), tự động tạo storyboard, sinh voiceover tiếng Việt dứt khoát, render video chuẩn dọc 1080x1920 và tự động kiểm định tuân thủ chính sách TikTok Shop.

---

## 4. Benchmark & Hiệu Năng (Performance Verification)
- **Chuẩn đầu ra video**: Định dạng MP4, độ phân giải 1080x1920 (9:16), 30fps, pixel format `yuv420p`, âm thanh AAC 192k.
- **Thời lượng tối ưu**: 20s - 30s (tốc độ đọc +10%), đảm bảo người xem nghe trọn vẹn Call-to-Action trước khi lướt qua.
- **Cơ chế tự sửa lỗi**: Tự động lặp lại (Autonomous retry loop) tối đa 5 lần nếu phát hiện lỗi kích thước hoặc vi phạm từ cấm, không làm phiền người dùng.
