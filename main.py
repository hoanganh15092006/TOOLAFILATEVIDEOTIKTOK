#!/usr/bin/env python3
"""
main.py - Central Pipeline Orchestrator CLI
============================================
Project: Automated TikTok Affiliate Video Creation & Upload Pipeline
Milestone: M6 (Requirement R6)

Responsibilities:
  1. CLI Argument Parsing:
     - Supports `--keyword` (`-k`), `--channel-url` (`-c`), `--max-videos` (`-m`),
       `--headless`, and `--skip-upload`.
  2. Preflight Checks:
     - Loads `.env` via `dotenv.load_dotenv()`.
     - Ensures required folders (`input_videos/`, `output_videos/`) exist.
     - Verifies `GEMINI_API_KEY` configuration.
  3. Interactive Fallback:
     - Prompts user in terminal if `--keyword` is omitted.
  4. Sequential Stage Execution:
     - Stage 0 (Optional): Channel sync via `video_hunter.sync_my_channel`.
     - Stage 1: Video hunt & download via `video_hunter.hunt_new_videos`.
     - Stage 2: Script generation via `ai_brain.generate_script` and
       Vietnamese voice synthesis via `ai_brain.generate_voice`.
     - Stage 3: Anti-fingerprinting video remixing via `video_editor.edit_and_render`.
     - Stage 4: TikTok Studio upload automation via `tiktok_uploader.upload_tiktok_video`.
  5. Presentation & Error Boundaries:
     - Terminal status banner and step-by-step progress logging.
     - Graceful recovery and clean exit on errors or empty search results.
"""

import os
import sys
import argparse
import logging
from typing import Optional, List

import dotenv

import video_hunter
import ai_brain
import video_editor
import tiktok_uploader

# Configure structured CLI logger
logger = logging.getLogger("pipeline")
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


BANNER = """
========================================================================
   TIKTOK AFFILIATE AUTOMATION PIPELINE (R6 CENTRAL ORCHESTRATOR)
========================================================================
   Hunter (yt-dlp) -> Brain (Gemini 2.5 + edge-tts) -> Editor (MoviePy) -> Uploader (Playwright)
========================================================================
"""


def print_banner() -> None:
    """Prints the pipeline execution banner."""
    print(BANNER)


def preflight_checks() -> bool:
    """
    Performs preflight checks:
      - Loads environment variables from `.env`.
      - Ensures `input_videos/` and `output_videos/` directories exist.
      - Verifies `GEMINI_API_KEY` presence.

    Returns:
        bool: True if directories and basic environment are ready.
    """
    dotenv.load_dotenv()

    # Ensure required working directories exist
    os.makedirs("input_videos", exist_ok=True)
    os.makedirs("output_videos", exist_ok=True)

    # Verify Gemini API key configuration
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not gemini_key or gemini_key == "your_key_here":
        logger.warning(
            "[PREFLIGHT] GEMINI_API_KEY is unset or placeholder in .env. "
            "Stage 2 (AI Script Generation) will fail unless a valid key is provided."
        )
    else:
        logger.info("[PREFLIGHT] GEMINI_API_KEY detected.")

    logger.info("[PREFLIGHT] Directories verified ('input_videos/', 'output_videos/').")
    return True


def run_single_pipeline(
    search_keyword: str,
    max_videos: int = 3,
    headless: bool = False,
    skip_upload: bool = False,
    auto_post: bool = False,
    save_draft: bool = False,
    product_name_hint: Optional[str] = None,
    style: str = "trend",
    voice: str = "vi-VN-HoaiMyNeural",
    is_affiliate: bool = True,
) -> bool:
    """
    Executes stages 1-4 for a single keyword:
      Video Hunter -> AI Brain -> Video Editor -> TikTok Uploader

    Returns:
        bool: True if pipeline completed successfully, False otherwise.
    """
    # -------------------------------------------------------------------------
    # Stage 1: Video Hunter
    # -------------------------------------------------------------------------
    logger.info(f"[STAGE 1/4] Hunting new videos for keyword: '{search_keyword}' (max: {max_videos})...")
    try:
        downloaded_videos = video_hunter.hunt_new_videos(
            search_keyword=search_keyword,
            max_videos=max(1, max_videos),
        )
    except Exception as exc:
        logger.error(f"[STAGE 1/4] Video hunting failed with error: {exc}")
        return False

    if not downloaded_videos:
        logger.warning(
            f"[STAGE 1/4] No new videos downloaded for '{search_keyword}'. "
            "All candidate videos may have been previously uploaded, exceed 90 seconds, "
            "or could not be downloaded. Exiting pipeline gracefully."
        )
        return False

    logger.info(
        f"[STAGE 1/4] Video Hunter completed successfully. "
        f"Downloaded {len(downloaded_videos)} video(s): {downloaded_videos}"
    )

    # -------------------------------------------------------------------------
    # Stage 2: AI Brain (Script Generation & Voice Synthesis)
    # -------------------------------------------------------------------------
    first_video = downloaded_videos[0]
    mode_label = "Affiliate Bán Hàng (>1K FL)" if is_affiliate else "Xây Kênh Kéo Follow (<1K FL)"
    logger.info(
        f"[STAGE 2/4] Analyzing first downloaded video with Gemini "
        f"(style='{style}', mode='{mode_label}'): {first_video}"
    )

    try:
        if (style and style != "trend") or not is_affiliate:
            script_data = ai_brain.generate_script(first_video, style=style, is_affiliate=is_affiliate)
        else:
            script_data = ai_brain.generate_script(first_video)
    except Exception as exc:
        logger.error(f"[STAGE 2/4] AI script generation failed: {exc}")
        return False

    product_name = script_data.get("product_name") or product_name_hint or "Sản phẩm"
    voiceover_text = script_data.get("voiceover", "")
    caption = script_data.get("caption", "")

    logger.info(f"[STAGE 2/4] Identified Topic/Product: {product_name}")
    logger.info(
        f"[STAGE 2/4] Generated Script ({len(voiceover_text.split())} words, style='{style}', mode='{mode_label}'):\n"
        f"------------\n{voiceover_text}\n------------"
    )
    logger.info(f"[STAGE 2/4] Generated Caption:\n{caption}")

    voiceover_file = "voiceover.mp3"
    logger.info(f"[STAGE 2/4] Synthesizing Vietnamese speech to '{voiceover_file}' (voice='{voice}')...")
    try:
        if voice and voice != "vi-VN-HoaiMyNeural":
            ai_brain.generate_voice(voiceover_text, output_audio=voiceover_file, voice=voice)
        else:
            ai_brain.generate_voice(voiceover_text, output_audio=voiceover_file)
        logger.info(f"[STAGE 2/4] Voiceover audio generated successfully: {voiceover_file}")
    except Exception as exc:
        logger.error(f"[STAGE 2/4] Voice synthesis failed: {exc}")
        return False

    # -------------------------------------------------------------------------
    # Stage 3: Video Editor (Anti-fingerprinting & Remixing)
    # -------------------------------------------------------------------------
    final_output_path = os.path.join("output_videos", "final_video.mp4")
    logger.info(
        f"[STAGE 3/4] Remixing source clips and applying anti-fingerprinting to create '{final_output_path}'..."
    )

    try:
        rendered_path = video_editor.edit_and_render(
            input_dir="input_videos",
            audio_path=voiceover_file,
            output_path=final_output_path,
        )
        logger.info(f"[STAGE 3/4] Video rendered and exported successfully to: {rendered_path}")
    except Exception as exc:
        logger.error(f"[STAGE 3/4] Video editing/rendering failed: {exc}")
        return False

    # -------------------------------------------------------------------------
    # Stage 4: TikTok Uploader
    # -------------------------------------------------------------------------
    if skip_upload:
        logger.info("[STAGE 4/4] Upload skipped (--skip-upload flag was enabled).")
    else:
        logger.info(f"[STAGE 4/4] Launching TikTok Studio uploader (headless={headless})...")
        try:
            upload_kwargs = {
                "video_path": rendered_path,
                "caption": caption,
                "headless": headless,
                "is_affiliate": is_affiliate,
                "product_name": product_name,
            }
            if auto_post:
                upload_kwargs["auto_post"] = True
            if save_draft:
                upload_kwargs["save_draft"] = True

            upload_success = tiktok_uploader.upload_tiktok_video(**upload_kwargs)
            if upload_success:
                logger.info("[STAGE 4/4] TikTok Studio upload completed successfully!")
            else:
                logger.warning("[STAGE 4/4] TikTok Studio upload did not complete or was not confirmed.")
        except Exception as exc:
            logger.error(f"[STAGE 4/4] TikTok Studio upload failed: {exc}")
            return False

    print("\n" + "=" * 70)
    print("  [SUCCESS] TikTok Affiliate Video Pipeline Completed Successfully!")
    print(f"  Final Video : {final_output_path}")
    print(f"  Product     : {product_name}")
    print("=" * 70 + "\n")
    return True


def run_pipeline(
    search_keyword: Optional[str] = None,
    channel_url: Optional[str] = None,
    max_videos: int = 3,
    headless: bool = False,
    skip_upload: bool = False,
    auto_mode: bool = False,
    auto_post: bool = False,
    save_draft: bool = False,
    loop: bool = False,
    loop_count: int = 1,
    loop_interval: int = 120,
    niche: Optional[str] = None,
    style: str = "trend",
    voice: str = "vi-VN-HoaiMyNeural",
    is_affiliate: bool = True,
) -> None:
    """
    Central orchestrator coordinating all pipeline stages:
      Preflight -> Channel Sync (opt) -> Video Hunter -> AI Brain -> Video Editor -> TikTok Uploader

    Supports rich customization:
      - Channel Objective: Affiliate (>1K FL, CTA cart) vs Channel Building (<1K FL, CTA follow)
      - Niche targeting (home, tech, beauty, decor, fashion)
      - Script style customization (trend, drama, fomo, review)
      - Voiceover selection (female: HoaiMy, male: NamMinh)
      - Auto-Posting vs Save as Draft
      - Multi-video continuous loop production

    Args:
        search_keyword: Product search keyword to hunt on TikTok. If None or empty, prompts user interactively.
        channel_url: Optional TikTok channel URL to extract and sync existing titles to history.json.
        max_videos: Maximum number of candidate review videos to download (default: 3).
        headless: Whether to run Playwright Chromium in headless mode (default: False).
        skip_upload: If True, skips Stage 4 TikTok upload (default: False).
        auto_mode: If True, AI automatically discovers trending affiliate products.
        auto_post: If True, automatically clicks Post button on TikTok Studio.
        save_draft: If True, automatically saves video to TikTok Drafts instead of posting.
        loop: If True, runs continuously in a multi-video auto-pilot loop.
        loop_count: Number of products to process in loop mode (default: 1).
        loop_interval: Delay in seconds between cycles in loop mode (default: 120s).
        niche: Filter products by niche ('home', 'tech', 'beauty', 'decor', 'fashion').
        style: Script style ('trend', 'drama', 'fomo', 'review').
        voice: edge-tts voice or alias ('female', 'male').
        is_affiliate: True for Affiliate Selling (>1K FL), False for Channel Building (<1K FL).
    """
    print_banner()

    # Execute Preflight Checks
    preflight_checks()

    # Optional Channel Sync
    if channel_url and channel_url.strip():
        url = channel_url.strip()
        logger.info(f"[STAGE 0] Syncing existing channel titles from: {url}")
        try:
            titles = video_hunter.sync_my_channel(url)
            logger.info(f"[STAGE 0] Channel sync completed. {len(titles)} title(s) in history.")
        except Exception as exc:
            logger.error(f"[STAGE 0] Channel sync failed: {exc}")

    # Interactive Prompt if neither keyword nor auto_mode is specified
    if search_keyword is not None:
        search_keyword = search_keyword.strip()

    if not search_keyword and not auto_mode:
        while True:
            target_str = "[CÓ AFFILIATE BÁN HÀNG - KÊNH >1K FL]" if is_affiliate else "[XÂY KÊNH KÉO FOLLOW - KÊNH <1K FL]"
            try:
                print("\n" + "=" * 72)
                print("   TIKTOK AUTOMATION - TRUNG TÂM SẢN XUẤT VIDEO TỰ ĐỘNG")
                print("=" * 72)
                print(f"  MỤC TIÊU KÊNH HIỆN TẠI: >>> {target_str} <<<")
                print("-" * 72)
                print("  [1] Tự Động Hoàn Toàn & ĐĂNG NGAY (Tìm trend, làm video & tự đăng)")
                print("  [2] Tự Động & Lưu Vào BẢN NHÁP (Tạo video & lưu Draft TikTok Studio)")
                print("  [3] Chọn Ngành Hàng Hot Trend (Gia dụng / Công nghệ / Mỹ phẩm...)")
                print("  [4] Chọn Phong Cách Kịch Bản (Trend / Drama / FOMO / Review)")
                print("  [5] Vòng Lặp Tự Động Liên Tục (Chạy chuỗi nhiều video tự động)")
                print("  [6] Chế Độ Thủ Công (Tùy biến từ khóa theo ý muốn)")
                print("  [7] Đổi Mục Tiêu: [Có Affiliate >1K FL] <---> [Xây Kênh Kéo Follow]")
                print("  [0] Thoát")
                print("-" * 72)
                user_choice = input("Lựa chọn của bạn [Mặc định: 1 - Tự động đăng]: ").strip()
                print("-" * 72 + "\n")
            except (EOFError, KeyboardInterrupt):
                print("\n[!] Input aborted by user. Exiting pipeline.")
                return

            if user_choice == "0" or user_choice.lower() == "exit":
                print("[!] Exiting pipeline.")
                return
            elif user_choice == "7" or user_choice.lower() == "toggle":
                is_affiliate = not is_affiliate
                print(f">>> Đã chuyển mục tiêu sang: {'[Có Affiliate >1K FL]' if is_affiliate else '[Xây Kênh Kéo Follow]'}")
                continue
            else:
                break

        def ask_channel_type(current_aff: bool) -> bool:
            try:
                curr_desc = "1: Affiliate >1k fl" if current_aff else "2: Xây kênh kéo follow"
                ans = input(f"Xác nhận loại kênh [1: Affiliate >1k fl, 2: Xây kênh kéo follow] [Mặc định: {curr_desc}]: ").strip()
                if ans == "1":
                    return True
                elif ans == "2":
                    return False
            except (EOFError, KeyboardInterrupt):
                pass
            return current_aff

        if user_choice == "2" or user_choice.lower() == "draft":
            is_affiliate = ask_channel_type(is_affiliate)
            auto_mode = True
            save_draft = True
        elif user_choice == "3" or user_choice.lower() == "niche":
            is_affiliate = ask_channel_type(is_affiliate)
            auto_mode = True
            try:
                print("Chọn ngành hàng hot trend:")
                print("  [1] Gia dụng thông minh & Tiện ích (home)")
                print("  [2] Công nghệ, Điện thoại & Máy tính (tech)")
                print("  [3] Mỹ phẩm, Làm đẹp & Chăm sóc cá nhân (beauty)")
                print("  [4] Decor phòng & Nhà cửa (decor)")
                print("  [5] Thời trang & Phụ kiện (fashion)")
                n_choice = input("Chọn ngành hàng [Mặc định: 1]: ").strip()
                niche_map = {"1": "home", "2": "tech", "3": "beauty", "4": "decor", "5": "fashion"}
                niche = niche_map.get(n_choice, "home")
                action_c = input("Tự động đăng ngay hay Lưu nháp? [1: Đăng ngay, 2: Lưu nháp, 3: Xem lại]: ").strip()
                if action_c == "1":
                    auto_post = True
                elif action_c == "2":
                    save_draft = True
            except (EOFError, KeyboardInterrupt):
                niche = "home"
        elif user_choice == "4" or user_choice.lower() == "style":
            is_affiliate = ask_channel_type(is_affiliate)
            auto_mode = True
            try:
                print("Chọn phong cách kịch bản:")
                print("  [1] Bắt trend Gen Z hài hước, sôi nổi (trend)")
                print("  [2] Kịch tính, vạch trần 'Đừng mua nếu chưa xem...' (drama)")
                print("  [3] Flash sale giục giã, cấp bách số lượng có hạn (fomo)")
                print("  [4] Review trải nghiệm chân thật của người dùng (review)")
                s_choice = input("Chọn phong cách [Mặc định: 1]: ").strip()
                style_map = {"1": "trend", "2": "drama", "3": "fomo", "4": "review"}
                style = style_map.get(s_choice, "trend")
                action_c = input("Tự động đăng ngay hay Lưu nháp? [1: Đăng ngay, 2: Lưu nháp, 3: Xem lại]: ").strip()
                if action_c == "1":
                    auto_post = True
                elif action_c == "2":
                    save_draft = True
            except (EOFError, KeyboardInterrupt):
                style = "trend"
        elif user_choice == "5" or user_choice.lower() == "loop":
            is_affiliate = ask_channel_type(is_affiliate)
            auto_mode = True
            loop = True
            try:
                cnt_str = input("Số lượng video muốn sản xuất [Mặc định: 3]: ").strip()
                loop_count = int(cnt_str) if cnt_str.isdigit() else 3
                inv_str = input("Thời gian nghỉ giữa các video (giây) [Mặc định: 120]: ").strip()
                loop_interval = int(inv_str) if inv_str.isdigit() else 120
                post_choice = input("Tự động đăng hay Lưu nháp? [1: Đăng ngay, 2: Lưu nháp, 3: Xem lại]: ").strip()
                if post_choice == "1":
                    auto_post = True
                elif post_choice == "2":
                    save_draft = True
            except (EOFError, KeyboardInterrupt):
                loop_count = 3
                loop_interval = 120
        elif user_choice == "6" or (user_choice not in ["", "1"] and len(user_choice) > 1):
            if user_choice not in ["6", "manual"]:
                search_keyword = user_choice
            else:
                try:
                    search_keyword = input("Nhập từ khóa sản phẩm / chủ đề để săn video: ").strip()
                except (EOFError, KeyboardInterrupt):
                    return
            if not search_keyword:
                logger.warning("No search keyword provided. Exiting pipeline.")
                return
            is_affiliate = ask_channel_type(is_affiliate)
            try:
                action_c = input("Tự động đăng ngay hay Lưu nháp? [1: Đăng ngay, 2: Lưu nháp, 3: Xem lại]: ").strip()
                if action_c == "1":
                    auto_post = True
                elif action_c == "2":
                    save_draft = True
            except (EOFError, KeyboardInterrupt):
                pass
        else:
            # Option 1 / Default: Auto-Pilot with Auto-Post
            is_affiliate = ask_channel_type(is_affiliate)
            auto_mode = True
            auto_post = True

    # Execution Loop (Single run or Auto-Pilot continuous loop)
    iterations = loop_count if (loop and loop_count > 0) else 1

    for cycle in range(iterations):
        if loop and iterations > 1:
            print("\n" + "#" * 70)
            print(f"  [AUTO-PILOT LOOP] Bắt đầu chu kỳ {cycle + 1}/{iterations}")
            print("#" * 70 + "\n")

        # Determine target keyword
        current_keyword = search_keyword
        current_hint = None

        if auto_mode or not current_keyword:
            mode_desc = "Sản phẩm Hot Trend TikTok Shop (Affiliate)" if is_affiliate else "Sản phẩm / Mẹo độc lạ Xây Kênh Kéo Follow"
            logger.info(f"[AUTO-PILOT] Đang tìm kiếm {mode_desc} (ngành: {niche or 'Tất cả'})...")
            history = video_hunter.load_history()
            excluded = list(
                set(history.get("affiliate_history", []) + history.get("channel_titles", []))
            )

            discovered = ai_brain.discover_trending_products(
                exclude_keywords=excluded,
                count=5,
                niche=niche,
                is_affiliate=is_affiliate,
            )

            if discovered:
                chosen = discovered[0]
                current_keyword = chosen["keyword"]
                current_hint = chosen["name"]
                cat = chosen.get("category", "Trending")
                logger.info(
                    f"[AUTO-PILOT] Đã chọn: '{current_hint}' | "
                    f"Ngành hàng: {cat} | Từ khóa săn video: '{current_keyword}'"
                )

                # Record into affiliate_history to prevent repeating in next cycles
                if "affiliate_history" not in history:
                    history["affiliate_history"] = []
                history["affiliate_history"].append(current_hint)
                history["affiliate_history"].append(current_keyword)
                video_hunter.save_history(history)
            else:
                current_keyword = "bình giữ nhiệt hiển thị nhiệt độ review"
                current_hint = "Bình giữ nhiệt hiển thị nhiệt độ"

        # Execute single product pipeline
        success = run_single_pipeline(
            search_keyword=current_keyword,
            max_videos=max_videos,
            headless=headless,
            skip_upload=skip_upload,
            auto_post=auto_post,
            save_draft=save_draft,
            product_name_hint=current_hint,
            style=style,
            voice=voice,
            is_affiliate=is_affiliate,
        )

        # Handle pause between loops
        if loop and cycle < iterations - 1:
            logger.info(f"[AUTO-PILOT] Nghỉ {loop_interval}s trước khi bắt đầu video tiếp theo...")
            import time
            time.sleep(max(1, loop_interval))


def main() -> None:
    """CLI entrypoint parsing command line arguments and invoking run_pipeline."""
    parser = argparse.ArgumentParser(
        description="Automated TikTok Affiliate Video Creation & Upload Pipeline (R6 CLI)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-k", "--keyword",
        dest="keyword",
        type=str,
        default=None,
        help="Product search keyword to hunt on TikTok",
    )
    parser.add_argument(
        "-c", "--channel-url",
        dest="channel_url",
        type=str,
        default=None,
        help="TikTok channel URL to sync existing video titles to history",
    )
    parser.add_argument(
        "-m", "--max-videos",
        dest="max_videos",
        type=int,
        default=3,
        help="Maximum number of videos to download",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode during upload",
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        default=False,
        help="Skip the TikTok Studio upload stage",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        dest="auto_mode",
        default=False,
        help="Kích hoạt chế độ Auto-Pilot: AI tự tìm sản phẩm hot trend và làm video affiliate",
    )
    parser.add_argument(
        "--auto-post",
        action="store_true",
        dest="auto_post",
        default=False,
        help="Tự động nhấn nút Đăng/Post trên TikTok Studio",
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        dest="save_draft",
        default=False,
        help="Tự động lưu video vào Bản nháp TikTok Studio thay vì đăng ngay",
    )
    parser.add_argument(
        "--niche",
        dest="niche",
        type=str,
        default=None,
        choices=["home", "tech", "beauty", "decor", "fashion", "all"],
        help="Chọn ngành hàng hot trend (home, tech, beauty, decor, fashion)",
    )
    parser.add_argument(
        "--style",
        dest="style",
        type=str,
        default="trend",
        choices=["trend", "drama", "fomo", "review"],
        help="Chọn phong cách kịch bản (trend: Gen Z, drama: vạch trần, fomo: flash sale, review: chân thật)",
    )
    parser.add_argument(
        "--voice",
        dest="voice",
        type=str,
        default="vi-VN-HoaiMyNeural",
        help="Giọng đọc AI (female, male hoặc mã giọng edge-tts)",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        dest="loop",
        default=False,
        help="Chạy vòng lặp tự động liên tục nhiều sản phẩm",
    )
    parser.add_argument(
        "--count",
        dest="loop_count",
        type=int,
        default=3,
        help="Số lượng video affiliate cần sản xuất trong chế độ vòng lặp (mặc định: 3)",
    )
    parser.add_argument(
        "--affiliate",
        action="store_true",
        dest="is_affiliate",
        default=True,
        help="Chế độ Affiliate TikTok Shop: Kênh >1k follow, kêu gọi giỏ hàng góc trái (Mặc định)",
    )
    parser.add_argument(
        "--build-channel", "--no-affiliate",
        action="store_false",
        dest="is_affiliate",
        help="Chế độ Xây Kênh Kéo Follow: Kênh <1k follow, kêu gọi follow/tim/bình luận, không nhắc mua hàng",
    )
    parser.add_argument(
        "--interval",
        dest="loop_interval",
        type=int,
        default=120,
        help="Thời gian nghỉ (giây) giữa các chu kỳ sản xuất video (mặc định: 120s)",
    )

    args = parser.parse_args()

    run_pipeline(
        search_keyword=args.keyword,
        channel_url=args.channel_url,
        max_videos=args.max_videos,
        headless=args.headless,
        skip_upload=args.skip_upload,
        auto_mode=args.auto_mode,
        auto_post=args.auto_post,
        save_draft=args.save_draft,
        loop=args.loop,
        loop_count=args.loop_count,
        loop_interval=args.loop_interval,
        niche=args.niche,
        style=args.style,
        voice=args.voice,
        is_affiliate=args.is_affiliate,
    )


if __name__ == "__main__":
    main()

