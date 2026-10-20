# TikTok Video Automation Tool: Xây Kênh & Auto Affiliate 🚀

Công cụ tự động hóa toàn diện quy trình làm video TikTok: Tự động săn sản phẩm hot trend, tải video ngắn lách bản quyền, viết kịch bản bằng AI (Gemini), lồng tiếng Việt AI tự nhiên (Edge-TTS), dựng remix video 9:16 và tự động tải lên / đăng trực tiếp lên TikTok Studio kèm **tự động gắn link sản phẩm TikTok Shop Affiliate**.

---

## ⚡ Hướng Dẫn Chạy 1-Click Tự Động 100% (Khuyên Dùng)

> [!TIP]
> **Người dùng mới chưa cài đặt Chromium hay môi trường Python?**
> Không cần lo lắng! Tool đã tích hợp sẵn script tự động hóa hoàn toàn từ A-Z.

### 🌟 Cách Chạy Nhanh Nhất (Dành cho Windows):

1. **Tải mã nguồn về máy** (hoặc dùng `git clone https://github.com/hoanganh15092006/TOOLAFILATEVIDEOTIKTOK.git`).
2. **Nhấp đúp chuột vào file `run.bat`** (hoặc mở Terminal gõ `run.bat` / PowerShell `.\run.ps1`).
3. **Script sẽ tự động:**
   - 🔍 Kiểm tra Python trên hệ thống.
   - 📦 Tự động tạo môi trường ảo độc lập (`.venv`).
   - 📥 Tự động cài đặt đầy đủ tất cả thư viện trong `requirements.txt`.
   - 🌐 **Tự động tải & cài đặt Chromium Browser (`playwright install chromium`)** cho bạn mà không cần cài thủ công.
   - ⚙️ Tự động tạo file cấu hình `.env` từ `.env.example`.
   - 🚀 Tự động mở giao diện điều khiển Menu tương tác trực quan.

*(Nếu là lần đầu chạy, bạn chỉ cần mở file `.env` vừa được tạo và dán mã `GEMINI_API_KEY=...` miễn phí từ Google AI Studio).*

---

## 🛒 Tính Năng Tự Động Tìm & Gắn Sản Phẩm Affiliate Chuẩn Xác

Khi bạn kích hoạt chế độ **Affiliate Bán Hàng (>1K Followers)**:

1. AI Gemini tự động phân tích video gốc và trích xuất tên sản phẩm chính xác (ví dụ: *Nồi chiên không dầu Lock&Lock*, *Bình giữ nhiệt hiển thị nhiệt độ*...).
2. Khi tải video lên TikTok Studio, tool tự động mở khu vực **Thêm liên kết sản phẩm (Add product / Showcase)**.
3. Tự động nhập tên sản phẩm, tìm kiếm sản phẩm chính xác trong Tủ trưng bày (Showcase / TikTok Shop Affiliate) và chọn gắn vào video.
4. Video xuất bản sẽ có ngay **Giỏ hàng góc trái** dẫn thẳng đến sản phẩm đó để người xem bấm mua nhận hoa hồng!
5. *(Nếu tài khoản chưa đủ điều kiện TikTok Shop Creator, tool sẽ phát hiện và thông báo nhẹ nhàng, tiếp tục đăng video an toàn mà không làm gián đoạn tiến trình).*

---

## 🎯 2 Chế Độ Kênh Riêng Biệt

### 1. Kênh Xây Dựng Kéo Follower (Kênh mới dưới 1K Follower) 📈

- **Mục tiêu:** Kéo view triệu view, tăng follower nhanh chóng, bùng nổ tương tác (tim, share, comment).
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

Chỉ cần chạy `run.bat` hoặc lệnh:

```bash
python main.py
```

Giao diện dòng lệnh tiếng Việt trực quan:

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

## 🚀 Các Tùy Chọn Dòng Lệnh Nâng Cao (CLI Flags)

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

* **Tự động săn sản phẩm hot trend TikTok Shop, tự tìm & gắn sản phẩm affiliate và TỰ ĐĂNG:**

  ```bash
  python main.py --auto --affiliate --style fomo --auto-post
  ```
* **Chạy chuỗi 5 video gia dụng thông minh, mỗi video cách nhau 15 phút, tự gắn link affiliate & tự đăng:**

  ```bash
  python main.py --auto --affiliate --niche home --auto-post --loop --count 5 --interval 900
  ```

### Chạy Thủ Công Với Từ Khóa Riêng

* **Tạo video theo từ khóa (bỏ qua upload TikTok):**
  ```bash
  python main.py -k "bình giữ nhiệt hiển thị nhiệt độ" --build-channel --skip-upload
  ```

---

## 🛡️ Lưu Ý Bảo Mật & Đăng Nhập

- **Đăng nhập TikTok Studio lần đầu:** Khi chạy lần đầu, cửa sổ trình duyệt Chromium sẽ mở ra trang TikTok Studio. Bạn chỉ cần đăng nhập tài khoản TikTok của mình 1 lần duy nhất. Trình duyệt sẽ lưu phiên đăng nhập vĩnh viễn vào thư mục `chrome_profile/` cho các lần chạy tự động tiếp theo.
- **Bảo mật:** Không bao giờ chia sẻ hay commit file `.env` hoặc thư mục `chrome_profile` lên GitHub.
