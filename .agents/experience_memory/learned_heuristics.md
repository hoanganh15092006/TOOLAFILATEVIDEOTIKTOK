# Sổ Tay Tri Thức & Heuristics Tự Học (Learned Heuristics & Experience Memory)

> **Hệ thống**: Self-Learning from Experience Loop  
> **Cập nhật lần cuối**: 2026-10-21  
> **Nguyên tắc cốt lõi**: Tích lũy bài học thực chiến từ cả ca thành công, ca tối ưu và ca lỗi/vấp váp để liên tục tinh chỉnh và nâng cấp bộ công cụ tự động hóa video TikTok.

---

## 1. Định Vị Mục Tiêu Kênh: [Có Affiliate >1K FL] vs [Xây Kênh Kéo Follow (<1K FL)]

### Heuristic 1.1: Tránh bóp tương tác kênh mới (<1K Follower)
- **Vấn đề**: Kênh mới dưới 1000 follower chưa mở được tính năng gắn link TikTok Shop. Nếu kịch bản nhắc đến "giỏ hàng", "link bio", "mua ngay", "giá tiền", thuật toán TikTok sẽ quét là nội dung thương mại trái phép hoặc spam, dẫn tới 0 view / bóp tương tác vĩnh viễn.
- **Quy tắc đúc kết**:
  + Khi mục tiêu là **[Xây Kênh Kéo Follow]**:
    - Call to Action (CTA) **bắt buộc** phải là: Thả tim, lưu video, bình luận ý kiến ("Bạn có muốn thử không? Bình luận bên dưới nhé!"), follow kênh để xem mẹo hay mỗi ngày.
    - Tuyệt đối cấm các từ: *giỏ hàng, mua hàng, đặt hàng, giá tiền, link bio, sale, giảm giá*.
    - Caption sử dụng câu hỏi kích thích thảo luận kèm 5 hashtag thịnh hành: `#xuhuong #fyp #trending #meohay #learnontiktok`.
  + Khi mục tiêu là **[Có Affiliate Bán Hàng]**:
    - CTA tập trung: "Nhấp ngay vào giỏ hàng góc trái bên dưới video để rinh ngay em nó với giá ưu đãi hôm nay nhé!".
    - Kêu gọi hành động dứt khoát, tạo cảm giác khan hiếm / FOMO.

---

## 2. Phân Hệ Săn Video (Video Hunter & yt-dlp)

### Heuristic 2.1: Lọc thời lượng và định dạng an toàn
- **Vấn đề**: Video dài >90 giây khiến MoviePy render rất lâu, ngốn RAM và không phù hợp định dạng TikTok Short.
- **Quy tắc đúc kết**:
  + Chỉ tải video có duration $\le 90$ giây.
  + Thêm hậu tố tìm kiếm tiếng Việt hoặc từ khóa review ("review", "trải nghiệm", "unbox", "đập hộp") để tránh video nhạc chế hoặc vlog dài lê thê.
  + Luôn sử dụng binary FFmpeg đóng gói kèm (`imageio_ffmpeg`) để tránh crash trên máy tính Windows chưa cài FFmpeg toàn cục.

### Heuristic 2.2: Tránh trùng lặp 3 lớp (Triple Deduplication)
- **Vấn đề**: Tool tải lại video cũ hoặc làm lại sản phẩm đã đăng.
- **Quy tắc đúc kết**:
  + Lớp 1: Kiểm tra `uploaded_ids` từ `history.json`.
  + Lớp 2: Kiểm tra `channel_titles` đã đồng bộ từ kênh TikTok chính.
  + Lớp 3: Kiểm tra `affiliate_history` (danh sách tên sản phẩm và từ khóa trend đã từng sản xuất trong các chu kỳ trước).

---

## 3. Phân Hệ AI Brain (Gemini 2.5 & edge-tts)

### Heuristic 3.1: Kiểm soát số từ và độ dài Voiceover
- **Vấn đề**: Voiceover quá ngắn khiến video cụt lủn; voiceover quá dài (>35s) khiến người xem lướt qua trước khi nghe hết CTA.
- **Quy tắc đúc kết**:
  + Giới hạn số từ tiếng Việt: **75 - 90 từ**. Khi đọc với tốc độ `+10%` (`rate="+10%"`), thời lượng chuẩn là **24 - 28 giây**.
  + 3 giây đầu tiên (Hook): Bắt buộc dùng câu hỏi gây sốc, vạch trần hoặc đánh trúng nỗi đau (Pain Point).

### Heuristic 3.2: Lọc triệt để ký tự rác và chỉ dẫn đạo diễn (Sanitization)
- **Vấn đề**: LLM thường tự ý sinh thêm `[Cảnh 1]`, `(cười nhẹ)`, `[Nhạc nền sôi động]`, `**bold**` hoặc markdown tags vào lời bình. Nếu chuyển thẳng vào TTS, máy đọc sẽ phát âm cả "mở ngoặc vuông cảnh một đóng ngoặc vuông".
- **Quy tắc đúc kết**:
  + Chạy hàm `sanitize_voiceover` đệ quy để xóa sạch toàn bộ cặp ngoặc `[]`, `()`, `{}`, ký tự markdown `*`, `_`, `#`, `` ` `` và khoảng trắng thừa.
  + Cấu trúc prompt âm bản nghiêm ngặt (Strict Negative Constraints).

### Heuristic 3.3: Lựa chọn giọng đọc AI phù hợp phong cách
- **Nữ Gen Z, năng động**: `vi-VN-HoaiMyNeural` (mặc định, tự nhiên, nhịp điệu nhanh).
- **Nam phóng sự, kịch tính**: `vi-VN-NamMinhNeural` (trầm ấm, uy tín, hợp phong cách drama/vạch trần).

---

## 4. Phân Hệ Biên Tập Video (Video Editor & MoviePy)

### Heuristic 4.1: Chống vi phạm bản quyền thuật toán TikTok (Anti-fingerprinting)
- **Vấn đề**: Video reup nguyên bản bị TikTok phát hiện vi phạm bản quyền hoặc trùng lặp (Unoriginal Content).
- **Quy tắc đúc kết**:
  + Cắt ghép ít nhất 2 - 3 subclips từ các video nguồn khác nhau.
  + Tốc độ clip tăng nhẹ ngẫu nhiên ($1.05\times - 1.15\times$).
  + Lật ngang khung hình ngẫu nhiên (horizontal flip).
  + Chuẩn hóa chuẩn dọc 9:16 (1080x1920) với nền mờ (blurred background padding) hoặc zoom crop để không bị viền đen lỗi thời.
  + Thay thế toàn bộ audio gốc bằng voiceover mới và nhạc nền nhẹ âm lượng 15-20%.

### Heuristic 4.2: Quản lý bộ nhớ và khóa file trên Windows
- **Vấn đề**: Windows khóa file video/audio khi ffmpeg hoặc MoviePy chưa đóng handle, gây lỗi `PermissionError` khi dọn dẹp thư mục tạm.
- **Quy tắc đúc kết**:
  + Luôn gọi `.close()` tường minh trên tất cả `VideoFileClip`, `AudioFileClip`, `CompositeVideoClip`.
  + Chạy `gc.collect()` và nghỉ `0.1s` trước khi xóa file nguồn trong `input_videos/`.

---

## 5. Phân Hệ Đăng Tải (TikTok Studio Uploader & Playwright)

### Heuristic 5.1: Chế độ an toàn Draft vs Auto-Post
- **Quy tắc đúc kết**:
  + Khi tài khoản mới hoặc đang thử nghiệm: Khuyên dùng chế độ `--draft` để video lưu vào Bản nháp, người dùng kiểm tra lại nhạc và thumbnail trước khi công khai.
  + Khi hệ thống đã ổn định: Dùng `--auto-post` kết hợp khoảng nghỉ `--interval 120` để không bị TikTok nghi ngờ hành vi bot.

### Heuristic 5.2: Tái sử dụng Profile trình duyệt
- **Quy tắc đúc kết**:
  + Lưu cookies và session trong `chrome_profile/` để duy trì trạng thái đăng nhập TikTok Studio dài hạn mà không cần đăng nhập lại mỗi lần chạy.

---

## 6. Trải Nghiệm Điều Khiển CLI & Menu Tương Tác ([7] Toggle)

### Heuristic 6.1: Khử trùng lặp xác nhận (Deduplicate Confirmations)
- **Vấn đề**: Khi người dùng đã chủ động bấm [7] để đảo mục tiêu sang [Xây Kênh Kéo Follow] hoặc [Affiliate], hệ thống lại tiếp tục hỏi lại `Xác nhận loại kênh [1: Affiliate, 2: Xây kênh]` ở mỗi tùy chọn tiếp theo. Điều này gây ức chế và làm chậm thao tác tự động.
- **Quy tắc đúc kết**:
  + Chỉ hỏi xác nhận loại kênh nếu người dùng chưa từng qua bước toggle mục tiêu hoặc cắm cờ CLI. Khi người dùng đã toggle ở menu chính, ghi nhớ lựa chọn đó làm mặc định tuyệt đối mà không hỏi lặp lại.

### Heuristic 6.2: Đồng bộ Hạt Giống Fallback (Curated Viral Seeds)
- **Vấn đề**: Hiện danh sách seed dự phòng `CURATED_TRENDING_PRODUCTS` chỉ toàn đồ gia dụng/công nghệ bán hàng. Khi chạy chế độ Kéo Follow mà AI gặp sự cố mạng hoặc 503, tool rơi vào fallback đồ affiliate, làm mất chất độc lạ/viral kéo follow.
- **Quy tắc đúc kết**:
  + Cần tách riêng `CURATED_VIRAL_FOLLOW_TOPICS` gồm các chủ đề mẹo công nghệ, thí nghiệm độc lạ, đồ chơi sáng tạo kích thích bình luận tranh luận.
  + Thêm cơ chế retry cho `discover_trending_products` khi gặp lỗi 503 hoặc kết nối tạm thời.

---

## 7. Nhật Ký Chu Kỳ Học & Nâng Cấp (Cycle Changelog)
- **Chu kỳ 0 (Khởi tạo hệ thống)**: Thiết lập cấu trúc tự học từ thực tế, ghi nhận trace baseline, benchmarks và quy chuẩn chuyển đổi mục tiêu [Affiliate] <---> [Xây Kênh].
- **Chu kỳ 1 (Thực nghiệm Xây Kênh Kéo Follow - Mode [7])**:
  + Chạy thực tế thành công video 1080x1920 (22.49s, 90 từ) không dính từ khóa cấm.
  + Phát hiện 3 điểm nghẽn: Câu hỏi loại kênh bị lặp thừa ở CLI menu; thiếu hạt giống chủ đề riêng cho chế độ Follow; nhãn thông báo kết thúc chưa đồng bộ theo loại kênh.

