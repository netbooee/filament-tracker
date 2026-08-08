"""Generate the Filament Vault iOS/PWA icon set.

Run from repo root: python3 tools/make_icons.py
Writes icon-32/180/192/512.png into renderer/.
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

# Brand palette
INK       = (29, 33, 48)       # --ink
INK_DEEP  = (18, 21, 32)
INK_WARM  = (42, 48, 69)
TEAL      = (18, 166, 142)     # --teal-mid
TEAL_DEEP = (14, 124, 107)     # --teal
TEAL_HI   = (70, 210, 188)
WHITE     = (255, 255, 255)

OUT = Path(__file__).resolve().parent.parent / "renderer"
MASTER = 1024
SIZES = [32, 180, 192, 512]


def bg_gradient(size):
    """Diagonal ink gradient, darker top-left → slightly warmer bottom-right."""
    img = Image.new("RGB", (size, size), INK)
    d = ImageDraw.Draw(img)
    for y in range(size):
        t = y / (size - 1)
        c = tuple(int(INK_DEEP[i] + (INK_WARM[i] - INK_DEEP[i]) * t) for i in range(3))
        d.line([(0, y), (size, y)], fill=c)
    # Soft vignette
    vg = Image.new("L", (size, size), 0)
    vd = ImageDraw.Draw(vg)
    vd.ellipse([-size // 4, -size // 4, size + size // 4, size + size // 4], fill=255)
    vg = vg.filter(ImageFilter.GaussianBlur(radius=size // 6))
    dark = Image.new("RGB", (size, size), INK_DEEP)
    img = Image.composite(img, dark, vg)
    return img


def hex_points(cx, cy, radius, pointy_top=True):
    pts = []
    for i in range(6):
        # Pointy-top: angles at 90, 150, 210, 270, 330, 30
        angle_deg = -90 + i * 60 if pointy_top else -60 + i * 60
        a = math.radians(angle_deg)
        pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return pts


def draw_master():
    img = bg_gradient(MASTER)

    # Work on an RGBA layer so strokes antialias against the bg nicely
    layer = Image.new("RGBA", (MASTER, MASTER), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx, cy = MASTER // 2, MASTER // 2
    R = int(MASTER * 0.36)  # hex radius

    hex_pts = hex_points(cx, cy, R, pointy_top=True)
    top, tr, br, bot, bl, tl = hex_pts  # order from hex_points

    # --- Teal inner fill, very subtle ---
    d.polygon(hex_pts, fill=(14, 124, 107, 30))

    # --- Soft glow under the hex ---
    glow = Image.new("RGBA", (MASTER, MASTER), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.polygon(hex_pts, fill=(70, 210, 188, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=70))
    img.paste(glow, (0, 0), glow)

    # --- Drop shadow for the strokes ---
    shadow = Image.new("RGBA", (MASTER, MASTER), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    stroke = int(MASTER * 0.052)
    sd.line(hex_pts + [hex_pts[0]], fill=(0, 0, 0, 180), width=stroke, joint="curve")
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=18))
    img.paste(shadow, (0, 14), shadow)

    # --- The isometric cube lines (drawn on a fresh layer) ---
    cube = Image.new("RGBA", (MASTER, MASTER), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cube)

    # Internal Y: from center to top, bottom-right, bottom-left
    y_stroke = int(MASTER * 0.044)
    for target in (top, br, bl):
        cd.line([(cx, cy), target], fill=TEAL_HI + (255,), width=y_stroke, joint="curve")

    # Outer hex silhouette in crisp white
    cd.line(hex_pts + [hex_pts[0]], fill=WHITE + (255,), width=stroke, joint="curve")

    # Round the hex corners with filled circles at each vertex
    cap_r = stroke // 2
    for p in hex_pts:
        cd.ellipse([p[0] - cap_r, p[1] - cap_r, p[0] + cap_r, p[1] + cap_r], fill=WHITE)
    # Round the Y cap at center
    yc_r = y_stroke // 2
    cd.ellipse([cx - yc_r, cy - yc_r, cx + yc_r, cy + yc_r], fill=TEAL_HI)

    img.paste(cube, (0, 0), cube)

    # --- Tiny glint at top-right of the hex for pop ---
    glint = Image.new("RGBA", (MASTER, MASTER), (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(glint)
    gx, gy = tr
    gr = int(MASTER * 0.025)
    gd2.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(255, 255, 255, 160))
    glint = glint.filter(ImageFilter.GaussianBlur(radius=6))
    img.paste(glint, (0, 0), glint)

    # --- Center dot ---
    dot_r = int(MASTER * 0.018)
    d2 = ImageDraw.Draw(img)
    d2.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=WHITE)

    return img


def main():
    master = draw_master()
    for size in SIZES:
        out = master.resize((size, size), Image.LANCZOS)
        out.save(OUT / f"icon-{size}.png", "PNG", optimize=True)
        print(f"wrote {OUT / f'icon-{size}.png'} ({size}x{size})")


if __name__ == "__main__":
    main()
