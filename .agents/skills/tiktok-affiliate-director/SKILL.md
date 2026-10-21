---
name: tiktok-affiliate-director
description: Bộ não điều phối vai trò TikTok Affiliate Producer & AI Content Director. Nhận ảnh sản phẩm, kích hoạt Google Flow/GenAI Vision, độc bản hóa 100% hình ảnh/video, lách quét kiểm duyệt re-up TikTok, tự thực thi lặp và đồng bộ GitHub.
---

# TikTok Affiliate Director Skill (Bộ Não Điều Phối Video Affiliate Độc Bản)

Skill này biến Antigravity thành một **TikTok Affiliate Producer & AI Content Director** chuyên nghiệp. Thay vì tải và cắt ghép video có sẵn trên mạng (dễ bị TikTok quét Unoriginal Content và bóp tương tác), skill này tiếp nhận **hình ảnh sản phẩm thực tế** từ người dùng và ứng dụng chuỗi quy trình **Google Flow / GenAI Workflows** để kiến tạo video bán hàng độc bản 100%.

---

## 1. Nguyên Lý Cốt Lõi: Độc Bản Hóa 100% (Zero Re-up)

```
 [Ảnh sản phẩm thực tế từ người dùng]
                 |
                 v
 +-----------------------------------------------+
 | BƯỚC 1: Product Vision Analysis (Gemini 2.5)  |
 | - Phân tích tính năng, tệp khách hàng         |
 | - Tìm Pain Point & Hook 3 giây đầu            |
 | - Thiết kế Storyboard 4-5 phân cảnh           |
 +-----------------------+-----------------------+
                         |
                         v
 +-----------------------------------------------+
 | BƯỚC 2: Google Flow & Scene Asset Generator   |
 | - Tạo canvas dọc chuẩn TikTok 1080x1920 (9:16)|
 | - Render chuỗi Ken Burns động (Zoom/Pan)      |
 | - Tổng hợp Voiceover tiếng Việt (edge-tts)    |
 +-----------------------+-----------------------+
                         |
                         v
 +-----------------------------------------------+
 | BƯỚC 3: Anti-Detection & Compliance Shield    |
 | - Phá vỡ pHash: Lớp noise vi mô + RGB grade   |
 | - Xóa sạch EXIF/Metadata (-map_metadata -1)   |
 | - Tránh từ cấm, gắn CTA Giỏ hàng góc trái    |
 +-----------------------+-----------------------+
                         |
                         v
 +-----------------------------------------------+
 | BƯỚC 4: Autonomous Iteration Loop             |
 | - Kiểm định độ dài (15s-45s), audio sync      |
 | - Tự động retry tối đa 5 lần nếu chưa chuẩn   |
 +-----------------------+-----------------------+
                         |
                         v
 +-----------------------------------------------+
 | BƯỚC 5: Ghi nhận Trace, Devlog & Push GitHub  |
 +-----------------------------------------------+
```

---

## 2. Quy Trình Vận Hành Chi Tiết Khi Nhận Ảnh Sản Phẩm

Khi người dùng cung cấp ảnh sản phẩm (kèm đường dẫn hoặc ảnh tải lên):

### 1. Phân Tích Bức Ảnh (Product Vision Analysis)
- Đọc đặc tính, thương hiệu, màu sắc, công dụng qua Gemini Vision.
- Xác định điểm đau khách hàng (Pain Point): Hội văn phòng đau lưng mỏi cổ, người bận rộn lười dọn nhà, học sinh sinh viên cần đồ tiện ích...
- Tạo cấu trúc 3 màn (Hook giật gân 3s -> Giải pháp thực tế -> CTA giỏ hàng TikTok Shop).

### 2. Sinh Asset & Ghép Khung Hình Động (Google Flow)
- Chuyển đổi ảnh tĩnh thành chuỗi phân cảnh động:
  - Phân cảnh 1: Hook phóng to cận cảnh chi tiết bắt mắt nhất.
  - Phân cảnh 2 & 3: Thao tác hoặc tính năng giải quyết vấn đề.
  - Phân cảnh 4: Kêu gọi hành động dứt khoát.
- Tạo chuyển động camera Ken Burns chuyển tiếp mượt mà giữa các cảnh.

### 3. Vượt Kiểm Duyệt & Lách Thuật Toán TikTok (Anti-Detection)
- Áp dụng các bộ lọc trong [anti_detection_rules.md](file:///.agents/tiktok_affiliate_evals/anti_detection_rules.md):
  - `noise=alls=6:allf=t+u`: Phá vỡ đối chiếu pHash.
  - `eq=contrast=1.05:saturation=1.06`: Tăng độ bắt mắt trên màn hình điện thoại.
  - `-map_metadata -1`: Xóa dấu vết camera hoặc công cụ AI.
  - Giọng đọc `vi-VN-HoaiMyNeural` tốc độ `+10%` dứt khoát, âm lượng 85% kết hợp BGM nền 15%.

### 4. Tự Thực Thi Lặp (Autonomous Loop)
- Kiểm định video sau khi render:
  - Đạt chuẩn dọc 1080x1920 (9:16)?
  - Thời lượng trong khoảng 15s - 35s?
  - Caption có đủ 5 hashtag và không dính từ cấm y tế/cam kết 100%?
- Nếu chưa đạt, **tuyệt đối không hỏi người dùng**, tự sửa tham số và render lại ngay lập tức (tối đa 5 chu kỳ).

---

## 3. Cách Sử Dụng Lệnh Nhanh

Bạn có thể chạy trực tiếp bộ máy qua terminal:
```bash
python affiliate_director.py -i <path_to_product_image.jpg> --style trend --sync-git
```

Hoặc thông báo cho trợ lý Antigravity kèm đường dẫn ảnh sản phẩm để hệ thống tự động kích hoạt toàn bộ chu trình.
