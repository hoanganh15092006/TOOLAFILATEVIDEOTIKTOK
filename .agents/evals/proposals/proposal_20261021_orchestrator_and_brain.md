# Đề Xuất Nâng Cấp Mã Nguồn - Chu Kỳ 1 (Self-Upgrade Proposal: Cycle 1)

> **Mã đề xuất**: `proposal_20261021_orchestrator_and_brain.md`  
> **Nguồn gốc học tập**: Trích xuất từ thực nghiệm thực tế `trace_001_follow_mode_real` trong `execution_traces.jsonl` và các nguyên tắc trong `learned_heuristics.md`.  
> **Trạng thái**: Chờ người dùng duyệt xác nhận (Pending User Approval).

---

## 1. Kết Quả Thẩm Định & Phản Tư (Evaluator Reflection)

Từ việc quan sát thực tế lần chạy tạo video với chế độ **[7] Đổi Mục Tiêu: [Có Affiliate >1K FL] <---> [Xây Kênh Kéo Follow]** và các tùy chọn mặc định, bộ máy Evaluator đã chỉ ra 3 điểm then chốt:

### 1.1. Điểm thừa (Redundancy & Friction)
- **Hỏi lặp lại loại kênh ở CLI (`main.py`)**: Khi người dùng đã chủ động bấm `[7]` để chuyển trạng thái sang `[XÂY KÊNH KÉO FOLLOW - KÊNH <1K FL]`, sau đó nhấn Enter để chọn mặc định `[1]`, hệ thống lại gọi hàm `ask_channel_type()` để hỏi lại: `Xác nhận loại kênh [1: Affiliate >1k fl, 2: Xây kênh kéo follow]`. Điều này gây phiền hà và làm chậm tính năng "1-click auto-pilot".
- **Nhãn kết thúc hard-code (`main.py`)**: Thông báo kết thúc vẫn ghi `[SUCCESS] TikTok Affiliate Video Pipeline Completed Successfully!` dù video vừa tạo hoàn toàn là video Xây Kênh Kéo Follow (không chứa giỏ hàng hay affiliate).

### 1.2. Điểm thiếu (Missing Resilience & Viral Seeds)
- **Thiếu danh mục hạt giống Viral riêng cho Kéo Follow (`ai_brain.py`)**: Khi Gemini API gặp lỗi tải chậm hoặc 503 Service Unavailable, hàm `discover_trending_products` rơi vào fallback dùng `CURATED_TRENDING_PRODUCTS`. Danh sách này hiện 100% là sản phẩm bán hàng gia dụng, thiếu các chủ đề độc lạ/gadget siêu cuốn/mẹo cuộc sống chuyên phục vụ kéo follow.
- **Thiếu retry đa tầng cho `discover_trending_products` (`ai_brain.py`)**: Khi gặp lỗi 503 tạm thời từ Google API, hàm lập tức fallback thay vì retry nhẹ như `generate_script`.

---

## 2. Thiết Kế Bản Nâng Cấp Mã Nguồn (Proposed Code Changes)

### Cải tiến 1: Tối ưu hóa `main.py`
- Ghi nhớ cờ `user_has_set_target` khi người dùng đã bấm `[7]`.
- Bỏ câu hỏi trùng lặp nếu người dùng đã chủ động chọn mục tiêu ở menu chính.
- Cập nhật banner hoàn tất linh hoạt theo mục tiêu: `TikTok Channel Building Video Pipeline` vs `TikTok Affiliate Video Pipeline`.

### Cải tiến 2: Bổ sung hạt giống Viral & Retry trong `ai_brain.py`
- Khởi tạo `CURATED_VIRAL_FOLLOW_TOPICS` gồm các chủ đề độc lạ cực hút view (bút vẽ 3D, đèn bay từ tính, máy đo độ ồn, mẹo công nghệ ẩn, kính thực tế tăng cường...).
- Nếu `is_affiliate=False` và cần fallback, ưu tiên chọn từ `CURATED_VIRAL_FOLLOW_TOPICS`.
- Thêm vòng lặp retry 2 lần với khoảng nghỉ 2s cho Gemini call trong `discover_trending_products`.

---

## 3. Bản Diff Code Dự Kiến

### Diff 1: `main.py`
```diff
@@ -306,6 +306,7 @@ def run_pipeline(
+    target_already_chosen = False
     if not search_keyword and not auto_mode:
         while True:
@@ -333,6 +334,7 @@ def run_pipeline(
             elif user_choice == "7" or user_choice.lower() == "toggle":
                 is_affiliate = not is_affiliate
+                target_already_chosen = True
                 print(f">>> Đã chuyển mục tiêu sang: {'[Có Affiliate >1K FL]' if is_affiliate else '[Xây Kênh Kéo Follow]'}")
                 continue
@@ -339,6 +341,8 @@ def run_pipeline(
         def ask_channel_type(current_aff: bool) -> bool:
+            if target_already_chosen:
+                return current_aff
             try:
```

### Diff 2: `ai_brain.py`
```diff
+CURATED_VIRAL_FOLLOW_TOPICS: list[dict[str, str]] = [
+    {"name": "Đèn mặt trăng bay lơ lửng từ tính", "keyword": "đèn mặt trăng lơ lửng từ tính review", "category": "Đồ gia dụng độc lạ"},
+    {"name": "Bút in 3D tạo hình không gian", "keyword": "bút in 3d tạo hình review", "category": "Sáng tạo công nghệ"},
+    {"name": "Kính thiên văn mini ngắm mặt trăng", "keyword": "kính thiên văn mini ngắm sao review", "category": "Khoa học khám phá"},
+    {"name": "Quạt hologram 3D phát hình ảnh không gian", "keyword": "quạt hologram 3d review", "category": "Công nghệ tương lai"},
+    {"name": "Hộp khóa điện thoại cai nghiện smartphone", "keyword": "hộp khóa điện thoại hẹn giờ review", "category": "Đời sống tiện ích"},
+]
```
