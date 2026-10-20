#!/usr/bin/env python3
"""
test_adversarial_hunter_brain.py - Adversarial Empirical Stress Test Suite
==========================================================================
Adversarial challenge and empirical verification for video_hunter.py and ai_brain.py.

Focus:
1. video_hunter.py:
   - Empty string, whitespace, unicode strings as search keywords
   - Empty, whitespace, invalid channel URLs to sync_my_channel
   - history.json missing file, corrupted JSON, missing fields, wrong types
   - yt-dlp imageio-ffmpeg binding verification without system ffmpeg on PATH
   - Atomic saving with UTF-8 character preservation

2. ai_brain.py:
   - generate_script with missing API key, empty API key, whitespace, placeholder 'your_key_here'
   - generate_voice with empty string, short text, long Vietnamese text (75-90 words)
   - MP3 binary integrity and valid audio playback header verification
   - Nested output directory auto-creation
   - Regex sanitization stripping all director notes, bracketed text, markdown, whitespace
"""

import os
import gc
import sys
import json
import time
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import video_hunter
import ai_brain


class TestAdversarialVideoHunter(unittest.TestCase):
    """Adversarial stress-testing of video_hunter.py."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="adv_hunter_test_")
        self.test_history = os.path.join(self.temp_dir, "test_history.json")
        self.test_input_dir = os.path.join(self.temp_dir, "input_videos")
        os.makedirs(self.test_input_dir, exist_ok=True)

    def tearDown(self):
        gc.collect()
        time.sleep(0.05)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. Keyword Edge Cases
    # -------------------------------------------------------------------------
    def test_hunt_new_videos_empty_keyword(self):
        """Verify hunt_new_videos returns [] gracefully on empty string."""
        res = video_hunter.hunt_new_videos("", output_dir=self.test_input_dir, history_file=self.test_history)
        self.assertEqual(res, [])

    def test_hunt_new_videos_whitespace_keyword(self):
        """Verify hunt_new_videos returns [] gracefully on whitespace string."""
        res = video_hunter.hunt_new_videos("   \t\n  ", output_dir=self.test_input_dir, history_file=self.test_history)
        self.assertEqual(res, [])

    def test_hunt_new_videos_invalid_max_videos(self):
        """Verify hunt_new_videos returns [] gracefully when max_videos <= 0."""
        res_zero = video_hunter.hunt_new_videos("test", max_videos=0, output_dir=self.test_input_dir, history_file=self.test_history)
        self.assertEqual(res_zero, [])
        res_neg = video_hunter.hunt_new_videos("test", max_videos=-5, output_dir=self.test_input_dir, history_file=self.test_history)
        self.assertEqual(res_neg, [])

    def test_hunt_new_videos_unicode_keyword_query_formation(self):
        """Verify unicode string (Vietnamese + emojis) is handled without encoding crash."""
        unicode_kw = "🔥 Review đồ gia dụng thông minh Lock&Lock chính hãng 2026 🌟"
        # We mock yt_dlp.YoutubeDL to inspect the query and ensure no encoding issues occur
        with patch("video_hunter.yt_dlp.YoutubeDL") as mock_ydl_cls:
            mock_ydl = MagicMock()
            mock_ydl_cls.return_value.__enter__.return_value = mock_ydl
            mock_ydl.extract_info.return_value = {"entries": []}

            res = video_hunter.hunt_new_videos(unicode_kw, output_dir=self.test_input_dir, history_file=self.test_history)
            self.assertEqual(res, [])
            mock_ydl.extract_info.assert_called_once()
            called_query = mock_ydl.extract_info.call_args[0][0]
            self.assertTrue(called_query.startswith("ytsearch15:"))
            self.assertIn("Review đồ gia dụng thông minh", called_query)

    # -------------------------------------------------------------------------
    # 2. Channel URL Edge Cases
    # -------------------------------------------------------------------------
    def test_sync_my_channel_empty_url(self):
        """Verify sync_my_channel returns current titles gracefully on empty URL."""
        video_hunter.save_history({"uploaded_ids": [], "channel_titles": ["Existing 1"]}, self.test_history)
        res = video_hunter.sync_my_channel("", history_file=self.test_history)
        self.assertEqual(res, ["Existing 1"])

    def test_sync_my_channel_whitespace_url(self):
        """Verify sync_my_channel returns current titles gracefully on whitespace URL."""
        video_hunter.save_history({"uploaded_ids": [], "channel_titles": ["Existing 1"]}, self.test_history)
        res = video_hunter.sync_my_channel("   \t  ", history_file=self.test_history)
        self.assertEqual(res, ["Existing 1"])

    def test_sync_my_channel_invalid_url(self):
        """Verify sync_my_channel catches yt-dlp network/URL errors and does not crash."""
        video_hunter.save_history({"uploaded_ids": [], "channel_titles": ["Existing 1"]}, self.test_history)
        res = video_hunter.sync_my_channel("https://invalid-non-existent-domain-xyz-404.com/@notfound", history_file=self.test_history)
        self.assertEqual(res, ["Existing 1"])

    # -------------------------------------------------------------------------
    # 3. History Auto-Recovery & Corrupt Content
    # -------------------------------------------------------------------------
    def test_history_auto_recovery_missing_file(self):
        """Verify missing history.json is auto-created with default schema."""
        missing_path = os.path.join(self.temp_dir, "non_existent_history.json")
        self.assertFalse(os.path.exists(missing_path))
        data = video_hunter.load_history(missing_path)
        self.assertEqual(data, {"uploaded_ids": [], "channel_titles": []})
        self.assertTrue(os.path.exists(missing_path))

    def test_history_auto_recovery_corrupt_json(self):
        """Verify corrupted JSON syntax is recovered without crashing."""
        corrupt_path = os.path.join(self.temp_dir, "corrupt_history.json")
        with open(corrupt_path, "w", encoding="utf-8") as f:
            f.write("{ broken json syntax [!@#$%^&*")

        data = video_hunter.load_history(corrupt_path)
        self.assertEqual(data, {"uploaded_ids": [], "channel_titles": []})

        # Verify repaired file is valid JSON on disk
        with open(corrupt_path, "r", encoding="utf-8") as f:
            repaired = json.load(f)
        self.assertEqual(repaired, {"uploaded_ids": [], "channel_titles": []})

    def test_history_auto_recovery_missing_fields(self):
        """Verify history with missing fields has missing lists auto-injected."""
        partial_path = os.path.join(self.temp_dir, "partial_history.json")
        with open(partial_path, "w", encoding="utf-8") as f:
            json.dump({"uploaded_ids": ["vid123"]}, f)

        data = video_hunter.load_history(partial_path)
        self.assertEqual(data["uploaded_ids"], ["vid123"])
        self.assertEqual(data["channel_titles"], [])

    def test_history_auto_recovery_wrong_types(self):
        """Verify non-list fields or top-level array are normalized to default dict schema."""
        bad_type_path = os.path.join(self.temp_dir, "bad_type_history.json")
        with open(bad_type_path, "w", encoding="utf-8") as f:
            json.dump({"uploaded_ids": "not_a_list", "channel_titles": 42}, f)

        data = video_hunter.load_history(bad_type_path)
        self.assertEqual(data["uploaded_ids"], [])
        self.assertEqual(data["channel_titles"], [])

        # Top-level array
        with open(bad_type_path, "w", encoding="utf-8") as f:
            json.dump([1, 2, 3], f)
        data = video_hunter.load_history(bad_type_path)
        self.assertEqual(data, {"uploaded_ids": [], "channel_titles": []})

    def test_history_atomic_save_unicode(self):
        """Verify save_history preserves Vietnamese diacritics and is atomically written."""
        vietnamese_titles = [
            "Đánh giá chi tiết nồi chiên không dầu Lock&Lock",
            "Mở hộp máy lọc không khí khử khuẩn siêu xịn",
            "Top 5 sản phẩm tiện ích cho nhà bếp 2026",
        ]
        test_data = {
            "uploaded_ids": ["vn_clip_01", "vn_clip_02"],
            "channel_titles": vietnamese_titles,
        }
        video_hunter.save_history(test_data, self.test_history)

        with open(self.test_history, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        self.assertEqual(loaded["channel_titles"], vietnamese_titles)
        self.assertEqual(loaded["uploaded_ids"], ["vn_clip_01", "vn_clip_02"])

    # -------------------------------------------------------------------------
    # 4. FFmpeg Binding Verification Without System FFmpeg on PATH
    # -------------------------------------------------------------------------
    def test_ffmpeg_binding_fallback_to_imageio_ffmpeg(self):
        """Verify imageio-ffmpeg provides valid binary even if system PATH has no ffmpeg."""
        with patch("shutil.which", return_value=None):
            resolved_ffmpeg = video_hunter.get_ffmpeg_path()
            self.assertIsNotNone(resolved_ffmpeg, "get_ffmpeg_path() returned None when system ffmpeg is absent")
            self.assertTrue(os.path.exists(resolved_ffmpeg), f"Resolved FFmpeg path does not exist on disk: {resolved_ffmpeg}")


class TestAdversarialAIBrain(unittest.TestCase):
    """Adversarial stress-testing of ai_brain.py."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="adv_brain_test_")
        self.created_files = []

    def tearDown(self):
        gc.collect()
        time.sleep(0.05)
        for p in self.created_files:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. API Key Validation
    # -------------------------------------------------------------------------
    def test_create_genai_client_unset_key(self):
        """Verify create_genai_client raises ValueError when key is unset."""
        orig_key = os.environ.get("GEMINI_API_KEY")
        try:
            os.environ.pop("GEMINI_API_KEY", None)
            with self.assertRaises(ValueError) as ctx:
                ai_brain.create_genai_client(api_key=None)
            self.assertIn("GEMINI_API_KEY is not set or invalid", str(ctx.exception))
        finally:
            if orig_key is not None:
                os.environ["GEMINI_API_KEY"] = orig_key

    def test_create_genai_client_empty_and_whitespace_key(self):
        """Verify create_genai_client raises ValueError when key is empty or whitespace."""
        for bad_key in ["", "   ", "\t\n  "]:
            with self.assertRaises(ValueError) as ctx:
                ai_brain.create_genai_client(api_key=bad_key)
            self.assertIn("GEMINI_API_KEY is not set or invalid", str(ctx.exception))

    def test_create_genai_client_placeholder_key(self):
        """Verify create_genai_client raises ValueError when key is placeholder 'your_key_here'."""
        for placeholder in ["your_key_here", "  your_key_here  "]:
            with self.assertRaises(ValueError) as ctx:
                ai_brain.create_genai_client(api_key=placeholder)
            self.assertIn("GEMINI_API_KEY is not set or invalid", str(ctx.exception))

    def test_generate_script_key_validation(self):
        """Verify generate_script immediately raises ValueError on invalid keys."""
        dummy_video = os.path.join(self.temp_dir, "dummy.mp4")
        with open(dummy_video, "wb") as f:
            f.write(b"video bytes")
        self.created_files.append(dummy_video)

        orig_key = os.environ.get("GEMINI_API_KEY")
        try:
            os.environ.pop("GEMINI_API_KEY", None)
            with self.assertRaises(ValueError):
                ai_brain.generate_script(dummy_video, api_key=None)

            with self.assertRaises(ValueError):
                ai_brain.generate_script(dummy_video, api_key="")

            with self.assertRaises(ValueError):
                ai_brain.generate_script(dummy_video, api_key="your_key_here")
        finally:
            if orig_key is not None:
                os.environ["GEMINI_API_KEY"] = orig_key

    # -------------------------------------------------------------------------
    # 2. Regex Sanitization Stress-Testing
    # -------------------------------------------------------------------------
    def test_sanitize_voiceover_edge_cases(self):
        """Verify sanitize_voiceover removes director notes, bracketed cues, markdown, extra spaces."""
        # Empty and None
        self.assertEqual(ai_brain.sanitize_voiceover(""), "")
        self.assertEqual(ai_brain.sanitize_voiceover(None), "")

        # Director notes in parentheses and brackets
        raw_text = "[nhạc nền mở đầu] Bạn có tin được không? (cười lớn) Đây chính là sản phẩm hot nhất! {cảnh quay cận cảnh}"
        expected = "Bạn có tin được không? Đây chính là sản phẩm hot nhất!"
        self.assertEqual(ai_brain.sanitize_voiceover(raw_text), expected)

        # Markdown tags and cues
        markdown_text = "**Siêu phẩm 2026** #1: [Hook: xem ngay] Nồi chiên không dầu _cực đỉnh_ `giá rẻ`."
        expected_md = "Siêu phẩm 2026 1: Nồi chiên không dầu cực đỉnh giá rẻ."
        self.assertEqual(ai_brain.sanitize_voiceover(markdown_text), expected_md)

        # Nested brackets / multiple annotations
        complex_text = " [Intro] (nhạc dạo) Xin chào cả nhà! [Cảnh 1 (zoom in)] Chiếc máy này đỉnh thật sự. "
        self.assertEqual(ai_brain.sanitize_voiceover(complex_text), "Xin chào cả nhà! Chiếc máy này đỉnh thật sự.")

    # -------------------------------------------------------------------------
    # 3. Edge-TTS Voice Synthesis Empirical Verification
    # -------------------------------------------------------------------------
    def test_generate_voice_empty_or_whitespace_raises(self):
        """Verify generate_voice raises ValueError on empty or whitespace text."""
        out_path = os.path.join(self.temp_dir, "fail_voice.mp3")
        with self.assertRaises(ValueError):
            ai_brain.generate_voice("", output_audio=out_path)
        with self.assertRaises(ValueError):
            ai_brain.generate_voice("    \t\n ", output_audio=out_path)

    def test_generate_voice_short_text_and_mp3_header(self):
        """Verify edge-tts voice generation on short phrase produces valid MP3 with valid header."""
        out_path = os.path.join(self.temp_dir, "short_voice.mp3")
        self.created_files.append(out_path)

        res = ai_brain.generate_voice("Xin chào Việt Nam!", output_audio=out_path)
        self.assertEqual(res, out_path)
        self.assertTrue(os.path.exists(out_path))

        file_size = os.path.getsize(out_path)
        self.assertGreater(file_size, 500, f"MP3 size {file_size} bytes is suspiciously small")

        # Verify MP3 Header (ID3 tag header b'ID3' or MPEG Sync Frame b'\xff\xfb' / b'\xff\xf3' / b'\xff\xf2')
        with open(out_path, "rb") as f:
            header = f.read(10)
        is_id3 = header.startswith(b"ID3")
        is_mpeg_sync = (header[0] == 0xFF and (header[1] & 0xE0) == 0xE0)
        self.assertTrue(is_id3 or is_mpeg_sync, f"Invalid MP3 audio header: {header[:4]!r}")

    def test_generate_voice_long_text_and_playback_validity(self):
        """
        Verify edge-tts voice generation on realistic 75-90 word Vietnamese affiliate script.
        Asserts file creation, valid duration > 10s, and MoviePy AudioFileClip compatibility.
        """
        script = (
            "Bạn có biết tại sao chiếc máy hút bụi cầm tay này lại đang cháy hàng trên toàn quốc không? "
            "Với lực hút siêu khủng lên tới mười hai nghìn pascal, máy dễ dàng hút sạch mọi bụi mịn và lông thú cưng chỉ trong một lần lướt. "
            "Thiết kế không dây gọn nhẹ chưa tới một cân, pin trâu dùng liên tục bốn mươi phút cực kỳ tiện lợi. "
            "Bấm ngay vào giỏ hàng góc trái bên dưới màn hình để nhận ưu đãi giảm giá độc quyền hôm nay nhé!"
        )
        word_count = len(script.split())
        self.assertTrue(75 <= word_count <= 95, f"Test script word count {word_count} is out of expected range")

        out_path = os.path.join(self.temp_dir, "long_voice.mp3")
        self.created_files.append(out_path)

        res = ai_brain.generate_voice(script, output_audio=out_path)
        self.assertEqual(res, out_path)
        self.assertTrue(os.path.exists(out_path))

        # Check audio readability and duration with MoviePy
        from moviepy.editor import AudioFileClip
        audio = AudioFileClip(out_path)
        dur = audio.duration
        audio.close()
        del audio
        gc.collect()

        self.assertGreater(dur, 10.0, f"Audio duration {dur:.2f}s is shorter than expected for 80-word script")
        self.assertLess(dur, 35.0, f"Audio duration {dur:.2f}s is longer than expected (>35s)")

    def test_generate_voice_nested_directory_creation(self):
        """Verify generate_voice automatically creates non-existent nested output directories."""
        nested_out = os.path.join(self.temp_dir, "nested", "subfolder", "audio.mp3")
        self.created_files.append(nested_out)

        res = ai_brain.generate_voice("Kiểm tra tạo thư mục tự động.", output_audio=nested_out)
        self.assertEqual(res, nested_out)
        self.assertTrue(os.path.exists(nested_out))
        self.assertGreater(os.path.getsize(nested_out), 500)


if __name__ == "__main__":
    unittest.main(verbosity=2)
