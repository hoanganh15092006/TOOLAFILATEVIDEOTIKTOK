#!/usr/bin/env python3
"""
test_tiktok_uploader.py - Unit test suite for tiktok_uploader.py
"""

import os
import gc
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import tiktok_uploader


class TestTikTokUploader(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="tiktok_test_")
        self.test_video = os.path.join(self.temp_dir, "sample.mp4")
        with open(self.test_video, "wb") as f:
            f.write(b"sample video bytes")

    def tearDown(self):
        gc.collect()
        if os.path.exists(self.test_video):
            os.remove(self.test_video)
        if os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except Exception:
                pass

    def test_missing_video_path_returns_false(self):
        non_existent = os.path.join(self.temp_dir, "does_not_exist.mp4")
        res = tiktok_uploader.upload_tiktok_video(non_existent, caption="Sample")
        self.assertFalse(res)

    def test_missing_video_path_raise_on_error(self):
        non_existent = os.path.join(self.temp_dir, "does_not_exist.mp4")
        with self.assertRaises(FileNotFoundError):
            tiktok_uploader.upload_tiktok_video(non_existent, caption="Sample", raise_on_error=True)

    def test_is_login_page_detection(self):
        page = MagicMock()
        page.url = "https://www.tiktok.com/login"
        self.assertTrue(tiktok_uploader._is_login_page_or_prompt(page))

        page.url = "https://www.tiktok.com/passport/web/account"
        self.assertTrue(tiktok_uploader._is_login_page_or_prompt(page))

        page.url = "https://www.tiktok.com/tiktokstudio/upload"
        page.locator.return_value.count.return_value = 0
        self.assertFalse(tiktok_uploader._is_login_page_or_prompt(page))

    def test_find_file_input_in_main_page(self):
        page = MagicMock()
        mock_input = MagicMock()
        page.locator.return_value.count.return_value = 1
        page.locator.return_value.first = mock_input
        found = tiktok_uploader._find_file_input(page)
        self.assertEqual(found, mock_input)

    def test_find_file_input_in_nested_frame(self):
        page = MagicMock()
        page.locator.return_value.count.return_value = 0
        frame = MagicMock()
        mock_input = MagicMock()
        frame.locator.return_value.count.return_value = 1
        frame.locator.return_value.first = mock_input
        page.frames = [frame]
        found = tiktok_uploader._find_file_input(page)
        self.assertEqual(found, mock_input)

    def test_find_caption_element(self):
        page = MagicMock()
        mock_caption = MagicMock()
        mock_caption.is_visible.return_value = True
        page.locator.return_value.count.return_value = 1
        page.locator.return_value.first = mock_caption
        page.frames = []
        found = tiktok_uploader._find_caption_element(page, timeout_seconds=1)
        self.assertEqual(found, mock_caption)

    @patch("tiktok_uploader.sync_playwright")
    def test_upload_success_flow(self, mock_playwright):
        mock_p = MagicMock()
        mock_playwright.return_value.__enter__.return_value = mock_p
        mock_context = MagicMock()
        mock_p.chromium.launch_persistent_context.return_value = mock_context

        mock_page = MagicMock()
        mock_page.is_closed.return_value = False
        mock_page.url = "https://www.tiktok.com/tiktokstudio/upload"
        mock_context.pages = [mock_page]

        mock_file_input = MagicMock()
        mock_caption_el = MagicMock()
        mock_caption_el.is_visible.return_value = True

        def locator_side_effect(sel):
            loc = MagicMock()
            if "input[type" in sel:
                loc.count.return_value = 1
                loc.first = mock_file_input
            elif "contenteditable" in sel:
                loc.count.return_value = 1
                loc.first = mock_caption_el
            else:
                loc.count.return_value = 0
            return loc

        mock_page.locator.side_effect = locator_side_effect
        mock_page.frames = []

        res = tiktok_uploader.upload_tiktok_video(
            video_path=self.test_video,
            caption="Đánh giá sản phẩm cực tốt! #review #affiliate",
            user_data_dir=os.path.join(self.temp_dir, "chrome_test"),
            headless=True,
            login_timeout=2,
            review_duration=1,
        )
        self.assertTrue(res)
        mock_file_input.set_input_files.assert_called_once_with(os.path.abspath(self.test_video))
        mock_page.keyboard.type.assert_called_once_with("Đánh giá sản phẩm cực tốt! #review #affiliate", delay=20)
        mock_context.close.assert_called()

    @patch("tiktok_uploader.sync_playwright")
    def test_upload_timeout_flow(self, mock_playwright):
        mock_p = MagicMock()
        mock_playwright.return_value.__enter__.return_value = mock_p
        mock_context = MagicMock()
        mock_p.chromium.launch_persistent_context.return_value = mock_context
        mock_page = MagicMock()
        mock_page.is_closed.return_value = False
        mock_page.url = "https://www.tiktok.com/login"
        mock_context.pages = [mock_page]
        mock_page.locator.return_value.count.return_value = 0
        mock_page.frames = []

        res = tiktok_uploader.upload_tiktok_video(
            video_path=self.test_video,
            caption="Test caption",
            user_data_dir=os.path.join(self.temp_dir, "chrome_test"),
            headless=True,
            login_timeout=1,
            review_duration=0,
        )
        self.assertFalse(res)


if __name__ == "__main__":
    unittest.main()
