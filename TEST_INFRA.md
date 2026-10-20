# E2E Test Infra: Automated TikTok Affiliate Pipeline

## Test Philosophy
- Opaque-box, requirement-driven testing based on ORIGINAL_REQUEST.md (R1-R7).
- Offline testability: Fast execution using synthetic media generators (ColorClip), mock/unit checks, and error assertions.
- Methodology: Equivalence Partitioning, Boundary Value Analysis, Pairwise Integration, and Pipeline Workload Testing.

## Feature Inventory & Test Mapping
| # | Feature | Source | Tier 1 (Unit/Feature) | Tier 2 (Boundary/Edge) | Tier 3 (Cross-Feature) | Tier 4 (Scenario) |
|---|---------|--------|:---------------------:|:----------------------:|:----------------------:|:-----------------:|
| 1 | Directory Scaffolding | R1 | Verify folder creation | Existing vs clean folders | Scaffolding + history load | Scaffolding -> Pipeline run |
| 2 | Dependencies & Imports | R1 | Import 5 core modules | Missing dependency handling | Dependency version pinning | Scaffolding -> All imports |
| 3 | Channel Sync | R2 | Extract flat titles | Invalid / empty channel URL | Sync + History save | Full channel audit |
| 4 | Video Hunter & Dedupe | R2 | Search ytsearch15 | >90s filter, uploaded ID filter | Hunter -> History update | Hunt -> Download 3 videos |
| 5 | AI Script Generation | R3 | Generate script JSON | Missing/invalid GEMINI_API_KEY | Brain -> Cloud file delete | Video upload -> Script gen |
| 6 | Voiceover Synthesis | R3 | Edge-tts voice generation | Empty text / long text | Script -> Voiceover.mp3 | Script gen -> Voice synthesis |
| 7 | Video Editing & Crop | R4 | ColorClip to 1080x1920 | Mute, flip 50%, colorx 1.04 | Audio sync + MoviePy render | Voiceover -> Edit -> MP4 export |
| 8 | Win32 Handle Cleanup | R4 | Input clip removal | File lock release with gc.collect | Edit -> input_videos/ clean | End-to-end clip garbage collect |
| 9 | TikTok Browser Context | R5 | Chromium launch options | Headless vs headed modes | Profile persistence | Context launch -> Close |
| 10 | TikTok Studio Upload | R5 | File input locator | 90s login wait timeout | Video render -> Upload file | End-to-end publish flow |
| 11 | Central CLI Pipeline | R6 | Run main with args | Missing keyword interactive prompt | Hunter -> Brain -> Editor -> Uploader | Full interactive CLI execution |
| 12 | Test Pipeline Suite | R7 | test_pipeline.py exec | All 4 assertions pass | Test suite self-execution | CI / automated gate check |

## Test Architecture
- Test Runner: `python test_pipeline.py` and modular tests.
- Pass/Fail semantics: Exit code 0, standard assertions pass.
- Synthetic Media Strategy: Uses MoviePy ColorClip to generate deterministic 3-second clips with different aspect ratios (16:9, 4:3, 1:1) in < 1 second.
