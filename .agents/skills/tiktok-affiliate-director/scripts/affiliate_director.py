#!/usr/bin/env python3
"""
Affiliate Director Runner Script for Skill
"""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from affiliate_director import produce_affiliate_video_from_image, main

if __name__ == "__main__":
    main()
