"""
Video Generator & Layout Engine:
Renders 1080x1920 (9:16 vertical) high-contrast recruitment videos
matching the FreeJobAlert reference shorts layout with 5 rotating color palettes,
subtle animation, and dynamic audio integration.
"""

import os
import math
import json
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import imageio_ffmpeg
from moviepy import VideoClip

# Palette Definitions per specification
PALETTES = [
    {
        "id": "palette_1_red_navy",
        "name": "Red & Navy (Classic Alert)",
        "header_bg": "#0B3C5D",
        "header_text": "#FFFFFF",
        "title_color": "#D32F2F",
        "banner_vac_bg": "#FFEB3B",
        "banner_vac_text": "#0B3C5D",
        "chips_bg": "#0B3C5D",
        "chips_text": "#FFFFFF",
        "table_label_color": "#D32F2F",
        "table_text_color": "#111111",
        "table_border": "#CBD5E1",
        "cta_bg": "#FFEB3B",
        "cta_text": "#B71C1C",
        "progress_color": "#D32F2F",
        "bg_color": "#FFFFFF",
    },
    {
        "id": "palette_2_green_maroon",
        "name": "Green & Maroon (Forest Alert)",
        "header_bg": "#1B5E20",
        "header_text": "#FFFFFF",
        "title_color": "#B71C1C",
        "banner_vac_bg": "#FFEB3B",
        "banner_vac_text": "#1B5E20",
        "chips_bg": "#1B5E20",
        "chips_text": "#FFFFFF",
        "table_label_color": "#1B5E20",
        "table_text_color": "#111111",
        "table_border": "#C8E6C9",
        "cta_bg": "#FFEB3B",
        "cta_text": "#1B5E20",
        "progress_color": "#1B5E20",
        "bg_color": "#FFFFFF",
    },
    {
        "id": "palette_3_royal_blue_orange",
        "name": "Royal Blue & Orange (High Contrast)",
        "header_bg": "#1565C0",
        "header_text": "#FFFFFF",
        "title_color": "#E64A19",
        "banner_vac_bg": "#FFF3E0",
        "banner_vac_text": "#BF360C",
        "chips_bg": "#1565C0",
        "chips_text": "#FFFFFF",
        "table_label_color": "#E64A19",
        "table_text_color": "#111111",
        "table_border": "#BBDEFB",
        "cta_bg": "#FFE082",
        "cta_text": "#BF360C",
        "progress_color": "#E64A19",
        "bg_color": "#FFFFFF",
    },
    {
        "id": "palette_4_teal_purple",
        "name": "Teal & Purple (Modern Alert)",
        "header_bg": "#00796B",
        "header_text": "#FFFFFF",
        "title_color": "#6A1B9A",
        "banner_vac_bg": "#FFECB3",
        "banner_vac_text": "#4A148C",
        "chips_bg": "#6A1B9A",
        "chips_text": "#FFFFFF",
        "table_label_color": "#00796B",
        "table_text_color": "#111111",
        "table_border": "#B2DFDB",
        "cta_bg": "#FFC107",
        "cta_text": "#4A148C",
        "progress_color": "#00796B",
        "bg_color": "#FFFFFF",
    },
    {
        "id": "palette_5_crimson_slate",
        "name": "Crimson & Slate (Authority Alert)",
        "header_bg": "#263238",
        "header_text": "#FFFFFF",
        "title_color": "#C2185B",
        "banner_vac_bg": "#E0F7FA",
        "banner_vac_text": "#006064",
        "chips_bg": "#263238",
        "chips_text": "#FFFFFF",
        "table_label_color": "#C2185B",
        "table_text_color": "#111111",
        "table_border": "#CFD8DC",
        "cta_bg": "#FFEB3B",
        "cta_text": "#C2185B",
        "progress_color": "#00BCD4",
        "bg_color": "#FFFFFF",
    },
]

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
EMBLEMS_DIR = os.path.join(ASSETS_DIR, "emblems")
PHOTOS_DIR = os.path.join(ASSETS_DIR, "stock_photos")
BRANDING_DIR = os.path.join(ASSETS_DIR, "branding")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)


FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Loads bundled or system fonts with graceful cross-platform fallback."""
    bundled_bold = os.path.join(FONTS_DIR, "arialbd.ttf")
    bundled_reg = os.path.join(FONTS_DIR, "arial.ttf")

    font_candidates = (
        [bundled_bold, "C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/segoeuib.ttf"]
        if bold
        else [bundled_reg, "C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/segoeui.ttf"]
    )
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    """Wraps text so it fits within max_width pixels."""
    words = text.split()
    if not words:
        return [""]
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def find_emblem_image(exam_data: Dict[str, Any]) -> str:
    """Finds best matching emblem or returns default."""
    org = (exam_data.get("org_short", "") + " " + exam_data.get("org_name", "")).lower()
    mapping = {
        "wbpsc": "wbpsc.png",
        "west bengal": "wbpsc.png",
        "tnmvmd": "tnmvmd.png",
        "tamil nadu": "tnmvmd.png",
        "nabfins": "nabfins.png",
        "itpo": "itpo.png",
    }
    for key, fn in mapping.items():
        if key in org:
            p = os.path.join(EMBLEMS_DIR, fn)
            if os.path.exists(p):
                return p
    default_p = os.path.join(EMBLEMS_DIR, "default_emblem.png")
    return default_p if os.path.exists(default_p) else ""


def find_stock_photo(exam_data: Dict[str, Any]) -> str:
    """Finds best matching profession scene photo."""
    tag = exam_data.get("profession_tag", "").lower()
    title = exam_data.get("title", "").lower()

    if "surveyor" in tag or "survey" in title:
        p = os.path.join(PHOTOS_DIR, "surveyor.jpg")
    elif "apprentice" in tag or "automobile" in tag or "motor" in title:
        p = os.path.join(PHOTOS_DIR, "automobile_technician.jpg")
    elif "cso" in tag or "banking" in tag or "officer" in tag:
        p = os.path.join(PHOTOS_DIR, "cso_field_officer.jpg")
    elif "steno" in tag or "assistant" in tag or "itpo" in title:
        p = os.path.join(PHOTOS_DIR, "office_assistant.jpg")
    elif "police" in tag or "constable" in tag or "ssc" in title or "defense" in tag:
        p = os.path.join(PHOTOS_DIR, "defense_police.jpg")
    elif "railway" in tag or "rrb" in tag or "station" in title or "ntpc" in title:
        p = os.path.join(PHOTOS_DIR, "railway_officer.jpg")
    else:
        p = os.path.join(PHOTOS_DIR, "default_job.jpg")

    return p if os.path.exists(p) else ""


def render_base_layout(
    exam_data: Dict[str, Any],
    palette: Dict[str, str],
    stock_zoom: float = 1.0,
    shine_offset: float = -1.0,
    progress: float = 0.0
) -> Image.Image:
    """
    Renders a single 1080x1920 frame matching the FreeJobAlert reference short.
    Includes split visual, bold titles, yellow banner, two-column specification table, and CTA.
    """
    canvas_w, canvas_h = 1080, 1920
    img = Image.new("RGB", (canvas_w, canvas_h), palette["bg_color"])
    draw = ImageDraw.Draw(img)

    # 1. TOP HEADER (0 to 135px)
    header_h = 135
    header_logo_path = os.path.join(BRANDING_DIR, "header_logo.png")
    if os.path.exists(header_logo_path):
        header_img = Image.open(header_logo_path).convert("RGBA")
        img.paste(header_img, (0, 0), header_img)
    else:
        draw.rectangle([0, 0, canvas_w, header_h], fill="#FFFFFF")
        font_h = get_font(60, bold=True)
        draw.text((canvas_w // 2, header_h // 2), "FreeJobAlert.com", fill=palette["header_bg"], font=font_h, anchor="mm")
        draw.line((0, header_h - 3, canvas_w, header_h - 3), fill=palette["header_bg"], width=4)

    # 2. SPLIT VISUAL SECTION (145 to 535px, Height = 390px)
    split_y = 145
    split_h = 390
    box_border_width = 3
    box_border_color = "#0B3C5D"

    # Left Box (Emblem) -> Width ~410px (x: 35 to 445)
    left_x1, left_y1, left_x2, left_y2 = 35, split_y, 445, split_y + split_h
    draw.rounded_rectangle([left_x1, left_y1, left_x2, left_y2], radius=16, fill="#FFFFFF", outline=box_border_color, width=box_border_width)

    emblem_path = find_emblem_image(exam_data)
    if emblem_path and os.path.exists(emblem_path):
        emb_img = Image.open(emblem_path).convert("RGBA")
        emb_target_w = (left_x2 - left_x1) - 20
        emb_target_h = split_h - 20
        emb_img.thumbnail((emb_target_w, emb_target_h), Image.Resampling.LANCZOS)
        offset_x = left_x1 + ((left_x2 - left_x1) - emb_img.width) // 2
        offset_y = left_y1 + (split_h - emb_img.height) // 2
        img.paste(emb_img, (offset_x, offset_y), emb_img)

    # Right Box (Stock Photo) -> Width ~595px (x: 455 to 1045)
    right_x1, right_y1, right_x2, right_y2 = 455, split_y, 1045, split_y + split_h
    stock_path = find_stock_photo(exam_data)
    if stock_path and os.path.exists(stock_path):
        stk_img = Image.open(stock_path).convert("RGB")
        target_w = right_x2 - right_x1
        target_h = split_h

        # Animated Ken Burns subtle crop & scale
        crop_w = int(stk_img.width / stock_zoom)
        crop_h = int(stk_img.height / stock_zoom)
        crop_x = (stk_img.width - crop_w) // 2
        crop_y = (stk_img.height - crop_h) // 2
        cropped = stk_img.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
        resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # Rounded mask for right box
        mask = Image.new("L", (target_w, target_h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, target_w, target_h], radius=16, fill=255)
        img.paste(resized, (right_x1, right_y1), mask)
        draw.rounded_rectangle([right_x1, right_y1, right_x2, right_y2], radius=16, outline=box_border_color, width=box_border_width)

    # 3. CALLOUT BANNER SECTION (545px to 775px)
    banner_y = 545

    # 3A: Recruitment Title Banner (545 to 615, H=70)
    recruitment_title = exam_data.get("title", "GOVERNMENT EXAM RECRUITMENT 2026")
    font_title = get_font(42, bold=True)
    # Check title width and scale font if necessary
    bbox_t = draw.textbbox((0, 0), recruitment_title, font=font_title)
    if (bbox_t[2] - bbox_t[0]) > 1000:
        font_title = get_font(35, bold=True)
    draw.rectangle([0, banner_y, canvas_w, banner_y + 70], fill="#FFFFFF")
    draw.text((canvas_w // 2, banner_y + 35), recruitment_title, fill=palette["title_color"], font=font_title, anchor="mm")

    # 3B: Extra-Large Vacancy Banner (615 to 715, H=100)
    vac_y = banner_y + 70
    vac_h = 100
    vac_text = exam_data.get("vacancy_callout", "MULTIPLE VACANCIES")
    draw.rectangle([0, vac_y, canvas_w, vac_y + vac_h], fill=palette["banner_vac_bg"])

    # Optional Animated Shine sweep across vacancy banner
    if 0.0 <= shine_offset <= 1.0:
        shine_x = int(shine_offset * (canvas_w + 300) - 150)
        shine_overlay = Image.new("RGBA", (140, vac_h), (255, 255, 255, 110))
        img.paste(Image.blend(Image.new("RGBA", (140, vac_h), (255, 255, 255, 0)), shine_overlay, 0.4), (shine_x, vac_y), shine_overlay)

    font_vac = get_font(62, bold=True)
    bbox_v = draw.textbbox((0, 0), vac_text, font=font_vac)
    if (bbox_v[2] - bbox_v[0]) > 1000:
        font_vac = get_font(52, bold=True)
    draw.text((canvas_w // 2, vac_y + vac_h // 2), vac_text, fill=palette["banner_vac_text"], font=font_vac, anchor="mm")

    # 3C: Eligibility & Chips Sub-Banner (715 to 770, H=55)
    chips_y = vac_y + vac_h
    chips_h = 55
    chips_text = exam_data.get("highlights", "10th / Diploma / Graduate | Apply Online")
    draw.rectangle([0, chips_y, canvas_w, chips_y + chips_h], fill=palette["chips_bg"])
    font_chips = get_font(34, bold=True)
    draw.text((canvas_w // 2, chips_y + chips_h // 2), chips_text, fill=palette["chips_text"], font=font_chips, anchor="mm")

    # 4. DETAILED SPECIFICATION TABLE (780px to 1740px)
    table_top = 780
    table_bottom = 1735
    table_left = 35
    table_right = 1045
    col_divider_x = 410

    # Draw outer table border
    draw.rectangle([table_left, table_top, table_right, table_bottom], outline="#78909C", width=3)
    draw.line((col_divider_x, table_top, col_divider_x, table_bottom), fill="#78909C", width=3)

    specs = exam_data.get("table", {})
    row_keys = list(specs.keys())
    num_rows = max(1, len(row_keys))
    row_height = (table_bottom - table_top) / num_rows

    font_label = get_font(33, bold=True)
    font_value = get_font(32, bold=False)

    for i, key in enumerate(row_keys):
        ry1 = int(table_top + i * row_height)
        ry2 = int(table_top + (i + 1) * row_height) if i < num_rows - 1 else table_bottom

        # Row separator line
        if i > 0:
            draw.line((table_left, ry1, table_right, ry1), fill="#B0BEC5", width=2)

        # Alternating subtle row tint for enhanced legibility
        if i % 2 == 1:
            draw.rectangle([table_left + 3, ry1 + 2, col_divider_x - 1, ry2 - 1], fill="#F8FAFC")
            draw.rectangle([col_divider_x + 3, ry1 + 2, table_right - 2, ry2 - 1], fill="#FAFAFA")

        # Left Column: Label in Palette Color
        label_text = key
        label_lines = wrap_text(label_text, font_label, col_divider_x - table_left - 25, draw)
        total_lbl_h = len(label_lines) * 38
        start_lbl_y = ry1 + (row_height - total_lbl_h) // 2
        for line_idx, line in enumerate(label_lines):
            draw.text(
                (table_left + 15, start_lbl_y + line_idx * 38),
                line,
                fill=palette["table_label_color"],
                font=font_label,
            )

        # Right Column: Value with bullet dot
        raw_val = str(specs[key])
        val_text = f"•  {raw_val}"
        val_lines = wrap_text(val_text, font_value, table_right - col_divider_x - 30, draw)
        total_val_h = len(val_lines) * 38
        start_val_y = ry1 + (row_height - total_val_h) // 2
        for line_idx, line in enumerate(val_lines):
            draw.text(
                (col_divider_x + 18, start_val_y + line_idx * 38),
                line,
                fill=palette["table_text_color"],
                font=font_value,
            )

    # 5. BOTTOM CTA BANNER (1745px to 1895px, H=150)
    cta_y = 1745
    cta_h = 150
    draw.rectangle([0, cta_y, canvas_w, cta_y + cta_h], fill=palette["cta_bg"])

    font_cta_main = get_font(42, bold=True)
    font_cta_sub = get_font(34, bold=True)

    cta_main = "FOR COMPLETE DETAILS, VISIT FREEJOBALERT.COM"
    cta_sub = "CHECK DESCRIPTION FOR OFFICIAL NOTIFICATION & APPLY LINK"
    draw.text((canvas_w // 2, cta_y + 45), cta_main, fill=palette["cta_text"], font=font_cta_main, anchor="mm")
    draw.text((canvas_w // 2, cta_y + 105), cta_sub, fill="#0B3C5D", font=font_cta_sub, anchor="mm")

    # 6. DYNAMIC PROGRESS BAR (1908px to 1920px)
    progress_w = int(canvas_w * min(1.0, max(0.0, progress)))
    if progress_w > 0:
        draw.rectangle([0, 1908, progress_w, 1920], fill=palette["progress_color"])

    return img


def render_preview_poster(exam_data: Dict[str, Any], palette_idx: int = 0, output_filename: str = None) -> str:
    """Renders a single high-resolution still image poster for thumbnail/preview."""
    palette = PALETTES[palette_idx % len(PALETTES)]
    poster = render_base_layout(exam_data, palette, stock_zoom=1.03, progress=0.35)

    if not output_filename:
        output_filename = f"poster_{exam_data.get('id', 'exam')}_{palette['id']}.jpg"
    path = os.path.join(OUTPUT_DIR, output_filename)
    poster.save(path, quality=95)
    print(f"[Renderer] Saved preview poster -> {path}")
    return path


def render_exam_video(
    exam_data: Dict[str, Any],
    palette_idx: int = 0,
    duration_sec: float = 15.0,
    fps: int = 30,
    output_filename: str = None
) -> str:
    """
    Renders 1080x1920 9:16 vertical short-form MP4 video with subtle motion,
    shine effect on vacancy banner, animated progress bar, and 30fps timing.
    """
    palette = PALETTES[palette_idx % len(PALETTES)]
    if not output_filename:
        output_filename = f"short_{exam_data.get('id', 'exam')}_{palette['id']}.mp4"
    temp_video_path = os.path.join(OUTPUT_DIR, f"temp_{output_filename}")
    final_video_path = os.path.join(OUTPUT_DIR, output_filename)

    print(f"[Renderer] Generating video '{exam_data['title']}' using Palette '{palette['name']}' ({duration_sec}s @ {fps}fps)...")

    # Pre-render static base frame to optimize speed and cache components
    # We only re-calculate animated elements per frame
    def make_frame(t):
        progress = t / duration_sec

        # Smooth Ken Burns zoom (1.00 -> 1.06)
        stock_zoom = 1.0 + 0.06 * (math.sin(progress * math.pi))

        # Periodic shine cycle across the yellow vacancy banner every 5 seconds
        cycle_t = (t % 5.0) / 1.5  # shine lasts 1.5s
        shine_offset = cycle_t if cycle_t <= 1.0 else -1.0

        pil_frame = render_base_layout(
            exam_data=exam_data,
            palette=palette,
            stock_zoom=stock_zoom,
            shine_offset=shine_offset,
            progress=progress
        )
        return np.array(pil_frame)

    clip = VideoClip(make_frame, duration=duration_sec)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # Write video stream via moviepy using ffmpeg
    clip.write_videofile(
        temp_video_path,
        fps=fps,
        codec="libx264",
        preset="fast",
        ffmpeg_params=["-pix_fmt", "yuv420p"],
        threads=4,
        logger=None
    )
    clip.close()

    # Mix background audio at -18dB using audio_mixer
    from audio_mixer import mix_audio_into_video
    mix_audio_into_video(temp_video_path, final_video_path, target_db=-18.0)

    # Clean up temp mute video
    if os.path.exists(temp_video_path):
        try:
            os.remove(temp_video_path)
        except Exception:
            pass

    print(f"[Renderer] Finished short video: {final_video_path}")
    return final_video_path


if __name__ == "__main__":
    from scraper import load_mock_exams
    exams = load_mock_exams()
    if exams:
        print(f"Testing renderer with first exam: {exams[0]['title']}")
        poster = render_preview_poster(exams[0], palette_idx=0)
        video = render_exam_video(exams[0], palette_idx=0, duration_sec=5.0, fps=24)
        print("Test rendering complete!")
