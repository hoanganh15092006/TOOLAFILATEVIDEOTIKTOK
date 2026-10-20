"""
ai_brain.py - Gemini 2.5 Flash Script Generation & Edge-TTS Voice Synthesis
===========================================================================
Part of: Automated TikTok Affiliate Video Creation & Upload Pipeline
Milestone: M3 (Requirement R3)

Responsibilities:
1. Video analysis and structured JSON affiliate script generation via Google Gemini 2.5 Flash.
2. Cloud file quota management (immediate deletion in finally block).
3. Vietnamese voiceover synthesis via Microsoft edge-tts (voice vi-VN-HoaiMyNeural, rate +10%).
"""

import os
import re
import time
import json
import asyncio
import concurrent.futures
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
import edge_tts

# Load environment variables on module import
load_dotenv()

# System prompt directing Gemini to generate viral TikTok Affiliate scripts
SCRIPT_STYLE_GUIDES = {
    "trend": "Ngôn ngữ: Tiếng Việt tự nhiên, trẻ trung, nhịp điệu nhanh, lôi cuốn, bắt trend Gen Z hài hước.",
    "drama": "Phong cách: Kịch tính, vạch trần sự thật ('Đừng vội mua nếu chưa xem clip này...', 'Liệu sản phẩm này có thần thánh như lời đồn?').",
    "fomo": "Phong cách: Flash sale giục giã, cấp bách, tạo cảm giác khan hiếm ('Chỉ còn đúng vài suất giá hời hôm nay...', 'Chậm tay là tiếc hùi hụi').",
    "review": "Phong cách: Trải nghiệm thực tế, chân thật, tin cậy từ góc nhìn người dùng ('Sau thời gian trải nghiệm thì đây là cảm nhận thật nhất của mình...').",
}


def get_script_prompt(style: str = "trend") -> str:
    """Returns specialized prompt template according to requested script style."""
    style_guide = SCRIPT_STYLE_GUIDES.get(str(style).lower(), SCRIPT_STYLE_GUIDES["trend"])
    return (
        "Bạn là một chuyên gia sáng tạo nội dung video TikTok Affiliate hàng đầu tại Việt Nam.\n"
        "Hãy phân tích kỹ video được cung cấp và thực hiện các yêu cầu sau:\n\n"
        "1. Xác định chính xác tên sản phẩm được review / xuất hiện trong video (`product_name`).\n"
        "2. Viết một kịch bản lời bình (voiceover) tiếp thị liên kết (affiliate script) cực kỳ cuốn hút (`voiceover`):\n"
        f"   - {style_guide}\n"
        "   - Độ dài: BẮT BUỘC trong khoảng từ 75 đến 90 từ tiếng Việt (để khi đọc với tốc độ +10% đạt thời lượng dưới 30 giây).\n"
        "   - 3 giây đầu: Câu Hook giật gân, đánh trúng nỗi đau, sự tò mò hoặc kết quả bất ngờ để giữ chân người xem.\n"
        "   - Phần giữa: Nêu bật tính năng nổi bật, công dụng thực tế và lợi ích của sản phẩm được minh họa trong video.\n"
        "   - Phần kết: Kêu gọi hành động (Call To Action - CTA) dứt khoát: hướng dẫn người xem bấm ngay vào GIỎ HÀNG GÓC TRÁI BÊN DƯỚI màn hình để mua với giá ưu đãi.\n"
        "   - QUY TẮC TUYỆT ĐỐI (STRICT NEGATIVE CONSTRAINTS):\n"
        "     + TUYỆT ĐỐI KHÔNG có bất kỳ ghi chú đạo diễn nào (ví dụ: [nhạc nền], (cười), [Cảnh 1], Hook:, CTA:...). \n"
        "     + TUYỆT ĐỐI KHÔNG chứa bất kỳ ký tự nào trong dấu ngoặc đơn () hoặc ngoặc vuông [].\n"
        "     + Nội dung `voiceover` CHỈ chứa DUY NHẤT các câu từ mà người đọc sẽ phát âm ra tiếng.\n"
        "3. Viết caption đăng TikTok ngắn gọn, hấp dẫn kèm ĐÚNG 5 hashtag thịnh hành liên quan đến sản phẩm và TikTok Shop (`caption`).\n\n"
        "Trả về kết quả dưới định dạng JSON tuân thủ đúng schema quy định."
    )


PROMPT_TEMPLATE = get_script_prompt("trend")


class VideoScriptResponse(BaseModel):
    """Structured response schema for Gemini video analysis and script generation."""
    product_name: str = Field(
        description="Tên sản phẩm chính được review hoặc xuất hiện trong video"
    )
    voiceover: str = Field(
        description="Kịch bản lời bình tiếp thị liên kết bằng tiếng Việt, 75-90 từ, hook 3s, CTA bấm giỏ hàng góc trái bên dưới, không ghi chú đạo diễn hay dấu ngoặc"
    )
    caption: str = Field(
        description="Caption mô tả đăng video TikTok bằng tiếng Việt kèm đúng 5 hashtag thịnh hành"
    )


def sanitize_voiceover(text: str) -> str:
    """
    Sanitizes voiceover text to ensure it contains only spoken words.
    Iteratively removes nested/mixed bracketed cues, parentheses notes,
    markdown formatting, and redundant whitespace.
    """
    if not text:
        return ""
    cleaned = text
    prev = None
    while prev != cleaned:
        prev = cleaned
        cleaned = re.sub(r"\[[^\[\]]*\]|\([^\(\)]*\)|\{[^\{\}]*\}", "", cleaned)
    # Remove any stray unclosed or mismatched bracket characters
    cleaned = re.sub(r"[\(\)\[\]\{\}]", "", cleaned)
    # Strip markdown symbols like *, _, #, `
    cleaned = re.sub(r"[*_#`]", "", cleaned)
    # Clean up spacing before punctuation marks
    cleaned = re.sub(r"\s+([,.!?:;])", r"\1", cleaned)
    # Collapse multiple whitespaces and trim
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def create_genai_client(api_key: str | None = None) -> genai.Client:
    """
    Initializes and returns a google-genai Client.
    Resolves api_key from argument or GEMINI_API_KEY environment variable.
    Raises ValueError if API key is unset, empty, or contains default placeholder.
    """
    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or not str(api_key).strip() or str(api_key).strip() == "your_key_here":
        raise ValueError("GEMINI_API_KEY is not set or invalid")

    return genai.Client(api_key=str(api_key).strip())


def generate_script(
    video_path: str,
    api_key: str | None = None,
    style: str = "trend",
) -> dict:
    """
    Uploads video_path to Gemini, polls until ACTIVE, requests Gemini model with
    structured JSON output, deletes the uploaded file in a finally block to conserve quota,
    and returns {'product_name': ..., 'voiceover': ..., 'caption': ...}.

    Args:
        video_path: Path to the review video MP4 file to analyze.
        api_key: Optional Gemini API key. Defaults to GEMINI_API_KEY environment variable.
        style: Script style ("trend", "drama", "fomo", "review"). Defaults to "trend".

    Returns:
        dict: Containing 'product_name', 'voiceover', and 'caption'.
    """
    # 1. Resolve and validate API key first
    client = create_genai_client(api_key=api_key)

    # 2. Validate video file existence
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at: {video_path}")

    uploaded_file = None
    try:
        # 3. Upload only the video file
        uploaded_file = client.files.upload(file=video_path)

        # 4. Poll until file state is ACTIVE (or timeout after 120s)
        start_time = time.time()
        poll_interval = 3
        timeout_seconds = 120

        while True:
            state = getattr(uploaded_file, "state", None)
            if state == types.FileState.ACTIVE or state == "ACTIVE" or str(state).endswith("ACTIVE"):
                break
            elif state == types.FileState.FAILED or state == "FAILED" or str(state).endswith("FAILED"):
                err_msg = getattr(uploaded_file, "error", "Unknown processing error")
                raise RuntimeError(f"Video processing failed on Gemini server: {err_msg}")

            if time.time() - start_time > timeout_seconds:
                raise TimeoutError(
                    f"Video processing timed out after {timeout_seconds}s for {video_path}"
                )

            time.sleep(poll_interval)
            uploaded_file = client.files.get(name=uploaded_file.name)

        # 5. Invoke Gemini with structured JSON configuration
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=VideoScriptResponse,
            temperature=0.7,
        )

        candidate_models = [
            os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            "gemini-3.5-flash",
            "gemini-flash-latest",
        ]
        # Deduplicate while preserving order
        candidate_models = list(dict.fromkeys(candidate_models))

        prompt_text = get_script_prompt(style)
        response = None
        last_error = None
        for m_name in candidate_models:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=m_name,
                        contents=[uploaded_file, prompt_text],
                        config=config,
                    )
                    break
                except Exception as gen_err:
                    last_error = gen_err
                    time.sleep(2)
            if response is not None:
                break

        if response is None:
            raise RuntimeError(f"All Gemini models failed: {last_error}") from last_error

        # 6. Parse structured response
        data = None
        if hasattr(response, "parsed") and response.parsed is not None:
            if isinstance(response.parsed, BaseModel):
                data = response.parsed.model_dump()
            elif isinstance(response.parsed, dict):
                data = response.parsed

        if data is None:
            if hasattr(response, "text") and response.text:
                data = json.loads(response.text)
            else:
                raise RuntimeError("Gemini 2.5 Flash returned an empty response")

        # Sanitize and ensure expected keys
        product_name = str(data.get("product_name", "")).strip()
        voiceover = sanitize_voiceover(str(data.get("voiceover", "")))
        caption = str(data.get("caption", "")).strip()

        return {
            "product_name": product_name,
            "voiceover": voiceover,
            "caption": caption,
        }

    finally:
        # 7. Guaranteed cloud quota cleanup
        if uploaded_file and hasattr(uploaded_file, "name") and uploaded_file.name:
            try:
                client.files.delete(name=uploaded_file.name)
            except Exception:
                pass


# Alias for compatibility with survey specifications
generate_script_and_caption = generate_script


async def _save_edge_tts(text: str, output_path: str, voice: str, rate: str) -> None:
    """Internal helper executing edge_tts async save."""
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(output_path)


def generate_voice(
    text: str,
    output_audio: str = "voiceover.mp3",
    voice: str = "vi-VN-HoaiMyNeural",
    rate: str = "+10%",
) -> str:
    """
    Synthesizes Vietnamese speech using edge-tts (voice vi-VN-HoaiMyNeural, rate +10%)
    and saves to output_audio synchronously.

    Args:
        text: Vietnamese script text to speak.
        output_audio: Path to output MP3 file (default: 'voiceover.mp3').
        voice: edge-tts voice identifier (default: 'vi-VN-HoaiMyNeural').
        rate: Speech tempo adjustment (default: '+10%').

    Returns:
        str: Path to the generated output audio file.

    Raises:
        ValueError: If text is empty or whitespace only.
        RuntimeError: If speech synthesis fails or file is not created.
    """
    # Normalize voice aliases
    if voice:
        v_low = voice.lower().strip()
        if v_low in ["female", "nu", "nữ"]:
            voice = "vi-VN-HoaiMyNeural"
        elif v_low in ["male", "nam"]:
            voice = "vi-VN-NamMinhNeural"

    clean_text = text.strip() if text else ""
    if not clean_text:
        raise ValueError("Text for voice generation cannot be empty or whitespace only.")

    output_dir = os.path.dirname(os.path.abspath(output_audio))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    def _execute_synthesis():
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(asyncio.run, _save_edge_tts(clean_text, output_audio, voice, rate)).result()
        else:
            asyncio.run(_save_edge_tts(clean_text, output_audio, voice, rate))

    # Retry mechanism for transient network resilience against Microsoft TTS servers
    max_retries = 3
    last_error = None
    for attempt in range(max_retries):
        try:
            _execute_synthesis()
            if os.path.exists(output_audio) and os.path.getsize(output_audio) > 0:
                return output_audio
            raise RuntimeError(f"Voice generation failed: '{output_audio}' was not created or is empty.")
        except Exception as err:
            last_error = err
            if attempt < max_retries - 1:
                time.sleep(1.0 * (attempt + 1))
            else:
                raise RuntimeError(
                    f"Failed to generate voice after {max_retries} attempts: {last_error}"
                ) from last_error

    return output_audio


# =============================================================================
# Auto-Pilot: Trending Affiliate Product Discovery Module
# =============================================================================

NICHE_DEFINITIONS = {
    "home": ("Đồ gia dụng thông minh & Tiện ích đời sống", ["gia dụng", "tiện ích", "nhà cửa", "bếp", "hút bụi", "nồi", "quạt"]),
    "tech": ("Công nghệ, Điện thoại & Máy tính", ["công nghệ", "điện thoại", "tai nghe", "sạc", "bàn phím", "smartwatch", "tripod"]),
    "beauty": ("Mỹ phẩm, Làm đẹp & Chăm sóc sức khỏe", ["chăm sóc", "mỹ phẩm", "làm đẹp", "sức khỏe", "tăm nước", "cạo râu", "sấy tóc", "massage"]),
    "decor": ("Decor phòng, Bàn làm việc & Nhà cửa", ["decor", "đèn", "phun sương", "tinh dầu", "hoàng hôn"]),
    "fashion": ("Thời trang, Túi xách & Phụ kiện", ["thời trang", "quần", "áo", "túi", "dép", "phụ kiện"]),
}

CURATED_TRENDING_PRODUCTS: list[dict[str, str]] = [
    {"name": "Bình giữ nhiệt hiển thị nhiệt độ", "keyword": "bình giữ nhiệt hiển thị nhiệt độ review", "category": "Gia dụng thông minh"},
    {"name": "Quạt tích điện mini để bàn", "keyword": "quạt tích điện mini cầm tay review", "category": "Điện tử tiện ích"},
    {"name": "Nồi cơm điện mini đa năng", "keyword": "nồi cơm điện mini đa năng review", "category": "Gia dụng thông minh"},
    {"name": "Máy hút bụi giường nệm diệt khuẩn UV", "keyword": "máy hút bụi giường nệm diệt khuẩn uv review", "category": "Đời sống"},
    {"name": "Bàn phím cơ không dây bluetooth", "keyword": "bàn phím cơ không dây giá rẻ review", "category": "Công nghệ"},
    {"name": "Máy tăm nước cầm tay du lịch", "keyword": "máy tăm nước cầm tay du lịch review", "category": "Chăm sóc cá nhân"},
    {"name": "Củ sạc nhanh 65W GaN đa năng", "keyword": "củ sạc nhanh 65w gan đa năng review", "category": "Phụ kiện điện thoại"},
    {"name": "Máy ép chậm mini cầm tay", "keyword": "máy ép chậm mini hoa quả review", "category": "Gia dụng thông minh"},
    {"name": "Gậy chụp ảnh selfie 3 chân tripod", "keyword": "gậy chụp ảnh selfie tripod bluetooth review", "category": "Phụ kiện điện thoại"},
    {"name": "Máy xay sinh tố cầm tay mini", "keyword": "máy xay sinh tố cầm tay mini review", "category": "Gia dụng thông minh"},
    {"name": "Gối công thái học memory foam", "keyword": "gối công thái học chống đau cổ vai gáy review", "category": "Sức khỏe"},
    {"name": "Đèn led hoàng hôn decor phòng", "keyword": "đèn led hoàng hôn decor phòng review", "category": "Decor nhà cửa"},
    {"name": "Máy massage cổ vai gáy xung điện", "keyword": "máy massage cổ vai gáy xung điện review", "category": "Sức khỏe"},
    {"name": "Giá đỡ điện thoại xoay 360 độ", "keyword": "giá đỡ điện thoại xoay 360 kim loại review", "category": "Phụ kiện điện thoại"},
    {"name": "Nồi lẩu nướng mini 2 ngăn", "keyword": "nồi lẩu nướng 2 ngăn mini đa năng review", "category": "Gia dụng thông minh"},
    {"name": "Kệ để giày dép thông minh gấp gọn", "keyword": "kệ để giày dép gấp gọn thông minh review", "category": "Gia dụng tiện ích"},
    {"name": "Đèn học để bàn chống cận tích điện", "keyword": "đèn bàn học chống cận led thông minh review", "category": "Đời sống"},
    {"name": "Máy khuếch tán tinh dầu phun sương", "keyword": "máy khuếch tán tinh dầu phun sương decor review", "category": "Decor nhà cửa"},
    {"name": "Tai nghe bluetooth chụp tai chống ồn", "keyword": "tai nghe bluetooth chụp tai anc review", "category": "Công nghệ"},
    {"name": "Bình xịt bọt tuyết tẩy dầu mỡ nhà bếp", "keyword": "bình xịt tẩy dầu mỡ nhà bếp siêu sạch review", "category": "Vệ sinh nhà cửa"},
    {"name": "Máy sấy tóc ion âm tốc độ cao", "keyword": "máy sấy tóc ion âm tốc độ cao review", "category": "Chăm sóc cá nhân"},
    {"name": "Đồng hồ thông minh smartwatch pin trâu", "keyword": "smartwatch giá rẻ pin trâu review", "category": "Công nghệ"},
    {"name": "Bộ tua vít đa năng bỏ túi", "keyword": "bộ tua vít đa năng bỏ túi review", "category": "Dụng cụ tiện ích"},
    {"name": "Thảm đá lau chân diatomite thấm hút", "keyword": "thảm đá lau chân diatomite thấm nước review", "category": "Gia dụng tiện ích"},
    {"name": "Máy cạo râu mini du lịch bỏ túi", "keyword": "máy cạo râu mini du lịch review", "category": "Chăm sóc cá nhân"},
    {"name": "Hộp cơm cắm điện hâm nóng văn phòng", "keyword": "hộp cơm cắm điện hâm nóng văn phòng review", "category": "Gia dụng tiện ích"},
    {"name": "Đèn ngủ cảm ứng chuyển động thông minh", "keyword": "đèn ngủ cảm ứng thông minh review", "category": "Gia dụng thông minh"},
]


def discover_trending_products(
    api_key: str | None = None,
    exclude_keywords: list[str] | None = None,
    count: int = 5,
    niche: str | None = None,
) -> list[dict[str, str]]:
    """
    Discovers high-converting trending affiliate products on TikTok Shop Vietnam.
    Attempts Gemini AI dynamic generation first, falling back smoothly to curated seeds.

    Args:
        api_key: Optional Gemini API key.
        exclude_keywords: List of keywords/product names to exclude to avoid repeats.
        count: Number of candidate products to return.
        niche: Optional niche category ('home', 'tech', 'beauty', 'decor', 'fashion').

    Returns:
        list of dicts with 'name', 'keyword', and 'category'.
    """
    import random

    excluded_lower = {k.strip().lower() for k in (exclude_keywords or []) if k}

    niche_clean = str(niche).lower().strip() if niche else None
    niche_info = NICHE_DEFINITIONS.get(niche_clean)
    niche_prompt = f"Tập trung ĐẶC BIỆT vào ngành hàng: {niche_info[0]}.\n" if niche_info else ""

    # Attempt dynamic discovery via Gemini AI
    try:
        client = create_genai_client(api_key=api_key)
        prompt = (
            f"Bạn là chuyên gia săn sản phẩm TikTok Shop Affiliate Marketing tại Việt Nam.\n"
            f"Hãy gợi ý {count} sản phẩm đang thịnh hành (trending), dễ bán, hoa hồng tốt và nhiều video review ngắn nhất trên TikTok Shop hiện nay.\n"
            f"{niche_prompt}"
            f"Yêu cầu:\n"
            f"- Cung cấp 'name' (tên sản phẩm rõ ràng), 'keyword' (từ khóa 3-6 từ tiếng Việt kèm chữ 'review' để tìm clip trên YouTube/TikTok), 'category' (ngành hàng).\n"
            f"- TUYỆT ĐỐI KHÔNG trùng với các từ khóa sau: {list(excluded_lower)[:20]}.\n"
            f"Trả về kết quả duy nhất ở định dạng JSON dạng danh sách các object [{{'name': '...', 'keyword': '...', 'category': '...'}}]."
        )

        model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        resp = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.8,
            ),
        )

        if resp and resp.text:
            cleaned = resp.text.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
                cleaned = re.sub(r"\n?```$", "", cleaned).strip()
            parsed = json.loads(cleaned)
            if isinstance(parsed, list) and len(parsed) > 0:
                results = []
                for item in parsed:
                    if isinstance(item, dict) and item.get("keyword"):
                        kw = item.get("keyword", "").strip()
                        if kw.lower() not in excluded_lower:
                            results.append({
                                "name": item.get("name", kw),
                                "keyword": kw,
                                "category": item.get("category", "Trending"),
                            })
                if results:
                    return results[:count]
    except Exception:
        pass

    # Seamless fallback to curated seeds with niche filtering
    pool = [p for p in CURATED_TRENDING_PRODUCTS if p["keyword"].lower() not in excluded_lower]
    if niche_info:
        niche_matches = []
        for p in pool:
            p_cat = (p.get("category", "") + " " + p.get("name", "")).lower()
            if any(term in p_cat for term in niche_info[1]):
                niche_matches.append(p)
        if niche_matches:
            pool = niche_matches

    if not pool:
        pool = list(CURATED_TRENDING_PRODUCTS)

    random.shuffle(pool)
    return pool[:max(1, count)]

