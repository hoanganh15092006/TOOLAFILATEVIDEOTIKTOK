# Project: Automated TikTok Affiliate Video Creation & Upload Pipeline

## Architecture
The system is an end-to-end Python pipeline that automates TikTok affiliate marketing video generation and publication:
```
[User CLI: main.py]
         │
         ▼
[video_hunter.py] ──(yt-dlp)──> Download trending clips to input_videos/{id}.mp4 & update history.json
         │
         ▼
[ai_brain.py] ─────(gemini-2.5-flash)──> Analyze clip, generate Vietnamese script & caption, cleanup cloud file
         │         └─(edge-tts)────────> Synthesize voiceover to voiceover.mp3
         ▼
[video_editor.py] ──(MoviePy)──────────> Remix subclips (2.5-4s), anti-fingerprint (flip 50%, colorx 1.04, crop 9:16 1080x1920),
         │                               attach voiceover.mp3, render output_videos/final_video.mp4, cleanup input clips
         ▼
[tiktok_uploader.py] (Playwright)─────> Launch persistent Chromium, 90s login wait, upload final_video.mp4, type caption, 60s review window
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Directory Scaffolding | Create `input_videos/`, `output_videos/`, `.env` template, `history.json` with initial schema | M1 | R1 |
| 2 | Dependency Specification & Installation | `requirements.txt` with pinned versions (`google-genai`, `yt-dlp`, `edge-tts`, `moviepy==1.0.3`, `playwright`, `python-dotenv`, `imageio-ffmpeg`), pip install & Playwright Chromium verification | M1 | R1 |
| 3 | Channel Sync | `sync_my_channel(channel_url)`: flat title extraction via yt-dlp, update `history.json["channel_titles"]` | M2 | R2 |
| 4 | Video Hunt & Download | `hunt_new_videos(search_keyword, max_videos=3)`: ytsearch15, filter uploaded IDs and >90s, download watermark-free MP4 via imageio-ffmpeg binding | M2 | R2 |
| 5 | Deduplication Tracking | Atomic read/write updates to `history.json["uploaded_ids"]` immediately upon download | M2 | R2 |
| 6 | Multimodal Video Script Gen | Upload first video to Gemini, poll until ACTIVE, prompt `gemini-2.5-flash` with structured JSON schema (75-90 Vietnamese words, 3s hook, bottom-left cart CTA, 5 hashtags) | M3 | R3 |
| 7 | Cloud File Cleanup | Immediate deletion of uploaded file in Google Cloud (`client.files.delete`) in guaranteed `finally` block | M3 | R3 |
| 8 | Voiceover Synthesis | `generate_voice(text, output_audio="voiceover.mp3")` using `edge-tts` (`vi-VN-HoaiMyNeural`, `rate="+10%"`) | M3 | R3 |
| 9 | Audio-Video Duration Sync | Read `voiceover.mp3` duration via MoviePy, slice random subclips (2.5s-4s) from `input_videos/` to match | M4 | R4 |
| 10 | Anti-fingerprinting Remix | Mute original audio, 50% random horizontal flip (`vfx.mirror_x`), color adjustment (`vfx.colorx(1.04)`), center crop/resize to 9:16 vertical 1080x1920 | M4 | R4 |
| 11 | Final Render & Cleanup | Render `output_videos/final_video.mp4` (fps=30, libx264, aac), release Win32 file handles, clean up `input_videos/` raw clips | M4 | R4 |
| 12 | Persistent Browser Context | Launch Playwright Chromium with persistent context (`user_data_dir="./chrome_profile"`, `headless=False`, anti-bot evasion) | M5 | R5 |
| 13 | Login Polling & Navigation | Navigate to `https://www.tiktok.com/tiktokstudio/upload`, detect authentication state, wait up to 90s for manual login | M5 | R5 |
| 14 | Upload & Caption Automation | Select and upload `output_videos/final_video.mp4`, type caption with UTF-8 accents and hashtags, hold 60s review window | M5 | R5 |
| 15 | Central Pipeline CLI | `main.py` CLI accepting `search_keyword` interactively or via args, executing stages sequentially with error recovery | M6 | R6 |
| 16 | Verification Test Suite | `test_pipeline.py` testing imports, edge-tts mp3 generation, synthetic 1080x1920 video editing, and Gemini API key error handling | M7 | R7 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Scaffolding & Dependencies | Create folder tree, `.env`, `history.json`, `requirements.txt`, install dependencies, verify Playwright Chromium | none | DONE |
| M2 | Video Hunter & Deduplication | Implement `video_hunter.py` with `sync_my_channel` and `hunt_new_videos`, ffmpeg_location binding, atomic history updates | M1 | DONE |
| M3 | AI Brain & Voice Synthesis | Implement `ai_brain.py` with `google-genai` client, structured JSON prompt, cloud cleanup, edge-tts voice synthesis | M1 | DONE |
| M4 | Video Editor & Anti-fingerprinting | Implement `video_editor.py` with duration sync, subclip slicing, 9:16 vertical 1080x1920 crop/resize, anti-fingerprinting, Win32 handle cleanup | M1 | DONE |
| M5 | TikTok Studio Uploader | Implement `tiktok_uploader.py` with Playwright persistent context, 90s login wait, file input upload, caption input, 60s review window | M1 | DONE |
| M6 | Central CLI Pipeline | Implement `main.py` tying Hunter -> Brain -> Editor -> Uploader sequentially with interactive CLI and error boundaries | M2, M3, M4, M5 | DONE |
| M7 | Final E2E Verification & Hardening | Implement `test_pipeline.py` covering imports, voice synthesis, synthetic 1080x1920 video editing, Gemini error handling; execute 100% test pass | M1, M2, M3, M4, M5, M6 | DONE |

## Interface Contracts

### 1. `video_hunter.py`
```python
def sync_my_channel(channel_url: str) -> list[str]:
    """Extracts video titles from channel_url and updates history.json['channel_titles']. Returns list of titles."""

def hunt_new_videos(search_keyword: str, max_videos: int = 3) -> list[str]:
    """Searches TikTok for keyword, skips uploaded_ids & videos > 90s, downloads up to max_videos to input_videos/{id}.mp4.
    Updates history.json['uploaded_ids'] immediately. Returns list of downloaded file paths."""
```

### 2. `ai_brain.py`
```python
class VideoScriptResponse(BaseModel):
    product_name: str
    voiceover: str
    caption: str

def generate_script(video_path: str, api_key: str | None = None) -> dict:
    """Uploads video_path to Gemini, polls until ACTIVE, requests gemini-2.5-flash with structured JSON output,
    deletes file in finally block, and returns {'product_name': ..., 'voiceover': ..., 'caption': ...}."""

def generate_voice(text: str, output_audio: str = "voiceover.mp3") -> str:
    """Uses edge-tts (voice vi-VN-HoaiMyNeural, rate +10%) to synthesize speech from text into output_audio.
    Returns output_audio path."""
```

### 3. `video_editor.py`
```python
def edit_and_render(
    input_dir: str = "input_videos",
    audio_path: str = "voiceover.mp3",
    output_path: str = "output_videos/final_video.mp4"
) -> str:
    """Reads voiceover.mp3 duration, cuts random 2.5-4s subclips from input_dir, applies anti-fingerprinting
    (mute, 50% mirror_x, colorx(1.04), 9:16 center-crop/resize 1080x1920), concatenates, attaches audio,
    renders final_video.mp4 (fps=30, libx264, aac), safely closes and deletes input clips. Returns output_path."""
```

### 4. `tiktok_uploader.py`
```python
def upload_tiktok_video(
    video_path: str,
    caption: str,
    user_data_dir: str = "./chrome_profile",
    headless: bool = False
) -> bool:
    """Launches Playwright Chromium with persistent context, navigates to upload URL, waits up to 90s for login,
    uploads video_path, types caption into post description, waits 60s for review, closes browser. Returns True on success."""
```

### 5. `main.py`
```python
def run_pipeline(search_keyword: str | None = None) -> None:
    """Main CLI orchestrator: prompts for search_keyword if not supplied, executes hunter -> brain -> editor -> uploader."""
```

## Code Layout
```
d:/Tool/
├── input_videos/            # Downloaded raw source clips
├── output_videos/           # Rendered final videos
├── chrome_profile/          # Playwright persistent Chromium user data
├── .env                     # GEMINI_API_KEY=your_key_here
├── history.json             # {"uploaded_ids": [], "channel_titles": []}
├── requirements.txt         # Pinned project dependencies
├── video_hunter.py          # R2: yt-dlp search, download & deduplication
├── ai_brain.py              # R3: Gemini 2.5 Flash script gen & edge-tts voiceover
├── video_editor.py          # R4: MoviePy anti-fingerprint editing & 1080x1920 export
├── tiktok_uploader.py       # R5: Playwright TikTok Studio uploader
├── main.py                  # R6: Central sequential CLI pipeline
└── test_pipeline.py         # R7: Offline automated verification test suite
```
