#!/usr/bin/env python3
"""
sync_to_github.py - Autonomous Devlog Generation & GitHub Sync Tool
===================================================================
Project: Automated TikTok Video Creation & Tool Self-Learning System
Path: .agents/skills/tool-learner-evaluator/scripts/sync_to_github.py

Responsibilities:
  1. Creates or updates structured daily Devlogs in docs/devlogs/devlog_YYYY-MM-DD.md.
  2. Updates docs/devlogs/README.md table of contents automatically.
  3. Audits git status to ensure zero accidental staging of sensitive files (.env, media).
  4. Stages documentation, experience traces, benchmarks, proposals, and approved tool files.
  5. Commits with conventional commit messages and pushes to GitHub with automatic rebase on conflicts.
  6. Outputs the final commit hash and status.
"""

import os
import sys
import argparse
import datetime
import subprocess
from pathlib import Path
from typing import Optional, List

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
DEVLOG_DIR = WORKSPACE_ROOT / "docs" / "devlogs"
DEVLOG_INDEX = DEVLOG_DIR / "README.md"

SENSITIVE_PATTERNS = [
    ".env",
    "chrome_profile",
    "input_videos",
    "output_videos",
    ".mp4",
    ".mp3",
    "voiceover.mp3",
]


def run_cmd(cmd: List[str], cwd: Path = WORKSPACE_ROOT) -> subprocess.CompletedProcess:
    """Executes a subprocess command safely within the workspace."""
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result


def get_current_branch() -> str:
    """Returns the current git branch name."""
    res = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if res.returncode == 0:
        return res.stdout.strip()
    return "main"


def ensure_devlog_index() -> None:
    """Ensures docs/devlogs/README.md exists with standard header."""
    DEVLOG_DIR.mkdir(parents=True, exist_ok=True)
    if not DEVLOG_INDEX.exists():
        initial_content = (
            "# Nhật Ký Tiến Hóa Hệ Thống (Devlog Index)\n\n"
            "Mục lục tổng hợp toàn bộ hành trình tự học, nâng cấp tool và tối ưu hóa hệ thống từ thực tế.\n\n"
            "| Ngày | Tiêu Đề | Tool Tinh Chỉnh | Trạng Thái |\n"
            "| :--- | :--- | :--- | :--- |\n"
        )
        DEVLOG_INDEX.write_text(initial_content, encoding="utf-8")


def append_to_devlog_index(date_str: str, title: str, tool_name: str, filename: str) -> None:
    """Appends an entry to the Devlog index if not already present."""
    ensure_devlog_index()
    content = DEVLOG_INDEX.read_text(encoding="utf-8")
    entry_link = f"[{title}](./{filename})"
    line = f"| {date_str} | {entry_link} | `{tool_name}` | Hoàn thành |\n"
    if filename not in content:
        content += line
        DEVLOG_INDEX.write_text(content, encoding="utf-8")


def generate_devlog(
    title: str,
    tool_name: str,
    context: str,
    heuristics: str,
    changelog: str,
    benchmark: str,
    date_str: Optional[str] = None,
) -> Path:
    """Creates or updates the daily Devlog markdown file."""
    if not date_str:
        date_str = datetime.date.today().strftime("%Y-%m-%d")

    DEVLOG_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"devlog_{date_str}.md"
    devlog_path = DEVLOG_DIR / filename

    content_template = f"""# Devlog: {title}

- **Ngày ghi nhận**: {date_str}
- **Công cụ trọng tâm**: `{tool_name}`
- **Hệ thống**: Self-Learning from Experience Loop

---

## 1. Bối Cảnh & Vấn Đề Thực Tế (Context)
{context.strip() if context else "Thực thi kiểm thử và vận hành tự động hoá tool trong môi trường thực tế."}

---

## 2. Bài Học Rút Ra (Learned Heuristics)
{heuristics.strip() if heuristics else "Đúc kết kinh nghiệm qua các ca chạy thực tế, xử lý trường hợp biên và tối ưu hoá."}

---

## 3. Thay Đổi Kỹ Thuật (Changelog & Technical Improvements)
{changelog.strip() if changelog else "Cập nhật mã nguồn, refactor hàm lõi và cải thiện khả năng phục hồi lỗi."}

---

## 4. Benchmark & Hiệu Năng (Performance Verification)
{benchmark.strip() if benchmark else "Kiểm định toàn bộ các tiêu chí trong benchmark_tests.json."}
"""

    devlog_path.write_text(content_template, encoding="utf-8")
    append_to_devlog_index(date_str, title, tool_name, filename)
    return devlog_path


def audit_git_safety() -> bool:
    """Audits staged or pending files to ensure sensitive items are never pushed."""
    status_res = run_cmd(["git", "status", "--porcelain"])
    lines = status_res.stdout.splitlines()
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
        # Check against sensitive patterns
        for pattern in SENSITIVE_PATTERNS:
            if pattern in cleaned_line and not cleaned_line.endswith(".gitignore"):
                if cleaned_line.startswith("A ") or cleaned_line.startswith("M "):
                    print(f"[ERROR] Phát hiện tệp nhạy cảm trong git staging: {cleaned_line}")
                    return False
    return True


def sync_github(
    commit_message: str,
    tool_files: Optional[List[str]] = None,
    push: bool = True,
) -> bool:
    """Stages appropriate files, commits and pushes cleanly to GitHub."""
    branch = get_current_branch()
    print(f"[SYNC] Bắt đầu đồng bộ hóa lên nhánh '{branch}'...")

    # Stage documentation and knowledge bases
    paths_to_stage = [
        "docs/devlogs",
        ".agents/experience_memory",
        ".agents/evals",
        ".agents/skills",
        ".agents/rules",
        ".gitignore",
    ]
    if tool_files:
        paths_to_stage.extend(tool_files)

    for p in paths_to_stage:
        if (WORKSPACE_ROOT / p).exists():
            run_cmd(["git", "add", p])

    if not audit_git_safety():
        print("[ABORT] Hủy push vì phát hiện tệp nhạy cảm.")
        return False

    # Check if there are changes to commit
    diff_check = run_cmd(["git", "diff", "--cached", "--quiet"])
    if diff_check.returncode == 0:
        print("[INFO] Không có thay đổi nào mới cần commit.")
        return True

    # Commit
    commit_res = run_cmd(["git", "commit", "-m", commit_message])
    if commit_res.returncode != 0:
        print(f"[ERROR] Commit thất bại:\n{commit_res.stderr}")
        return False

    print(f"[COMMIT SUCCESS] {commit_message}")

    if not push:
        print("[INFO] Cờ --no-push được bật. Bỏ qua bước git push.")
        return True

    # Push with rebase fallback
    print(f"[PUSH] Đang push lên remote origin/{branch}...")
    push_res = run_cmd(["git", "push", "origin", branch])

    if push_res.returncode != 0:
        print("[REBASE] Push bị từ chối hoặc có xung đột. Thử chạy git pull --rebase...")
        pull_res = run_cmd(["git", "pull", "--rebase", "origin", branch])
        if pull_res.returncode != 0:
            print(f"[ERROR] Git rebase thất bại:\n{pull_res.stderr}")
            return False
        # Push again after rebase
        push_res = run_cmd(["git", "push", "origin", branch])
        if push_res.returncode != 0:
            print(f"[ERROR] Push thất bại sau rebase:\n{push_res.stderr}")
            return False

    # Retrieve last commit hash
    log_res = run_cmd(["git", "rev-parse", "--short", "HEAD"])
    commit_hash = log_res.stdout.strip()
    print(f"[SYNC COMPLETED] Commit {commit_hash} đã được đẩy thành công lên GitHub!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Autonomous Devlog Generator & GitHub Synchronizer")
    parser.add_argument("--title", default="Tiến Hóa Hệ Thống & Tự Học Thực Tế", help="Tiêu đề Devlog")
    parser.add_argument("--tool", default="pipeline", help="Tên tool/script trọng tâm")
    parser.add_argument("--context", default="", help="Bối cảnh và bài toán vừa giải")
    parser.add_argument("--heuristics", default="", help="Mẹo và quy tắc rút ra")
    parser.add_argument("--changelog", default="", help="Các cải tiến kỹ thuật")
    parser.add_argument("--benchmark", default="", help="Kết quả đo đạc benchmark")
    parser.add_argument("--message", default="", help="Git commit message")
    parser.add_argument("--tool-files", nargs="*", default=[], help="Danh sách file tool cần stage bổ sung")
    parser.add_argument("--no-push", action="store_true", help="Chỉ commit nội bộ, không push")

    args = parser.parse_args()

    devlog_file = generate_devlog(
        title=args.title,
        tool_name=args.tool,
        context=args.context,
        heuristics=args.heuristics,
        changelog=args.changelog,
        benchmark=args.benchmark,
    )
    print(f"[DEVLOG CREATED] {devlog_file}")

    commit_msg = args.message
    if not commit_msg:
        today = datetime.date.today().strftime("%Y-%m-%d")
        commit_msg = f"feat(tool-evolution): upgrade {args.tool} and update devlog [{today}]"

    success = sync_github(
        commit_message=commit_msg,
        tool_files=args.tool_files,
        push=not args.no_push,
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
