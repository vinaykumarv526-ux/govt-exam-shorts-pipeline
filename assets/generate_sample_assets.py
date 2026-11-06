"""
Generates high-resolution emblems, stock illustrations, and branding assets
for government exam shorts rendering.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
EMBLEMS_DIR = os.path.join(ASSETS_DIR, "emblems")
PHOTOS_DIR = os.path.join(ASSETS_DIR, "stock_photos")
BRANDING_DIR = os.path.join(ASSETS_DIR, "branding")

os.makedirs(EMBLEMS_DIR, exist_ok=True)
os.makedirs(PHOTOS_DIR, exist_ok=True)
os.makedirs(BRANDING_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)


def get_font(size: int, bold: bool = True):
    bundled_bold = os.path.join(FONTS_DIR, "arialbd.ttf")
    bundled_reg = os.path.join(FONTS_DIR, "arial.ttf")

    font_names = (
        [bundled_bold, "C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "C:/Windows/Fonts/segoeuib.ttf"]
        if bold
        else [bundled_reg, "C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "C:/Windows/Fonts/segoeui.ttf"]
    )
    for fn in font_names:
        if os.path.exists(fn):
            try:
                return ImageFont.truetype(fn, size)
            except Exception:
                pass
    return ImageFont.load_default()


def create_wbpsc_emblem():
    """Generates a crisp West Bengal Public Service Commission circular golden emblem."""
    w, h = 420, 360
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Gold circular seal
    cx, cy = w // 2, h // 2
    r = 150
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#FFF8E1", outline="#D4AF37", width=6)
    draw.ellipse((cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14), fill="#FFE082", outline="#B8860B", width=3)

    # Upper text: GOVERNMENT OF WEST BENGAL
    font_small = get_font(15, bold=True)
    draw.text((cx, cy - 105), "GOVERNMENT OF WEST BENGAL", fill="#7B5E00", font=font_small, anchor="mm")

    # Emblem pillar / lions stylized
    draw.polygon([(cx - 24, cy + 30), (cx + 24, cy + 30), (cx + 34, cy + 42), (cx - 34, cy + 42)], fill="#A07800")
    draw.rectangle([cx - 28, cy - 40, cx + 28, cy + 28], fill="#C59B27", outline="#855E00", width=2)
    # Ashoka chakra ring in center
    draw.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), outline="#0B3C5D", width=3)
    for deg in range(0, 360, 45):
        rad = math.radians(deg)
        x2 = cx + int(16 * math.cos(rad))
        y2 = cy + int(16 * math.sin(rad))
        draw.line((cx, cy, x2, y2), fill="#0B3C5D", width=2)

    # Three lions crown top
    draw.ellipse((cx - 32, cy - 62, cx - 12, cy - 35), fill="#855E00")
    draw.ellipse((cx + 12, cy - 62, cx + 32, cy - 35), fill="#855E00")
    draw.ellipse((cx - 15, cy - 70, cx + 15, cy - 32), fill="#A07800")

    # Lower text: WBPSC
    font_bold = get_font(28, bold=True)
    draw.text((cx, cy + 85), "WBPSC", fill="#5A4000", font=font_bold, anchor="mm")
    font_sub = get_font(13, bold=True)
    draw.text((cx, cy + 115), "PUBLIC SERVICE COMMISSION", fill="#7B5E00", font=font_sub, anchor="mm")

    path = os.path.join(EMBLEMS_DIR, "wbpsc.png")
    img.save(path)
    return path


def create_tnmvmd_emblem():
    """Generates Tamil Nadu State Government Gopuram Temple emblem."""
    w, h = 420, 360
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    cx, cy = w // 2, h // 2
    r = 150
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#F1F8E9", outline="#2E7D32", width=6)
    draw.ellipse((cx - r + 12, cy - r + 12, cx + r - 12, cy + r - 12), fill="#E8F5E9", outline="#1B5E20", width=2)

    # Tamil Nadu arc text representation
    font_head = get_font(18, bold=True)
    draw.text((cx, cy - 108), "TAMIL NADU GOVT", fill="#1B5E20", font=font_head, anchor="mm")

    # Temple Gopuram Tower (Srivilliputhur Andal temple tower)
    steps = 6
    for i in range(steps):
        tw = 40 + i * 16
        th = 14
        ty = cy - 50 + i * 16
        draw.rectangle([cx - tw // 2, ty, cx + tw // 2, ty + th], fill="#E65100", outline="#BF360C", width=2)

    # Indian flag tricolor bar at base
    draw.rectangle([cx - 70, cy + 50, cx + 70, cy + 58], fill="#FF9933")
    draw.rectangle([cx - 70, cy + 58, cx + 70, cy + 66], fill="#FFFFFF")
    draw.rectangle([cx - 70, cy + 66, cx + 70, cy + 74], fill="#138808")

    # Ashoka chakra in base center
    draw.ellipse((cx - 8, cy + 54, cx + 8, cy + 70), outline="#000080", width=2)

    # Text at bottom
    font_bold = get_font(26, bold=True)
    draw.text((cx, cy + 100), "TNMVMD", fill="#1B5E20", font=font_bold, anchor="mm")

    path = os.path.join(EMBLEMS_DIR, "tnmvmd.png")
    img.save(path)
    return path


def create_nabfins_emblem():
    """Generates NABARD Financial Services Ltd emblem."""
    w, h = 420, 360
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    cx, cy = w // 2, h // 2 - 25
    # Distinctive dark red spiral symbol of NABFINS
    draw.ellipse((cx - 95, cy - 95, cx + 95, cy + 95), fill="#FFFFFF", outline="#7B1113", width=8)
    draw.ellipse((cx - 65, cy - 65, cx + 65, cy + 65), fill="#7B1113")
    draw.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), fill="#FFFFFF")
    draw.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill="#7B1113")

    # Triangle arrow pointing up-left
    draw.polygon([(cx - 75, cy - 40), (cx - 15, cy - 90), (cx - 30, cy - 30)], fill="#7B1113")

    # Typography: nabfins
    font_brand = get_font(44, bold=True)
    draw.text((cx, h - 60), "nabfins", fill="#7B1113", font=font_brand, anchor="mm")
    font_sub = get_font(13, bold=False)
    draw.text((cx, h - 25), "A Subsidiary of NABARD", fill="#555555", font=font_sub, anchor="mm")

    path = os.path.join(EMBLEMS_DIR, "nabfins.png")
    img.save(path)
    return path


def create_itpo_emblem():
    """Generates ITPO logo."""
    w, h = 420, 360
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    cx, cy = w // 2, h // 2 - 20
    # ITPO orange/red geometric logo
    draw.rectangle([cx - 100, cy - 70, cx + 100, cy + 40], outline="#E65100", width=6)
    draw.line((cx, cy - 70, cx, cy + 40), fill="#E65100", width=6)
    draw.ellipse((cx - 60, cy - 45, cx - 15, cy), fill="#E65100")
    draw.ellipse((cx + 15, cy - 45, cx + 60, cy), fill="#E65100")

    font_brand = get_font(48, bold=True)
    draw.text((cx, h - 65), "ITPO", fill="#E65100", font=font_brand, anchor="mm")
    font_sub = get_font(13, bold=False)
    draw.text((cx, h - 25), "PRAGATI MAIDAN, NEW DELHI", fill="#555555", font=font_sub, anchor="mm")

    path = os.path.join(EMBLEMS_DIR, "itpo.png")
    img.save(path)
    return path


def create_default_emblem():
    """Official Central Government Ashoka Stambh Seal fallback."""
    w, h = 420, 360
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    cx, cy = w // 2, h // 2
    r = 145
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#F8FAFC", outline="#0B3C5D", width=6)
    draw.ellipse((cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10), fill="#FFFFFF", outline="#0B3C5D", width=2)

    font_head = get_font(18, bold=True)
    draw.text((cx, cy - 105), "GOVERNMENT OF INDIA", fill="#0B3C5D", font=font_head, anchor="mm")

    # Emblem lions stylized silhouette
    draw.rectangle([cx - 36, cy - 50, cx + 36, cy + 20], fill="#0B3C5D")
    draw.ellipse((cx - 45, cy - 65, cx - 15, cy - 25), fill="#0B3C5D")
    draw.ellipse((cx + 15, cy - 65, cx + 45, cy - 25), fill="#0B3C5D")
    draw.ellipse((cx - 18, cy - 75, cx + 18, cy - 30), fill="#0B3C5D")

    # Base with Ashoka chakra
    draw.rectangle([cx - 55, cy + 20, cx + 55, cy + 40], fill="#D32F2F")
    draw.ellipse((cx - 16, cy + 45, cx + 16, cy + 77), outline="#0B3C5D", width=3)

    font_motto = get_font(18, bold=True)
    draw.text((cx, cy + 105), "सत्यमेव जयते", fill="#0B3C5D", font=font_motto, anchor="mm")

    path = os.path.join(EMBLEMS_DIR, "default_emblem.png")
    img.save(path)
    return path


def create_stock_photos():
    """Generates realistic professional scene illustrations matching the 4 jobs."""
    w, h = 630, 360

    # 1. Surveyor (wbpsc)
    img = Image.new("RGB", (w, h), (180, 210, 235))
    draw = ImageDraw.Draw(img)
    # Background: field/sky/construction
    draw.rectangle([0, h // 2, w, h], fill="#9E9D24")  # Greenish ground
    draw.polygon([(0, h // 2), (200, 120), (420, 160), (w, 100), (w, h // 2)], fill="#B0BEC5")  # Distant hills
    # Tripod + Total Station
    draw.line((190, h - 20, 240, 140), fill="#FDD835", width=8)
    draw.line((290, h - 20, 240, 140), fill="#FDD835", width=8)
    draw.line((240, h - 20, 240, 140), fill="#C0CA33", width=8)
    draw.rectangle([215, 95, 265, 145], fill="#E53935")  # Total station body
    draw.rectangle([230, 75, 250, 95], fill="#212121")  # Top handle
    draw.line((200, 120, 280, 120), fill="#212121", width=6)  # Telescope
    # Surveyor Person with Safety Vest & Hard Hat
    draw.ellipse((350, 60, 420, 130), fill="#FFB74D")  # Face
    draw.ellipse((340, 40, 430, 85), fill="#FDD835")   # Yellow Safety Helmet
    draw.polygon([(320, 130), (450, 130), (480, h), (300, h)], fill="#FDD835")  # High-vis vest
    draw.rectangle([340, 170, 430, 200], fill="#ECEFF1")  # Reflective stripe
    # Clip board in hand
    draw.rectangle([410, 180, 480, 270], fill="#8D6E63", outline="#3E2723", width=3)
    font = get_font(22, bold=True)
    draw.rectangle([10, h - 45, w - 10, h - 10], fill=(0, 0, 0, 180))
    draw.text((w // 2, h - 28), "SUB-SURVEYOR / CIVIL SITE SURVEY", fill="#FFFFFF", font=font, anchor="mm")
    img.save(os.path.join(PHOTOS_DIR, "surveyor.jpg"), quality=95)

    # 2. Automobile Technician (tnmvmd)
    img = Image.new("RGB", (w, h), (230, 235, 240))
    draw = ImageDraw.Draw(img)
    # Workshop bay
    draw.rectangle([0, 0, w, h], fill="#37474F")
    # Hydraulic lift pillars
    draw.rectangle([80, 30, 130, h], fill="#0277BD")
    draw.rectangle([w - 130, 30, w - 80, h], fill="#0277BD")
    # Bus/Vehicle engine bay chassis
    draw.rectangle([130, 70, w - 130, 240], fill="#E53935", outline="#B71C1C", width=4)
    draw.rectangle([160, 100, w - 160, 210], fill="#212121")  # Open engine bay
    # Mechanic figure in blue overalls
    draw.ellipse((280, 110, 340, 170), fill="#D7CCC8")
    draw.polygon([(260, 170), (360, 170), (370, h), (250, h)], fill="#1565C0")
    # Tools / Spanner in hand
    draw.line((350, 180, 410, 150), fill="#CFD8DC", width=8)
    draw.rectangle([10, h - 45, w - 10, h - 10], fill=(0, 0, 0, 180))
    draw.text((w // 2, h - 28), "AUTOMOBILE & DIPLOMA APPRENTICESHIP", fill="#FFFFFF", font=font, anchor="mm")
    img.save(os.path.join(PHOTOS_DIR, "automobile_technician.jpg"), quality=95)

    # 3. CSO Field Officer (nabfins)
    img = Image.new("RGB", (w, h), (245, 240, 230))
    draw = ImageDraw.Draw(img)
    # Rural outdoor banking / village home background
    draw.rectangle([0, h // 2 - 20, w, h], fill="#D7CCC8")  # Verandah floor
    draw.polygon([(50, 30), (250, 30), (300, 120), (0, 120)], fill="#8D6E63")  # Tile roof
    # Customer Service Officer with ID card and tablet
    draw.ellipse((160, 60, 230, 130), fill="#FFE0B2")
    draw.polygon([(140, 130), (250, 130), (270, h), (120, h)], fill="#FFFFFF", outline="#0B3C5D", width=2)
    # Blue ID Card Lanyard
    draw.line((180, 130, 195, 190), fill="#0D47A1", width=4)
    draw.line((210, 130, 195, 190), fill="#0D47A1", width=4)
    draw.rectangle([185, 190, 205, 220], fill="#F57C00")  # ID badge
    # Tablet in hands
    draw.rectangle([210, 180, 290, 240], fill="#212121", outline="#90CAF9", width=3)
    # Beneficiary customer in saree
    draw.ellipse((420, 80, 480, 140), fill="#D7CCC8")
    draw.polygon([(390, 140), (510, 140), (540, h), (360, h)], fill="#E91E63")  # Traditional dress
    draw.rectangle([10, h - 45, w - 10, h - 10], fill=(0, 0, 0, 180))
    draw.text((w // 2, h - 28), "FINANCIAL SERVICES & FIELD BANKING", fill="#FFFFFF", font=font, anchor="mm")
    img.save(os.path.join(PHOTOS_DIR, "cso_field_officer.jpg"), quality=95)

    # 4. Office Assistant / Steno (itpo)
    img = Image.new("RGB", (w, h), (235, 245, 250))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, h], fill="#ECEFF1")
    draw.rectangle([80, 140, 320, 300], fill="#37474F", outline="#263238", width=3)
    draw.rectangle([95, 155, 305, 285], fill="#0288D1")
    draw.rectangle([340, 150, 480, 290], fill="#37474F")
    draw.rectangle([350, 160, 470, 280], fill="#455A64")
    draw.ellipse((w - 150, 90, w - 80, 160), fill="#FFCCBC")
    draw.polygon([(w - 180, 160), (w - 50, 160), (w - 30, h), (w - 200, h)], fill="#2E7D32")
    draw.rectangle([10, h - 45, w - 10, h - 10], fill=(0, 0, 0, 180))
    draw.text((w // 2, h - 28), "GOVT OFFICE ADMINISTRATION & STENO", fill="#FFFFFF", font=font, anchor="mm")
    img.save(os.path.join(PHOTOS_DIR, "office_assistant.jpg"), quality=95)

    # 5. Defense / Police Constable (SSC GD)
    img = Image.new("RGB", (w, h), (210, 225, 215))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, h // 2, w, h], fill="#556B2F")
    draw.rectangle([0, 0, w, h // 2], fill="#87CEEB")
    draw.ellipse((w // 2 - 40, 60, w // 2 + 40, 140), fill="#DEB887")
    draw.ellipse((w // 2 - 45, 45, w // 2 + 45, 80), fill="#2F4F4F")
    draw.polygon([(w // 2 - 60, 140), (w // 2 + 60, 140), (w // 2 + 80, h), (w // 2 - 80, h)], fill="#4B5320")
    draw.rectangle([10, h - 45, w - 10, h - 10], fill=(0, 0, 0, 180))
    draw.text((w // 2, h - 28), "DEFENSE & CONSTABLE CADRE (GD)", fill="#FFFFFF", font=font, anchor="mm")
    img.save(os.path.join(PHOTOS_DIR, "defense_police.jpg"), quality=95)

    # 6. Railway Officer / NTPC Station Master
    img = Image.new("RGB", (w, h), (225, 230, 245))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, h], fill="#283593")
    draw.line((0, h - 80, w, h - 80), fill="#ECEFF1", width=12)
    draw.line((0, h - 30, w, h - 30), fill="#ECEFF1", width=12)
    draw.rectangle([60, 40, 340, 220], fill="#D32F2F", outline="#FFFFFF", width=4)
    draw.ellipse((w - 180, 80, w - 100, 160), fill="#FFD54F")
    draw.polygon([(w - 210, 160), (w - 70, 160), (w - 50, h), (w - 230, h)], fill="#FFFFFF", outline="#1A237E", width=2)
    draw.rectangle([10, h - 45, w - 10, h - 10], fill=(0, 0, 0, 180))
    draw.text((w // 2, h - 28), "INDIAN RAILWAYS NTPC / STATION MASTER", fill="#FFFFFF", font=font, anchor="mm")
    img.save(os.path.join(PHOTOS_DIR, "railway_officer.jpg"), quality=95)

    # Default fallback
    img.save(os.path.join(PHOTOS_DIR, "default_job.jpg"), quality=95)
    print("Generated all stock scene illustrations.")


def create_branding_header():
    """Generates the top header banner logo matching FreeJobAlert style."""
    w, h = 1080, 130
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Left back arrow circle (like mobile UI in reference)
    cx, cy = 60, h // 2
    draw.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), fill="#E8F0FE")
    # Left arrow line
    draw.line((cx + 10, cy, cx - 10, cy), fill="#1A73E8", width=4)
    draw.line((cx - 2, cy - 8, cx - 10, cy), fill="#1A73E8", width=4)
    draw.line((cx - 2, cy + 8, cx - 10, cy), fill="#1A73E8", width=4)

    # FreeJobAlert.com brand text
    font_bold = get_font(68, bold=True)
    # Free (Blue) + Job (Red) + Alert (Blue) + .com (Dark)
    # We can measure and draw nicely centered
    brand_x = 130
    draw.text((brand_x, cy - 6), "Free", fill="#0D47A1", font=font_bold, anchor="lm")
    # Measure width of 'Free'
    bbox_free = draw.textbbox((brand_x, cy - 6), "Free", font=font_bold, anchor="lm")
    x_job = bbox_free[2]
    draw.text((x_job, cy - 6), "Job", fill="#D32F2F", font=font_bold, anchor="lm")
    bbox_job = draw.textbbox((x_job, cy - 6), "Job", font=font_bold, anchor="lm")
    x_alert = bbox_job[2]
    draw.text((x_alert, cy - 6), "Alert", fill="#0D47A1", font=font_bold, anchor="lm")
    bbox_alert = draw.textbbox((x_alert, cy - 6), "Alert", font=font_bold, anchor="lm")
    x_com = bbox_alert[2]
    draw.text((x_com, cy - 6), ".com", fill="#212121", font=font_bold, anchor="lm")

    # Right search / dots icon placeholder
    rcx, rcy = w - 60, h // 2
    draw.ellipse((rcx - 4, rcy - 12, rcx + 4, rcy - 4), fill="#5F6368")
    draw.ellipse((rcx - 4, rcy - 4, rcx + 4, rcy + 4), fill="#5F6368")
    draw.ellipse((rcx - 4, rcy + 4, rcx + 4, rcy + 12), fill="#5F6368")

    # Bottom blue borderline
    draw.line((0, h - 3, w, h - 3), fill="#0B3C5D", width=4)

    path = os.path.join(BRANDING_DIR, "header_logo.png")
    img.save(path)
    print("Generated header logo.")
    return path


if __name__ == "__main__":
    create_wbpsc_emblem()
    create_tnmvmd_emblem()
    create_nabfins_emblem()
    create_itpo_emblem()
    create_default_emblem()
    create_stock_photos()
    create_branding_header()
    print("All visual assets successfully generated!")
