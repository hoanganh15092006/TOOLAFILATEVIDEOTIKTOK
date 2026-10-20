# TikTok Affiliate Video Automation Tool 🚀

Công cụ tự động hóa toàn diện quy trình làm video TikTok Affiliate từ tìm sản phẩm hot trend, tải video re-up lách bản quyền, viết kịch bản bằng AI (Gemini), lồng tiếng Việt AI tự nhiên, dựng video và tự động tải lên / đăng trực tiếp lên TikTok Studio.

---

## 🌟 Tính Năng Nổi Bật

1. **Tự động săn sản phẩm Hot Trend & Affiliate:**
   - Tự động gợi ý và tìm kiếm các sản phẩm bán chạy theo từng ngành hàng: Gia dụng (`home`), Công nghệ (`tech`), Làm đẹp (`beauty`), Trang trí (`decor`), Thời trang (`fashion`).
   - Tự động lưu lịch sử để không bao giờ làm trùng sản phẩm đã đăng.

2. **Video Hunter & Lách Bản Quyền:**
   - Tự động tìm kiếm và tải video review/demo ngắn chất lượng cao từ YouTube Shorts.
   - Cơ chế bypass chống bot và phân tích định dạng chuẩn.

3. **AI Brain (Google Gemini & Edge TTS):**
   - Phân tích nội dung video gốc để trích xuất tên sản phẩm và công dụng.
   - Tự động viết kịch bản theo nhiều phong cách: Bắt trend Gen Z (`trend`), Hé lộ tò mò (`drama`), Kích cầu chốt đơn FOMO (`fomo`), hoặc Đánh giá trải nghiệm (`review`).
   - Lồng tiếng tiếng Việt tự nhiên (Giọng nữ Hoài My hoặc giọng nam Nam Minh).

4. **Remix & Edit Video Tự Động (MoviePy):**
   - Cắt ghép ngẫu nhiên các subclip để phá vỡ fingerprint video gốc.
   - Thêm hiệu ứng màu, zoom, lật khung hình nhẹ để lách thuật toán kiểm duyệt của TikTok.
   - Tự động đồng bộ thời lượng khớp 100% với giọng đọc thuyết minh.
   - Xuất video chuẩn dọc 9:16 (1080x1920) tốc độ cao.

5. **Tự Động Upload & Tự Đăng TikTok Studio (Playwright):**
   - Lưu trữ phiên đăng nhập Chrome profile, không cần đăng nhập lại mỗi lần.
   - Tự động đính kèm video, điền tiêu đề và hashtag affiliate tối ưu SEO.
   - Hỗ trợ tùy chọn **Tự Động Bấm Đăng Ngay** (`--auto-post`) hoặc **Lưu Bản Nháp** (`--draft`).

---

## 🛠️ Cài Đặt & Thiết Lập

### 1. Yêu cầu hệ thống
- Python 3.10 trở lên
- Git
- Trình duyệt Google Chrome hoặc Chromium

### 2. Cài đặt thư viện
```bash
git clone https://github.com/hoanganh15092006/TOOLAFILATEVIDEOTIKTOK.git
cd TOOLAFILATEVIDEOTIKTOK
pip install -r requirements.txt
playwright install chromium
```

### 3. Cấu hình API Key
Sao chép file `.env.example` thành `.env` và điền Google Gemini API Key của bạn:
```bash
cp .env.example .env
```
Mở file `.env` và cấu hình:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🚀 Hướng Dẫn Sử Dụng

### Cách 1: Sử dụng Menu tương tác (Khuyên dùng)
Chạy lệnh đơn giản:
```bash
python main.py
```
Giao diện dòng lệnh sẽ cho phép bạn lựa chọn:
- `[1]` Tự Động Hoàn Toàn & ĐĂNG NGAY
- `[2]` Tự Động & Lưu Vào BẢN NHÁP
- `[3]` Chọn Ngành Hàng Hot Trend (Gia dụng / Công nghệ / Mỹ phẩm...)
- `[4]` Chọn Phong Cách Kịch Bản (Trend / Drama / FOMO / Review)
- `[5]` Vòng Lặp Tự Động Liên Tục
- `[6]` Chế Độ Thủ Công (Tùy biến từ khóa)

---

### Cách 2: Chạy trực tiếp qua dòng lệnh (CLI Commands)

* **Tự động quét sản phẩm trend, làm video phong cách FOMO chốt đơn và TỰ ĐĂNG:**
  ```bash
  python main.py --auto --style fomo --auto-post
  ```

* **Săn trend ngành công nghệ, kịch bản Drama hé lộ và Lưu vào bản nháp:**
  ```bash
  python main.py --auto --niche tech --style drama --draft
  ```

* **Chạy chuỗi tự động 5 video ngành đồ gia dụng, mỗi video cách nhau 15 phút, tự đăng:**
  ```bash
  python main.py --auto --niche home --style trend --auto-post --loop --count 5 --interval 900
  ```

* **Chạy với từ khóa tùy chọn và chỉ tạo video (bỏ qua upload TikTok):**
  ```bash
  python main.py -k "tai nghe bluetooth chống ồn" --skip-upload
  ```

---

## 🛡️ Lưu Ý Bảo Mật
- Không bao giờ commit file `.env` hoặc thư mục `chrome_profile` lên GitHub vì có thể làm lộ API Key hoặc phiên đăng nhập tài khoản TikTok của bạn.
- Tất cả các file nhạy cảm và video tải về đã được cấu hình trong `.gitignore`.
