#!/usr/bin/env python3
"""
test_challenger_adversarial.py - Adversarial Stress-Testing Harness for Challenger 2
====================================================================================
Tests:
  1. video_editor.py:
     - Aspect ratio stress test:
       * 16:9 widescreen, 4:3 standard, 1:1 square, 21:9 ultra-wide, 9:20 ultra-tall.
       * Exact function-level tests for `center_crop_and_resize`.
       * Full multi-aspect render test verifying strictly 1080x1920 (9:16) output.
     - Win32 file locking and handle release:
       * 3 consecutive end-to-end renders.
       * Deletion/overwriting of inputs and outputs between renders without [WinError 32].
  2. tiktok_uploader.py:
     - Missing video file validation (file missing, directory instead of file, raise_on_error flag).
     - Headless flag pass-through to Playwright launch_persistent_context (True and False).
     - CLI execution and exit codes (help, missing arguments, non-existent file).
  3. main.py:
     - CLI help output verification.
     - CLI argument parsing errors (invalid types, unknown flags).
     - Preflight checks behavior under missing/placeholder GEMINI_API_KEY.
     - Error boundaries & graceful exits (empty search keyword, hunter empty, module exceptions).
"""

import os
import gc
import sys
import time
import shutil
import tempfile
import unittest
import subprocess
from unittest.mock import MagicMock, patch

import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import video_editor
import tiktok_uploader
import main


class TestVideoEditorAdversarial(unittest.TestCase):
    """Stress tests for video_editor.py covering aspect ratios, vertical 1080x1920, and Win32 locks."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="adv_editor_test_")
        self.inputs_dir = os.path.join(self.temp_dir, "input_videos")
        self.outputs_dir = os.path.join(self.temp_dir, "output_videos")
        os.makedirs(self.inputs_dir, exist_ok=True)
        os.makedirs(self.outputs_dir, exist_ok=True)
        self.created_audio = []

    def tearDown(self):
        gc.collect()
        time.sleep(0.2)
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except Exception:
                pass

    def _create_synthetic_audio(self, duration: float = 3.0) -> str:
        from moviepy.editor import AudioClip
        audio_path = os.path.join(self.temp_dir, f"audio_{int(time.time()*1000)}.mp3")
        self.created_audio.append(audio_path)

        def _make_frame(t):
            return [np.sin(440 * 2 * np.pi * t), np.sin(440 * 2 * np.pi * t)]

        clip = AudioClip(_make_frame, duration=duration, fps=22050)
        clip.write_audiofile(audio_path, fps=22050, logger=None)
        clip.close()
        del clip
        gc.collect()
        return audio_path

    def _create_synthetic_video(self, path: str, size: tuple, duration: float = 3.0, color=(128, 128, 128)):
        from moviepy.editor import ColorClip
        clip = ColorClip(size=size, color=color, duration=duration)
        clip.write_videofile(path, fps=15, logger=None)
        clip.close()
        del clip
        gc.collect()

    def test_center_crop_and_resize_diverse_aspect_ratios(self):
        """Unit test center_crop_and_resize with 16:9, 4:3, 1:1, ultra-wide 21:9, and ultra-tall 9:20."""
        from moviepy.editor import ColorClip

        test_cases = [
            ("16:9 widescreen", (1280, 720)),
            ("4:3 standard", (640, 480)),
            ("1:1 square", (600, 600)),
            ("21:9 ultra-wide", (840, 360)),
            ("9:20 ultra-tall", (450, 1000)),
            ("Exact 9:16 target", (1080, 1920)),
        ]

        for label, (w, h) in test_cases:
            with self.subTest(aspect_ratio=label, size=(w, h)):
                clip = ColorClip(size=(w, h), color=(100, 150, 200), duration=1.0)
                transformed = video_editor.center_crop_and_resize(clip, target_w=1080, target_h=1920)

                self.assertEqual(
                    tuple(transformed.size),
                    (1080, 1920),
                    f"Failed for {label} ({w}x{h}): output size {transformed.size} != (1080, 1920)",
                )

                transformed.close()
                clip.close()
                del clip, transformed
                gc.collect()

    def test_multi_aspect_ratio_render_pipeline(self):
        """Stress-test edit_and_render with an input folder containing all 5 aspect ratios simultaneously."""
        from moviepy.editor import VideoFileClip

        ratios = [
            ("16_9.mp4", (640, 360), (255, 0, 0)),
            ("4_3.mp4", (640, 480), (0, 255, 0)),
            ("1_1.mp4", (500, 500), (0, 0, 255)),
            ("21_9.mp4", (840, 360), (255, 255, 0)),
            ("9_20.mp4", (450, 1000), (255, 0, 255)),
        ]

        for fname, size, color in ratios:
            p = os.path.join(self.inputs_dir, fname)
            self._create_synthetic_video(p, size=size, duration=3.0, color=color)

        audio_path = self._create_synthetic_audio(duration=3.5)
        output_path = os.path.join(self.outputs_dir, "final_multi_aspect.mp4")

        result = video_editor.edit_and_render(
            input_dir=self.inputs_dir,
            audio_path=audio_path,
            output_path=output_path,
            cleanup_inputs=True,
            logger_opt=None,
        )

        self.assertEqual(result, output_path)
        self.assertTrue(os.path.exists(output_path), "Output file was not created.")
        self.assertGreater(os.path.getsize(output_path), 1000, "Rendered output file too small.")

        # Verify output resolution and aspect ratio
        out_clip = VideoFileClip(output_path)
        res = tuple(out_clip.size)
        dur = out_clip.duration
        out_clip.close()
        del out_clip
        gc.collect()

        self.assertEqual(res, (1080, 1920), f"Expected resolution (1080, 1920), got {res}")
        self.assertAlmostEqual(res[0] / res[1], 9.0 / 16.0, places=3)
        self.assertAlmostEqual(dur, 3.5, delta=0.6)

        # Verify input files cleaned up
        remaining = [f for f in os.listdir(self.inputs_dir) if f.endswith(".mp4")]
        self.assertEqual(len(remaining), 0, f"Inputs were not cleaned up: {remaining}")

    def test_successive_renders_win32_locks(self):
        """Stress test: 3 consecutive renders to check for [WinError 32] file locking issues."""
        from moviepy.editor import VideoFileClip

        audio_path = self._create_synthetic_audio(duration=2.5)

        for iteration in range(3):
            # Create fresh inputs
            clip_path = os.path.join(self.inputs_dir, f"clip_iter_{iteration}.mp4")
            self._create_synthetic_video(clip_path, size=(640, 360), duration=3.0)

            out_path = os.path.join(self.outputs_dir, f"final_iter_{iteration}.mp4")

            # Execute render
            res_path = video_editor.edit_and_render(
                input_dir=self.inputs_dir,
                audio_path=audio_path,
                output_path=out_path,
                cleanup_inputs=True,
                logger_opt=None,
            )

            self.assertTrue(os.path.exists(res_path))
            # Test immediate read/write access to verify no lingering file locks
            clip = VideoFileClip(res_path)
            self.assertEqual(tuple(clip.size), (1080, 1920))
            clip.close()
            del clip
            gc.collect()

            # Verify we can immediately delete or overwrite the output without WinError 32
            try:
                with open(res_path, "a+b") as f:
                    f.write(b"")
            except PermissionError as pe:
                self.fail(f"Win32 file lock on output video during iteration {iteration}: {pe}")


class TestTikTokUploaderAdversarial(unittest.TestCase):
    """Stress tests for tiktok_uploader.py covering arguments, missing files, and headless pass-through."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="adv_uploader_test_")
        self.test_video = os.path.join(self.temp_dir, "real_video.mp4")
        with open(self.test_video, "wb") as f:
            f.write(b"fake mp4 video bytes")

    def tearDown(self):
        gc.collect()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_missing_video_validation_scenarios(self):
        """Verify handling when video path does not exist or is a directory."""
        non_existent = os.path.join(self.temp_dir, "non_existent.mp4")

        # 1. Non-existent file with raise_on_error=False
        res = tiktok_uploader.upload_tiktok_video(non_existent, caption="test", raise_on_error=False)
        self.assertFalse(res)

        # 2. Non-existent file with raise_on_error=True
        with self.assertRaises(FileNotFoundError):
            tiktok_uploader.upload_tiktok_video(non_existent, caption="test", raise_on_error=True)

        # 3. Path is a directory instead of a file
        with self.assertRaises(FileNotFoundError):
            tiktok_uploader.upload_tiktok_video(self.temp_dir, caption="test", raise_on_error=True)

        res_dir = tiktok_uploader.upload_tiktok_video(self.temp_dir, caption="test", raise_on_error=False)
        self.assertFalse(res_dir)

    @patch("tiktok_uploader.sync_playwright")
    def test_headless_flag_passthrough(self, mock_playwright):
        """Verify headless flag is faithfully passed through to Playwright's launch_persistent_context."""
        mock_p = MagicMock()
        mock_playwright.return_value.__enter__.return_value = mock_p
        mock_context = MagicMock()
        mock_p.chromium.launch_persistent_context.return_value = mock_context
        mock_page = MagicMock()
        mock_page.is_closed.return_value = False
        mock_page.url = "https://www.tiktok.com/tiktokstudio/upload"
        mock_context.pages = [mock_page]

        # Case 1: headless=True
        tiktok_uploader.upload_tiktok_video(
            video_path=self.test_video,
            caption="test",
            user_data_dir=os.path.join(self.temp_dir, "p1"),
            headless=True,
            login_timeout=1,
            review_duration=0,
        )
        _, kwargs_true = mock_p.chromium.launch_persistent_context.call_args
        self.assertTrue(kwargs_true.get("headless"))

        # Case 2: headless=False
        tiktok_uploader.upload_tiktok_video(
            video_path=self.test_video,
            caption="test",
            user_data_dir=os.path.join(self.temp_dir, "p2"),
            headless=False,
            login_timeout=1,
            review_duration=0,
        )
        _, kwargs_false = mock_p.chromium.launch_persistent_context.call_args
        self.assertFalse(kwargs_false.get("headless"))

    def test_cli_execution(self):
        """Verify tiktok_uploader.py CLI help and missing argument behaviors."""
        # 1. CLI help
        res = subprocess.run(
            [sys.executable, "tiktok_uploader.py", "--help"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("--headless", res.stdout)
        self.assertIn("--user-data-dir", res.stdout)
        self.assertIn("video_path", res.stdout)

        # 2. Missing video_path positional arg
        res_missing = subprocess.run(
            [sys.executable, "tiktok_uploader.py"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_missing.returncode, 2)  # Argparse exits with 2 for missing required args

        # 3. Non-existent file via CLI
        res_nonexist = subprocess.run(
            [sys.executable, "tiktok_uploader.py", "does_not_exist_abc.mp4"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_nonexist.returncode, 1)  # sys.exit(1) on failure


class TestMainAdversarial(unittest.TestCase):
    """Stress tests for main.py orchestrator CLI, argument parsing, preflights, and error recovery."""

    def test_main_cli_help(self):
        """Verify python main.py --help output contains all expected pipeline options."""
        res = subprocess.run(
            [sys.executable, "main.py", "--help"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("--keyword", res.stdout)
        self.assertIn("--channel-url", res.stdout)
        self.assertIn("--max-videos", res.stdout)
        self.assertIn("--headless", res.stdout)
        self.assertIn("--skip-upload", res.stdout)

    def test_main_cli_invalid_arguments(self):
        """Verify argparse rejection of unrecognized flags or invalid types."""
        # Unrecognized flag
        res1 = subprocess.run(
            [sys.executable, "main.py", "--non-existent-option"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res1.returncode, 2)

        # Invalid type for --max-videos
        res2 = subprocess.run(
            [sys.executable, "main.py", "--max-videos", "invalid_number"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res2.returncode, 2)

    def test_preflight_checks(self):
        """Verify preflight checks create directories and handle missing GEMINI_API_KEY gracefully."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=True):
            status = main.preflight_checks()
            self.assertTrue(status)
            self.assertTrue(os.path.isdir("input_videos"))
            self.assertTrue(os.path.isdir("output_videos"))

    @patch("main.video_hunter")
    @patch("main.ai_brain")
    @patch("main.video_editor")
    @patch("main.tiktok_uploader")
    def test_run_pipeline_full_success_flow(self, mock_uploader, mock_editor, mock_brain, mock_hunter):
        """Verify complete pipeline coordination when all stages succeed."""
        mock_hunter.hunt_new_videos.return_value = ["input_videos/test_vid.mp4"]
        mock_brain.generate_script.return_value = {
            "product_name": "Tai nghe bluetooth",
            "voiceover": "Tai nghe bluetooth giá rẻ chất lượng cao",
            "caption": "Tai nghe xịn #review",
        }
        mock_editor.edit_and_render.return_value = "output_videos/final_video.mp4"
        mock_uploader.upload_tiktok_video.return_value = True

        main.run_pipeline(
            search_keyword="tai nghe",
            max_videos=2,
            headless=True,
            skip_upload=False,
        )

        mock_hunter.hunt_new_videos.assert_called_once_with(search_keyword="tai nghe", max_videos=2)
        mock_brain.generate_script.assert_called_once_with("input_videos/test_vid.mp4")
        mock_brain.generate_voice.assert_called_once()
        mock_editor.edit_and_render.assert_called_once()
        mock_uploader.upload_tiktok_video.assert_called_once_with(
            video_path="output_videos/final_video.mp4",
            caption="Tai nghe xịn #review",
            headless=True,
            is_affiliate=True,
            product_name="Tai nghe bluetooth",
        )

    @patch("main.video_hunter")
    @patch("main.tiktok_uploader")
    def test_run_pipeline_skip_upload_flag(self, mock_uploader, mock_hunter):
        """Verify --skip-upload prevents invoking tiktok_uploader."""
        mock_hunter.hunt_new_videos.return_value = ["input_videos/test_vid.mp4"]
        with patch("main.ai_brain") as mock_brain, patch("main.video_editor") as mock_editor:
            mock_brain.generate_script.return_value = {"product_name": "P", "voiceover": "V", "caption": "C"}
            mock_editor.edit_and_render.return_value = "output_videos/final_video.mp4"

            main.run_pipeline(
                search_keyword="test",
                skip_upload=True,
            )

            mock_uploader.upload_tiktok_video.assert_not_called()

    @patch("main.video_hunter")
    def test_run_pipeline_hunter_empty_results(self, mock_hunter):
        """Verify graceful exit when hunt_new_videos returns empty list."""
        mock_hunter.hunt_new_videos.return_value = []
        with patch("main.ai_brain") as mock_brain:
            # Should exit without calling brain
            main.run_pipeline(search_keyword="nonexistent_product_12345")
            mock_brain.generate_script.assert_not_called()

    def test_run_pipeline_empty_keyword_non_interactive(self):
        """Verify empty keyword without user input terminates gracefully."""
        with patch("builtins.input", side_effect=EOFError):
            main.run_pipeline(search_keyword="")


if __name__ == "__main__":
    unittest.main()
