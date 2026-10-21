# Quy Tắc Vượt Kiểm Duyệt & Lách Thuật Toán TikTok (Anti-Detection Rules)

> **Hệ thống**: TikTok Affiliate Producer & AI Content Director  
> **Mục tiêu**: Độc bản hóa 100% nội dung video Affiliate từ hình ảnh sản phẩm gốc, vượt qua thuật toán quét nội dung trùng lặp (Unoriginal Content / Re-up), bóp tương tác hoặc từ chối duyệt gắn link TikTok Shop.

---

## 1. Cơ Chế Quét Của Thuật Toán TikTok (Detection Mechanics)

TikTok sử dụng hệ thống kiểm duyệt đa tầng tự động (Multimodal AI Shield) gồm:
1. **Perceptual Hash & Keyframe Matching (pHash/VMAF)**: Quét vân tay hình ảnh của từng chu kỳ 0.5s - 1s để so khớp với kho video toàn cầu.
2. **Audio Waveform Fingerprint**: Quét phổ âm thanh, nhạc nền bản quyền và các đoạn voiceover re-up.
3. **AI Generated Content (AIGC) Watermark & C2PA Detection**: Quét metadata ngầm hoặc watermark mờ của các công cụ sinh ảnh AI.
4. **NLP Policy Scanner**: Quét từ khóa vi phạm chính sách thương mại (từ cấm y tế, cam kết giật gân, lừa đảo, chuyển hướng link ngoài TikTok Shop).

---

## 2. Quy Tắc Độc Bản Hóa Hình Ảnh & Video (Visual Uniqueness)

### 2.1. Tuyệt Đối Không Cắt Ghép Re-up Thô Sơ
- **Nguyên tắc**: Không tải video có sẵn trên Douyin/TikTok để cắt gọt đơn giản.
- **Quy trình**: Bắt đầu từ **hình ảnh sản phẩm thực tế** được người dùng cung cấp -> sử dụng Gemini Vision để phân tích đặc tính -> sinh kịch bản storyboard phân cảnh độc quyền -> ứng dụng Google GenAI / hiệu ứng Ken Burns động chuyển động 3D để tạo các khung cảnh B-Roll hoàn toàn mới.

### 2.2. Biến Đổi Khung Hình & Motion Pacing (FFmpeg Anti-Detection Stack)
Mỗi video kết xuất bắt buộc phải áp dụng chuỗi biến đổi tín hiệu:
- **Tỷ lệ khung hình & Canvas**: Chuẩn dọc TikTok `1080x1920` (9:16), 30fps ổn định, pixel format `yuv420p`.
- **Dynamic Ken Burns Effect**: Mỗi phân cảnh tĩnh/ảnh đều có chuyển động camera (Zoom-in từ 1.0 -> 1.15 hoặc Pan mượt mà) với tốc độ chuyển cảnh từ 2.5s - 3.5s/scene để giữ nhịp retention cao.
- **Micro Color Grading (RGB Curve / Saturation)**:
  - Tăng nhẹ độ tương phản: `contrast=1.05`, `saturation=1.08`.
  - Giúp hình ảnh sản phẩm bắt mắt, sắc nét trên màn hình điện thoại AMOLED.
- **Film Grain & Noise Injection**:
  - Thêm một lớp noise vi mô ngẫu nhiên (`noise=c1s=6:c0f=u:allf=t`) mắt thường không nhận ra nhưng phá vỡ hoàn toàn mã băm pHash tĩnh của AI kiểm duyệt.
- **Randomized Micro-Crop / Padding**: Cắt cúp hoặc đệm ngẫu nhiên 1-2% viền để làm lệch tọa độ pixel gốc.

---

## 3. Quy Tắc Độc Bản Hóa Âm Thanh (Audio Anti-Fingerprint)

- **Voiceover**: 100% tạo mới bằng AI TTS tiếng Việt giọng tự nhiên (`vi-VN-HoaiMyNeural` hoặc `vi-VN-NamMinhNeural`), tốc độ `+8%` đến `+12%` để giữ nhịp điệu nhanh, dứt khoát.
- **BGM (Nhạc nền)**: Sử dụng các giai điệu trending không dính Content ID hoặc nhạc acoustic/lofi kích thích mua sắm.
- **Mixing & Ducking**: Giọng đọc voiceover chiếm 80-85% âm lượng; BGM giảm xuống 15-20% âm lượng nền (Auto-ducking khi có tiếng người nói).
- **Pitch Shift**: Thay đổi nhẹ cao độ voiceover `+0.3%` để phá vỡ signature mẫu giọng AI mặc định.

---

## 4. Xóa Sạch Metadata & Watermark (Metadata Sanitization)

- Lệnh render FFmpeg bắt buộc phải chứa cờ `-map_metadata -1` để triệt tiêu mọi thông tin EXIF, camera, công cụ sinh ảnh AI hoặc dấu vết phần mềm biên tập.
- Thiết lập encoder header chuẩn MP4 tương thích native thiết bị di động:
  ```bash
  ffmpeg -i ... -map_metadata -1 -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k ...
  ```

---

## 5. Quy Chuẩn Kịch Bản & Caption An Toàn (TikTok Shop Compliance)

### 5.1. Từ Cấm Cần Tránh Tuyệt Đối (Blacklisted Terms)
- Cấm cam kết tuyệt đối: *"100% hết bệnh", "chữa khỏi vĩnh viễn", "trắng da cấp tốc sau 1 ngày", "hoàn tiền gấp 10 nếu không hiệu quả"*.
- Cấm giật gân rẻ tiền, gây sợ hãi hoặc hình ảnh nhạy cảm hở hang.
- Cấm nhắc đến các nền tảng đối thủ hoặc lôi kéo ra ngoài: *"inbox Zalo", "link ở bio Facebook", "Shopee", "Lazada"*.

### 5.2. Công Thức Hook & CTA Chuẩn Chuyển Đổi
- **3 Giây đầu (Hook)**: Đánh trúng nỗi đau (Pain Point) hoặc sự tò mò thị giác: *"Đừng mua ... nếu bạn chưa biết điều này!", "Chiếc máy cứu rỗi căn bếp bừa bộn của hội lười!"*.
- **Giữa video (Solution)**: Trình diễn 2-3 tính năng nổi bật gắn liền với công dụng thực tế của sản phẩm từ ảnh.
- **Cuối video (CTA TikTok Shop)**: *"Bấm ngay vào giỏ hàng góc trái bên dưới video để săn ưu đãi hời hôm nay nhé!"*.
- **Caption**: Đặt câu hỏi thảo luận + tên sản phẩm + đúng 5 hashtag thịnh hành:
  `(Ví dụ: Hội yêu bếp núc đâu rồi? Rinh ngay em nó nha #xuhuong #fyp #trending #reviewgiadung #tiktokshop)`.
