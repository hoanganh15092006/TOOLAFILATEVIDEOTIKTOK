# TikTok Video Automation Tool: Xây Kênh & Auto Affiliate 🚀

Công cụ tự động hóa toàn diện quy trình làm video TikTok từ tìm sản phẩm hot trend, tải video ngắn lách bản quyền, viết kịch bản bằng AI (Gemini), lồng tiếng Việt AI tự nhiên (Edge-TTS), dựng remix video 9:16 và tự động tải lên / đăng trực tiếp lên TikTok Studio.

---

## 🎯 2 Chế Độ Kênh Riêng Biệt

### 1. Kênh Xây Dựng Kéo Follower (Kênh mới dưới 1K Follower) 📈
- **Mục tiêu:** Kéo view, tăng follower, bùng nổ tương tác (tim, share, comment).
- **Chiến lược nội dung:** Chia sẻ mẹo hay, giải trí, khám phá tính năng độc lạ, kiến thức đời sống.
- **Call-to-Action (CTA):** Kêu gọi *Follow kênh*, *Thả tim*, *Lưu video*, *Để lại bình luận*.
- **Quy tắc quan trọng:** **TUYỆT ĐỐI KHÔNG** nhắc mua hàng, giỏ hàng, giá cả để tránh bị thuật toán TikTok bóp tương tác khi tài khoản chưa đủ điều kiện mở TikTok Shop.
- **Hashtags:** `#xuhuong #fyp #trending #meohay #learnontiktok #viralvideo`.

### 2. Kênh Affiliate Bán Hàng (Kênh đã trên 1K Follower có TikTok Shop) 🛒
- **Mục tiêu:** Tối đa tỷ lệ chuyển đổi, kích thích đặt hàng, kiếm hoa hồng tiếp thị liên kết.
- **Chiến lược nội dung:** Đánh giá sản phẩm giải quyết nỗi đau, nêu bật lợi ích thực tế, ưu đãi giá sốc.
- **Call-to-Action (CTA):** Kêu gọi người xem *Bấm ngay vào giỏ hàng góc trái bên dưới màn hình* để săn deal hời trước khi hết mã giảm giá.
- **Hashtags:** `#tiktokshop #affiliate #dealhot #review #muataitiktok`.

---

## 🌟 Menu Điều Khiển Trực Quan

Chỉ cần chạy lệnh:
```bash
python main.py
```
Giao diện dòng lệnh sẽ cho phép bạn lựa chọn:
```text
========================================================================
   TIKTOK AUTOMATION - TRUNG TÂM SẢN XUẤT VIDEO TỰ ĐỘNG
========================================================================
  MỤC TIÊU KÊNH HIỆN TẠI: >>> [CÓ AFFILIATE BÁN HÀNG - KÊNH >1K FL] <<<
------------------------------------------------------------------------
  [1] Tự Động Hoàn Toàn & ĐĂNG NGAY (Tìm trend, làm video & tự đăng)
  [2] Tự Động & Lưu Vào BẢN NHÁP (Tạo video & lưu Draft TikTok Studio)
  [3] Chọn Ngành Hàng Hot Trend (Gia dụng / Công nghệ / Mỹ phẩm...)
  [4] Chọn Phong Cách Kịch Bản (Trend / Drama / FOMO / Review)
  [5] Vòng Lặp Tự Động Liên Tục (Chạy chuỗi nhiều video tự động)
  [6] Chế Độ Thủ Công (Tùy biến từ khóa theo ý muốn)
  [7] Đổi Mục Tiêu: [Có Affiliate >1K FL] <---> [Xây Kênh Kéo Follow]
  [0] Thoát
========================================================================
```

---

## 🛠️ Cài Đặt & Thiết Lập

### 1. Yêu cầu hệ thống
- Python 3.10 trở lên
- Git
- Google Chrome hoặc Chromium

### 2. Cài đặt thư viện
```bash
git clone https://github.com/hoanganh15092006/TOOLAFILATEVIDEOTIKTOK.git
cd TOOLAFILATEVIDEOTIKTOK
pip install -r requirements.txt
playwright install chromium
```

### 3. Cấu hình Gemini API Key
Sao chép `.env.example` thành `.env` và điền Google Gemini API Key:
```bash
cp .env.example .env
```
Nội dung file `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🚀 Các Tùy Chọn Dòng Lệnh (CLI Flags)

### Cho Kênh Xây Dựng (Dưới 1K Followers)
* **Tự động săn mẹo/đồ thông minh viral, làm video kịch bản Gen Z và ĐĂNG NGAY:**
  ```bash
  python main.py --auto --build-channel --style trend --auto-post
  ```

* **Săn đồ công nghệ độc lạ, kịch bản Drama hé lộ và Lưu bản nháp:**
  ```bash
  python main.py --auto --build-channel --niche tech --style drama --draft
  ```

### Cho Kênh Affiliate (Trên 1K Followers)
* **Tự động săn sản phẩm hot trend TikTok Shop, kịch bản FOMO chốt deal và TỰ ĐĂNG:**
  ```bash
  python main.py --auto --affiliate --style fomo --auto-post
  ```

* **Chạy chuỗi 5 video gia dụng thông minh, mỗi video cách nhau 15 phút, tự đăng:**
  ```bash
  python main.py --auto --affiliate --niche home --auto-post --loop --count 5 --interval 900
  ```

### Chạy Thủ Công Với Từ Khóa Riêng
* **Chỉ tạo video theo từ khóa (bỏ qua upload TikTok):**
  ```bash
  python main.py -k "bình giữ nhiệt hiển thị nhiệt độ" --build-channel --skip-upload
  ```

---

## 🛡️ Lưu Ý Bảo Mật
- Không bao giờ commit file `.env` hoặc thư mục `chrome_profile` lên GitHub.
- Các file nhạy cảm và file media tạm đã được cấu hình loại trừ tự động trong `.gitignore`.
