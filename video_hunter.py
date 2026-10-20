"""
video_hunter.py - R2: Video Hunter & Deduplication Module
=========================================================
Project: Automated TikTok Affiliate Video Creation & Upload Pipeline
Scope: Milestone M2 (Requirement R2)

Responsibilities:
  1. sync_my_channel(channel_url, history_file='history.json'):
     Extracts video titles from channel_url using yt-dlp flat extraction and
     appends new titles to history.json['channel_titles'] without duplicates.
     Returns list of titles.
  2. hunt_new_videos(search_keyword, max_videos=3, output_dir='input_videos', history_file='history.json'):
     Searches candidate review videos using yt-dlp (ytsearch15:{search_keyword}),
     filters out videos >90s or already present in history.json['uploaded_ids'],
     downloads up to max_videos watermark-free MP4 videos to output_dir/{id}.mp4,
     and updates history.json['uploaded_ids'] immediately upon each download.
     Returns list of downloaded file paths.
  3. Safe atomic history.json loading, saving, and auto-initialization.
"""

import os
import sys
import json
import logging
import tempfile
import shutil
from typing import List, Dict, Optional, Any

import yt_dlp
import imageio_ffmpeg

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [video_hunter] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

DEFAULT_HISTORY: Dict[str, Any] = {
    "uploaded_ids": [],
    "channel_titles": [],
    "affiliate_history": [],
}


def get_ffmpeg_path() -> Optional[str]:
    """
    Resolves the bundled FFmpeg binary from imageio-ffmpeg or system PATH.
    Ensures video merging and conversion works on Windows without system ffmpeg.
    """
    try:
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.exists(exe):
            return exe
    except Exception as exc:
        logger.debug("imageio_ffmpeg resolution failed: %s", exc)

    return shutil.which("ffmpeg")


def load_history(history_file: str = "history.json") -> Dict[str, Any]:
    """
    Loads deduplication database from history_file.
    Auto-initializes the file with default schema if missing or corrupted.
    """
    if not os.path.exists(history_file):
        save_history(DEFAULT_HISTORY, history_file)
        return json.loads(json.dumps(DEFAULT_HISTORY))

    try:
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                data = json.loads(json.dumps(DEFAULT_HISTORY))
            if not isinstance(data.get("uploaded_ids"), list):
                data["uploaded_ids"] = []
            if not isinstance(data.get("channel_titles"), list):
                data["channel_titles"] = []
            if not isinstance(data.get("affiliate_history"), list):
                data["affiliate_history"] = []
            return data
    except Exception as exc:
        logger.warning("Failed to read %s (%s). Re-initializing with defaults.", history_file, exc)
        save_history(DEFAULT_HISTORY, history_file)
        return json.loads(json.dumps(DEFAULT_HISTORY))


def save_history(data: Dict[str, Any], history_file: str = "history.json") -> None:
    """
    Saves history data to history_file atomically using tempfile and os.replace
    with UTF-8 encoding to support Vietnamese characters and prevent corruption.
    """
    abs_history = os.path.abspath(history_file)
    dirname = os.path.dirname(abs_history)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    # Use same directory to ensure atomic replace on Windows across same drive
    temp_fd, temp_path = tempfile.mkstemp(dir=dirname, suffix=".tmp")
    try:
        with open(temp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(temp_path, abs_history)
    except Exception:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        raise


def sync_my_channel(channel_url: str, history_file: str = "history.json") -> List[str]:
    """
    Extracts video titles from channel_url using yt-dlp flat extraction and
    appends new titles to history.json['channel_titles'] without duplicates.

    Args:
        channel_url: Channel, playlist, or user profile URL.
        history_file: Path to history.json.

    Returns:
        List[str]: Updated list of channel titles in history.json.
    """
    history = load_history(history_file)
    channel_titles: List[str] = history.get("channel_titles", [])
    if not isinstance(channel_titles, list):
        channel_titles = []
        history["channel_titles"] = channel_titles

    if not channel_url or not str(channel_url).strip():
        logger.warning("sync_my_channel called with empty channel_url.")
        return list(channel_titles)

    clean_url = str(channel_url).strip()

    ydl_opts: Dict[str, Any] = {
        "extract_flat": True,
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "extractor_args": {"youtube": {"player_client": ["mweb", "android"]}},
    }

    ffmpeg_exe = get_ffmpeg_path()
    if ffmpeg_exe:
        ydl_opts["ffmpeg_location"] = ffmpeg_exe

    extracted_titles: List[str] = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            if info:
                entries = info.get("entries")
                if entries is not None:
                    for entry in entries:
                        if isinstance(entry, dict):
                            title = entry.get("title")
                            if title and isinstance(title, str) and title.strip():
                                extracted_titles.append(title.strip())
                elif isinstance(info, dict):
                    title = info.get("title")
                    if title and isinstance(title, str) and title.strip():
                        extracted_titles.append(title.strip())
    except Exception as exc:
        logger.warning("Error extracting channel info from %s: %s", clean_url, exc)
        return list(channel_titles)

    existing_set = set(channel_titles)
    new_count = 0
    for title in extracted_titles:
        if title not in existing_set:
            channel_titles.append(title)
            existing_set.add(title)
            new_count += 1

    if new_count > 0:
        logger.info("Added %d new titles to channel_titles.", new_count)
        save_history(history, history_file)
    else:
        logger.info("No new titles to add for %s.", clean_url)

    return list(channel_titles)


def hunt_new_videos(
    search_keyword: str,
    max_videos: int = 3,
    output_dir: str = "input_videos",
    history_file: str = "history.json",
) -> List[str]:
    """
    Searches TikTok candidate review videos using yt-dlp (query: ytsearch15:{search_keyword}),
    filters out videos >90 seconds or already in history.json['uploaded_ids'],
    downloads up to max_videos watermark-free MP4 videos into output_dir/{id}.mp4,
    and updates history.json['uploaded_ids'] immediately upon each download.

    Args:
        search_keyword: Search keyword (e.g., 'nồi chiên không dầu review').
        max_videos: Maximum number of new videos to download (default: 3).
        output_dir: Directory where raw clips are saved (default: 'input_videos').
        history_file: Path to history.json.

    Returns:
        List[str]: Relative or absolute file paths of successfully downloaded MP4 files.
    """
    if not search_keyword or not str(search_keyword).strip():
        logger.warning("hunt_new_videos called with empty search_keyword. Returning empty list.")
        return []

    if max_videos <= 0:
        logger.warning("max_videos must be > 0. Got %d.", max_videos)
        return []

    clean_keyword = str(search_keyword).strip()
    if (
        clean_keyword.startswith("ytsearch")
        or clean_keyword.startswith("http://")
        or clean_keyword.startswith("https://")
    ):
        query = clean_keyword
    else:
        query = f"ytsearch15:{clean_keyword}"

    history = load_history(history_file)
    uploaded_ids = set(history.get("uploaded_ids", []))

    os.makedirs(output_dir, exist_ok=True)
    ffmpeg_exe = get_ffmpeg_path()

    # Search options (flat extraction, no media download)
    search_opts: Dict[str, Any] = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "extractor_args": {"youtube": {"player_client": ["mweb", "android"]}},
    }
    if ffmpeg_exe:
        search_opts["ffmpeg_location"] = ffmpeg_exe

    logger.info("Searching for candidates with query: %s", query)
    try:
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            search_result = ydl.extract_info(query, download=False)
    except Exception as exc:
        logger.warning("Search query failed for '%s': %s", query, exc)
        return []

    if not search_result:
        logger.warning("No search results returned for '%s'.", query)
        return []

    raw_entries = search_result.get("entries")
    if raw_entries is None:
        raw_entries = [search_result] if search_result.get("id") else []
    elif not isinstance(raw_entries, (list, tuple)):
        raw_entries = list(raw_entries)

    # Filter candidate entries
    candidates: List[Dict[str, Any]] = []
    for entry in raw_entries:
        if not entry or not isinstance(entry, dict):
            continue
        video_id = entry.get("id")
        if not video_id or not isinstance(video_id, str):
            continue

        # Filter 1: Deduplication against history.json
        if video_id in uploaded_ids:
            logger.debug("Skipping already uploaded video ID: %s", video_id)
            continue

        # Filter 2: Duration <= 90 seconds
        duration = entry.get("duration")
        if duration is not None:
            try:
                if float(duration) > 90.0:
                    logger.debug("Skipping video %s: duration %.1fs > 90s", video_id, float(duration))
                    continue
            except (ValueError, TypeError):
                pass

        candidates.append(entry)

    # Fallback to shorts query if no candidate <= 90s was found in standard search
    if not candidates and not clean_keyword.endswith("shorts") and not clean_keyword.startswith("http"):
        fallback_query = f"ytsearch15:{clean_keyword} shorts"
        logger.info("No candidates <=90s found. Searching fallback Shorts query: %s", fallback_query)
        try:
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                fb_result = ydl.extract_info(fallback_query, download=False)
            if fb_result:
                fb_entries = fb_result.get("entries") or []
                for entry in fb_entries:
                    if not entry or not isinstance(entry, dict):
                        continue
                    v_id = entry.get("id")
                    if not v_id or v_id in uploaded_ids:
                        continue
                    dur = entry.get("duration")
                    if dur is not None:
                        try:
                            if float(dur) > 90.0:
                                continue
                        except (ValueError, TypeError):
                            pass
                    candidates.append(entry)
        except Exception as fb_err:
            logger.debug("Fallback shorts search failed: %s", fb_err)

    logger.info("Found %d candidate videos matching criteria.", len(candidates))
    if not candidates:
        return []

    # Download options
    download_opts: Dict[str, Any] = {
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": False,
        "extractor_args": {"youtube": {"player_client": ["mweb", "android"]}},
    }
    if ffmpeg_exe:
        download_opts["ffmpeg_location"] = ffmpeg_exe

    downloaded_paths: List[str] = []

    for entry in candidates:
        if len(downloaded_paths) >= max_videos:
            break

        video_id = entry.get("id")
        if not video_id:
            continue

        # Re-check history in case another process modified it
        fresh_history = load_history(history_file)
        if video_id in fresh_history.get("uploaded_ids", []):
            continue

        target_url = (
            entry.get("webpage_url")
            or entry.get("url")
            or f"https://www.youtube.com/watch?v={video_id}"
        )

        expected_mp4 = os.path.join(output_dir, f"{video_id}.mp4")
        logger.info("Downloading candidate [%d/%d]: %s", len(downloaded_paths) + 1, max_videos, video_id)

        try:
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                info_dict = ydl.extract_info(target_url, download=True)

            # Secondary duration verification on full metadata
            if info_dict and isinstance(info_dict, dict):
                real_duration = info_dict.get("duration")
                if real_duration is not None:
                    try:
                        if float(real_duration) > 90.0:
                            logger.info(
                                "Video %s full duration %.1fs > 90s, discarding.",
                                video_id,
                                float(real_duration),
                            )
                            if os.path.exists(expected_mp4):
                                os.remove(expected_mp4)
                            continue
                    except (ValueError, TypeError):
                        pass

            # Verify downloaded file on disk
            final_file = None
            if os.path.exists(expected_mp4) and os.path.getsize(expected_mp4) > 0:
                final_file = expected_mp4
            else:
                for fname in os.listdir(output_dir):
                    if fname.startswith(f"{video_id}."):
                        cand = os.path.join(output_dir, fname)
                        if os.path.getsize(cand) > 0:
                            final_file = cand
                            break

            if not final_file:
                logger.warning("Downloaded file for %s not found on disk.", video_id)
                continue

            # Update history immediately and atomically upon successful download
            current_history = load_history(history_file)
            if video_id not in current_history.get("uploaded_ids", []):
                current_history.setdefault("uploaded_ids", []).append(video_id)
                save_history(current_history, history_file)
                uploaded_ids.add(video_id)

            downloaded_paths.append(final_file)
            logger.info("Saved %s and recorded in %s", final_file, history_file)

        except Exception as dl_err:
            logger.warning("Failed to download video %s: %s", video_id, dl_err)
            continue

    return downloaded_paths


if __name__ == "__main__":
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        print(f"Hunting videos for keyword: {keyword}")
        results = hunt_new_videos(keyword, max_videos=1)
        print("Downloaded:", results)
    else:
        print("video_hunter module loaded. Usage: python video_hunter.py <search_keyword>")
