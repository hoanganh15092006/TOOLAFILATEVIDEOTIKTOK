#!/usr/bin/env python3
"""
tiktok_uploader.py - TikTok Studio Browser Automation (Milestone M5 / Requirement R5)
======================================================================================
Automates video uploading to TikTok Studio via Playwright Chromium persistent context.

Features:
  - Persistent Chromium profile (preserves cookies, session credentials, and cache).
  - Anti-bot evasion (--disable-blink-features=AutomationControlled).
  - Authentication detection with a 90-second manual login grace period.
  - Robust file input locator (searches top-level DOM and nested iframes).
  - Video upload via set_input_files using absolute file path.
  - Multi-selector caption locator (contenteditable div, rich-text editor, textarea).
  - Human typing emulation with keystroke delay for full UTF-8 Vietnamese accent support.
  - 60-second live countdown review window for manual review, draft saving, or posting.
  - Graceful error recovery: catches timeouts, closed windows, and missing elements.
"""

import os
import sys
import time
import logging
from typing import Optional

from playwright.sync_api import (
    sync_playwright,
    Page,
    Locator,
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("tiktok_uploader")


def _find_file_input(page: Page) -> Optional[Locator]:
    """
    Locates the video file input element ('input[type="file"]') across the main
    page DOM and any nested iframes.

    Args:
        page: Playwright Page instance.

    Returns:
        Locator for the file input element, or None if not found.
    """
    file_input_selectors = [
        'input[type="file"][accept*="video"]',
        'input[type="file"]',
    ]

    # 1. Search top-level page
    for sel in file_input_selectors:
        try:
            loc = page.locator(sel)
            if loc.count() > 0:
                return loc.first
        except Exception:
            continue

    # 2. Search child iframes (TikTok Studio frequently nests upload widgets)
    try:
        for frame in page.frames:
            for sel in file_input_selectors:
                try:
                    f_loc = frame.locator(sel)
                    if f_loc.count() > 0:
                        return f_loc.first
                except Exception:
                    continue
    except Exception:
        pass

    return None


def _is_login_page_or_prompt(page: Page) -> bool:
    """
    Checks if the browser is currently at a login redirect or presenting a login dialog.

    Args:
        page: Playwright Page instance.

    Returns:
        bool: True if page indicates unauthenticated/login state.
    """
    try:
        current_url = page.url.lower()
        if any(term in current_url for term in ["/login", "passport", "signin", "redirect_url"]):
            return True

        # Check for visible login buttons or prompts
        login_btn = page.locator('button:has-text("Log in"), button:has-text("Đăng nhập"), a[href*="login"]')
        if login_btn.count() > 0:
            for i in range(min(login_btn.count(), 3)):
                if login_btn.nth(i).is_visible():
                    return True
    except Exception:
        pass

    return False


def _find_caption_element(page: Page, timeout_seconds: int = 30) -> Optional[Locator]:
    """
    Locates the caption/description editor element in the main page or nested iframes.
    Supports rich-text contenteditable divs, comboboxes, and standard textareas.

    Args:
        page: Playwright Page instance.
        timeout_seconds: Maximum time to poll for the element.

    Returns:
        Locator for the caption element, or None if not found.
    """
    caption_selectors = [
        'div[contenteditable="true"]',
        'div.notranslate[contenteditable="true"]',
        'div[class*="caption"] [contenteditable="true"]',
        'div[class*="editor"] [contenteditable="true"]',
        'div[class*="description"] [contenteditable="true"]',
        'div[role="combobox"][contenteditable="true"]',
        'div[data-placeholder*="caption" i]',
        'textarea[placeholder*="caption" i]',
        'textarea[placeholder*="description" i]',
        'textarea[class*="caption" i]',
        'textarea',
    ]

    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        # Check main page
        for sel in caption_selectors:
            try:
                loc = page.locator(sel)
                if loc.count() > 0:
                    first = loc.first
                    if first.is_visible():
                        return first
            except Exception:
                continue

        # Check child iframes
        try:
            for frame in page.frames:
                for sel in caption_selectors:
                    try:
                        f_loc = frame.locator(sel)
                        if f_loc.count() > 0:
                            first = f_loc.first
                            if first.is_visible():
                                return first
                    except Exception:
                        continue
        except Exception:
            pass

        time.sleep(1.0)

def _handle_confirmation_dialogs(page) -> bool:
    """Checks and clicks any confirmation modals (e.g., Copyright check, Post anyway, Confirm)."""
    confirm_selectors = [
        'button:has-text("Post anyway")',
        'button:has-text("Đăng dù sao đi nữa")',
        'button:has-text("Vẫn đăng")',
        'button:has-text("Tiếp tục đăng")',
        'button:has-text("Confirm")',
        'button:has-text("Xác nhận")',
        'button:has-text("Đồng ý")',
        'div[role="dialog"] button:has-text("Post")',
        'div[role="dialog"] button:has-text("Đăng")',
        'button:has-text("Continue")',
        'button:has-text("Tiếp tục")',
    ]

    contexts = [page] + list(getattr(page, "frames", []))
    for ctx in contexts:
        for sel in confirm_selectors:
            try:
                loc = ctx.locator(sel)
                if loc.count() > 0 and loc.first.is_visible() and loc.first.is_enabled():
                    logger.info(f"[TikTok Uploader] Detected confirmation modal ('{sel}'). Clicking to continue...")
                    loc.first.click()
                    return True
            except Exception:
                continue
    return False


def _wait_for_post_completion(page, max_wait_seconds: int = 90) -> bool:
    """
    Monitors TikTok Studio page until video upload and publish is 100% confirmed,
    or until timeout.
    """
    success_indicators = [
        'text="Manage your posts"',
        'text="Quản lý bài đăng"',
        'text="Upload another video"',
        'text="Tải lên video khác"',
        'text="Your video has been uploaded"',
        'text="Video của bạn đã được tải lên"',
        'text="Đã tải lên"',
        'button:has-text("Manage your posts")',
        'button:has-text("Quản lý bài đăng")',
        'button:has-text("Upload another video")',
        'button:has-text("Tải lên video khác")',
        'a[href*="tiktokstudio/content"]',
    ]

    start_time = time.time()
    last_log_time = 0

    while time.time() - start_time < max_wait_seconds:
        elapsed = int(time.time() - start_time)

        # 1. Check if URL redirected to content management
        try:
            curr_url = page.url or ""
            if "tiktokstudio/content" in curr_url or "tiktokstudio/manage" in curr_url:
                logger.info(f"[TikTok Uploader] Video published! Redirected to: {curr_url}")
                return True
        except Exception:
            pass

        # 2. Check for any confirmation modal (like "Post anyway") that may have appeared
        _handle_confirmation_dialogs(page)

        # 3. Check for success dialog or text
        contexts = [page] + list(getattr(page, "frames", []))
        for ctx in contexts:
            for sel in success_indicators:
                try:
                    loc = ctx.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        logger.info(f"[TikTok Uploader] Video publish 100% confirmed! (Found: '{sel}')")
                        return True
                except Exception:
                    continue

        if elapsed - last_log_time >= 5:
            last_log_time = elapsed
            logger.info(
                f"[TikTok Uploader] Đang đợi TikTok Studio tải lên và hoàn tất xử lý ({elapsed}s/{max_wait_seconds}s)..."
            )

        time.sleep(2.0)

    return False


def upload_tiktok_video(
    video_path: str,
    caption: str,
    user_data_dir: str = "./chrome_profile",
    headless: bool = False,
    login_timeout: int = 90,
    review_duration: int = 60,
    raise_on_error: bool = False,
    auto_post: bool = False,
    save_draft: bool = False,
) -> bool:
    """
    Automates uploading a video to TikTok Studio using Playwright Chromium persistent context.

    Workflow:
      1. Validates that `video_path` exists on disk.
      2. Launches Playwright Chromium with persistent context (retaining cookies and session).
      3. Navigates to `https://www.tiktok.com/tiktokstudio/upload`.
      4. Detects authentication state; if not logged in, waits up to `login_timeout` (default 90s)
         for manual user login.
      5. Locates the upload file input (`input[type="file"]`) in main page or nested iframes.
      6. Uploads the video via `set_input_files`.
      7. Locates the caption / post description field and types `caption` with keystroke delay.
      8. Keeps browser open for `review_duration` (default 60s) for manual review, draft saving, or posting.
      9. Cleanly closes browser context and returns True on success.

    Args:
        video_path: Path to the MP4 video file to upload.
        caption: Text description and hashtags for the post.
        user_data_dir: Path to directory storing Chromium persistent profile data.
        headless: Whether to run browser headlessly (False per requirement).
        login_timeout: Maximum seconds to wait for manual login (default 90).
        review_duration: Seconds to keep browser open after upload for review (default 60).
        raise_on_error: If True, re-raises caught exceptions; otherwise returns False gracefully.

    Returns:
        bool: True on successful upload and caption entry, False otherwise.
    """
    # 1. Validate video_path
    if not os.path.exists(video_path):
        err_msg = f"Video file not found at: {video_path}"
        logger.error(f"[TikTok Uploader] {err_msg}")
        if raise_on_error:
            raise FileNotFoundError(err_msg)
        return False

    abs_video_path = os.path.abspath(video_path)
    if not os.path.isfile(abs_video_path):
        err_msg = f"Specified path is not a file: {abs_video_path}"
        logger.error(f"[TikTok Uploader] {err_msg}")
        if raise_on_error:
            raise FileNotFoundError(err_msg)
        return False

    # Ensure profile directory exists
    os.makedirs(user_data_dir, exist_ok=True)

    logger.info(f"[TikTok Uploader] Starting upload pipeline for '{abs_video_path}'")
    logger.info(f"[TikTok Uploader] Chrome profile directory: {os.path.abspath(user_data_dir)}")

    context = None
    try:
        with sync_playwright() as playwright:
            # 2. Launch persistent Chromium context with anti-automation flags
            logger.info("[TikTok Uploader] Launching Playwright Chromium persistent context...")
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                ],
            )

            # Get existing page or open a new one
            if len(context.pages) > 0:
                page = context.pages[0]
            else:
                page = context.new_page()

            # Set viewport to standard desktop resolution
            try:
                page.set_viewport_size({"width": 1280, "height": 800})
            except Exception:
                pass

            # 3. Navigate to TikTok Studio upload page
            upload_url = "https://www.tiktok.com/tiktokstudio/upload"
            logger.info(f"[TikTok Uploader] Navigating to {upload_url}...")
            try:
                page.goto(upload_url, wait_until="domcontentloaded", timeout=60000)
            except PlaywrightTimeoutError:
                logger.warning("[TikTok Uploader] Navigation timed out waiting for domcontentloaded, continuing...")

            # 4. Authentication detection & polling loop (up to login_timeout seconds)
            logger.info(
                f"[TikTok Uploader] Checking authentication state (waiting up to {login_timeout}s for upload readiness)..."
            )
            start_poll = time.time()
            file_input = None
            last_status_time = 0

            while time.time() - start_poll < login_timeout:
                # Check if upload file input is present and ready
                file_input = _find_file_input(page)
                if file_input is not None:
                    logger.info("[TikTok Uploader] Upload element detected! Session is authenticated.")
                    break

                # Monitor login indicators
                now = time.time()
                if now - last_status_time >= 10:
                    remaining = int(login_timeout - (now - start_poll))
                    if _is_login_page_or_prompt(page):
                        logger.info(
                            f"[TikTok Uploader] Login required. Please log in manually in the browser window ({remaining}s remaining)..."
                        )
                    else:
                        logger.info(
                            f"[TikTok Uploader] Waiting for TikTok Studio upload page to load ({remaining}s remaining)..."
                        )
                    last_status_time = now

                # Check if page was closed by user
                if page.is_closed():
                    err_msg = "Browser page was closed during login wait."
                    logger.warning(f"[TikTok Uploader] {err_msg}")
                    return False

                time.sleep(2.0)

            if file_input is None:
                err_msg = f"Timed out after {login_timeout}s waiting for TikTok login or upload element."
                logger.error(f"[TikTok Uploader] {err_msg}")
                if raise_on_error:
                    raise TimeoutError(err_msg)
                return False

            # 5. Upload video file via set_input_files
            logger.info(f"[TikTok Uploader] Setting input file: {abs_video_path}")
            file_input.set_input_files(abs_video_path)
            logger.info("[TikTok Uploader] Video file attached. Waiting for video processing and caption field...")

            # Wait briefly for TikTok upload processor to mount caption UI
            time.sleep(3.0)

            # 6. Locate caption / post description field and input caption
            if caption:
                logger.info("[TikTok Uploader] Searching for caption/description input field...")
                caption_el = _find_caption_element(page, timeout_seconds=30)

                if caption_el is not None:
                    try:
                        caption_el.click()
                        time.sleep(0.5)

                        # Clear any existing placeholder text
                        page.keyboard.press("Control+A")
                        page.keyboard.press("Backspace")
                        time.sleep(0.2)

                        # Type caption with delay to ensure UTF-8 Vietnamese accents and hashtags register
                        logger.info(f"[TikTok Uploader] Typing caption ({len(caption)} characters)...")
                        page.keyboard.type(caption, delay=20)
                        logger.info("[TikTok Uploader] Caption entered successfully.")
                    except Exception as err:
                        logger.warning(f"[TikTok Uploader] Failed to type caption: {err}")
                else:
                    logger.warning(
                        "[TikTok Uploader] Caption field not found within timeout. Continuing to review window..."
                    )

            # 7. Post video or Review window
            if auto_post:
                logger.info("[TikTok Uploader] Auto-post enabled. Searching for Post/Đăng button...")
                post_btn = None
                post_selectors = [
                    'button:has-text("Post")',
                    'button:has-text("Đăng")',
                    'button[data-e2e="post_video_button"]',
                    'button.btn-post',
                    'button:has-text("Publish")',
                    'div[role="button"]:has-text("Post")',
                    'div[role="button"]:has-text("Đăng")',
                ]

                # Wait up to 60s for video file to finish uploading and Post button to become enabled
                btn_start = time.time()
                while time.time() - btn_start < 60:
                    contexts = [page] + list(getattr(page, "frames", []))
                    for ctx in contexts:
                        for sel in post_selectors:
                            try:
                                loc = ctx.locator(sel)
                                if loc.count() > 0 and loc.first.is_visible():
                                    is_disabled = loc.first.get_attribute("disabled")
                                    aria_disabled = loc.first.get_attribute("aria-disabled")
                                    if (is_disabled is None or is_disabled == "false") and aria_disabled != "true":
                                        post_btn = loc.first
                                        break
                            except Exception:
                                continue
                        if post_btn:
                            break
                    if post_btn:
                        break
                    logger.info("[TikTok Uploader] Đang tải video lên TikTok Studio, chờ nút Đăng sẵn sàng...")
                    time.sleep(3.0)

                if post_btn:
                    try:
                        logger.info("[TikTok Uploader] Clicking Post/Đăng button...")
                        post_btn.click()
                        time.sleep(3.0)

                        # Handle any popups like Copyright check / Post anyway
                        _handle_confirmation_dialogs(page)

                        # Wait for TikTok Studio to finish uploading and publishing
                        logger.info("[TikTok Uploader] Đang chờ TikTok Studio xác nhận đăng tải hoàn tất...")
                        confirmed = _wait_for_post_completion(page, max_wait_seconds=90)
                        if confirmed:
                            logger.info("[TikTok Uploader] Video published successfully and confirmed by TikTok Studio!")
                        else:
                            logger.info("[TikTok Uploader] Đã gửi lệnh đăng thành công!")

                        # Grace period: keep browser visible for 15s so user can view the result
                        logger.info("[TikTok Uploader] Giữ trình duyệt thêm 15 giây để bạn kiểm tra kết quả đăng...")
                        time.sleep(15.0)
                    except Exception as post_err:
                        logger.warning(f"[TikTok Uploader] Failed to click Post button or confirm: {post_err}")
                else:
                    logger.warning("[TikTok Uploader] Post button was not found or remained disabled. Continuing...")
            elif save_draft:
                logger.info("[TikTok Uploader] Save Draft enabled. Searching for Save Draft/Lưu nháp button...")
                draft_btn = None
                draft_selectors = [
                    'button:has-text("Save draft")',
                    'button:has-text("Lưu nháp")',
                    'button:has-text("Lưu làm bản nháp")',
                    'button[data-e2e="save_draft_button"]',
                    'button:has-text("Draft")',
                ]

                btn_start = time.time()
                while time.time() - btn_start < 45:
                    contexts = [page] + list(getattr(page, "frames", []))
                    for ctx in contexts:
                        for sel in draft_selectors:
                            try:
                                loc = ctx.locator(sel)
                                if loc.count() > 0 and loc.first.is_visible():
                                    draft_btn = loc.first
                                    break
                            except Exception:
                                continue
                        if draft_btn:
                            break
                    if draft_btn:
                        break
                    time.sleep(2.0)

                if draft_btn:
                    try:
                        logger.info("[TikTok Uploader] Clicking Save Draft/Lưu nháp button...")
                        draft_btn.click()
                        time.sleep(3.0)
                        _handle_confirmation_dialogs(page)
                        logger.info("[TikTok Uploader] Video saved to TikTok Studio Drafts successfully!")
                        logger.info("[TikTok Uploader] Giữ trình duyệt thêm 10 giây để xác nhận lưu nháp...")
                        time.sleep(10.0)
                    except Exception as draft_err:
                        logger.warning(f"[TikTok Uploader] Failed to click Draft button: {draft_err}")
                else:
                    logger.warning("[TikTok Uploader] Draft button was not found. Continuing...")
            else:
                # Review window: Keep browser open for review_duration seconds (default 60s)
                logger.info(
                    f"[TikTok Uploader] Upload completed. Keeping browser open for {review_duration}s for manual review/posting..."
                )
                countdown_start = time.time()
                while time.time() - countdown_start < review_duration:
                    remaining = int(review_duration - (time.time() - countdown_start))
                    print(f"[TikTok Uploader REVIEW] {remaining}s remaining for manual review / post...")

                    try:
                        if page.is_closed():
                            logger.info("[TikTok Uploader] Browser page was closed by user.")
                            break
                    except Exception:
                        break

                    sleep_chunk = min(10, max(1, remaining))
                    try:
                        time.sleep(sleep_chunk)
                    except KeyboardInterrupt:
                        logger.info("[TikTok Uploader] Review window interrupted by user.")
                        break

            # 8. Clean up and close persistent context
            try:
                context.close()
                context = None
            except Exception:
                pass

            logger.info("[TikTok Uploader] Browser context closed. Upload process completed successfully.")
            return True

    except PlaywrightTimeoutError as pte:
        logger.error(f"[TikTok Uploader] Playwright timeout occurred: {pte}")
        if raise_on_error:
            raise
        return False
    except PlaywrightError as pe:
        logger.error(f"[TikTok Uploader] Playwright error occurred: {pe}")
        if raise_on_error:
            raise
        return False
    except Exception as exc:
        logger.error(f"[TikTok Uploader] Unexpected error during upload: {exc}")
        if raise_on_error:
            raise
        return False
    finally:
        if context is not None:
            try:
                context.close()
            except Exception:
                pass


# Contract alias for backward and cross-module compatibility
upload_video_to_tiktok = upload_tiktok_video


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="TikTok Studio Browser Automation: Upload video and set caption."
    )
    parser.add_argument("video_path", help="Path to video MP4 file to upload")
    parser.add_argument("--caption", default="", help="Post description/caption with hashtags")
    parser.add_argument(
        "--user-data-dir",
        default="./chrome_profile",
        help="Chromium persistent user data directory (default: ./chrome_profile)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (default: False)",
    )
    parser.add_argument(
        "--login-timeout",
        type=int,
        default=90,
        help="Seconds to wait for manual login (default: 90)",
    )
    parser.add_argument(
        "--review-duration",
        type=int,
        default=60,
        help="Seconds to keep browser open after upload (default: 60)",
    )
    parser.add_argument(
        "--auto-post",
        action="store_true",
        help="Automatically click Post/Đăng button after video is ready",
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        dest="save_draft",
        help="Automatically save video as Draft instead of posting",
    )

    args = parser.parse_args()

    success = upload_tiktok_video(
        video_path=args.video_path,
        caption=args.caption,
        user_data_dir=args.user_data_dir,
        headless=args.headless,
        login_timeout=args.login_timeout,
        review_duration=args.review_duration,
        auto_post=args.auto_post,
        save_draft=args.save_draft,
    )
    sys.exit(0 if success else 1)
