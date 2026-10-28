# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# Generates companion Xcursor suite: sleek aerodynamic modern cursors.
# High-definition multi-resolution (24, 32, 48) Xcursor suite with smooth curves and palette glow.

import json
import math
import os
import shutil
import struct
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REPO_ROOT = Path(__file__).resolve().parents[2]
TOKENS = json.loads((REPO_ROOT / "palette" / "tokens.json").read_text())
TECH_NAME = TOKENS.get("meta", {}).get("tech_name", "MT-Theme-Starter")
DISPLAY_NAME = TOKENS.get("meta", {}).get("name", "MT Theme Starter")
OUT_DIR = REPO_ROOT / "src" / "cursors" / f"{TECH_NAME}-Cursors"


def hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple:
    # Convert #RRGGBB into RGBA tuple.
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return (r, g, b, alpha)


# Palette tokens from palette/tokens.json
COLOR_BODY = hex_to_rgba(TOKENS["color"]["bg"]["base"], 255)
COLOR_ACCENT = hex_to_rgba(TOKENS["color"]["accent"]["base"], 255)
COLOR_EMERALD = hex_to_rgba(TOKENS["color"]["accent"]["strong"], 255)
COLOR_CORAL = hex_to_rgba(TOKENS["color"]["status"]["destructive"], 255)
COLOR_SHADOW = (0, 0, 0, int(round(255 * float(TOKENS["color"].get("shadow_alpha", 0.55)))))

INDEX_THEME = f"""[Icon Theme]
Name={TECH_NAME}-Cursors
Comment=Sleek aerodynamic cursor suite for {DISPLAY_NAME}
Inherits=Adwaita
"""


def img_to_premultiplied_bgra(img: Image.Image) -> bytes:
    # Convert RGBA Pillow image to premultiplied BGRA bytes for Xcursor binary format
    arr = np.array(img.convert("RGBA"), dtype=np.float32)
    alpha = arr[..., 3:4] / 255.0
    arr[..., :3] *= alpha
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return arr[..., [2, 1, 0, 3]].tobytes()


def make_xcursor(frames_with_hotspots: list) -> bytes:
    # frames_with_hotspots: list of tuples (Image, xhot, yhot, delay_ms)
    magic = 0x72756358
    header_size = 16
    version = 0x00010000
    ntoc = len(frames_with_hotspots)

    header = struct.pack("<IIII", magic, header_size, version, ntoc)
    toc_entries = []
    image_chunks = []
    cur_offset = header_size + ntoc * 12

    for img, xhot, yhot, delay in frames_with_hotspots:
        w, h = img.size
        toc_entries.append(struct.pack("<III", 0xfffd0002, w, cur_offset))
        img_hdr = struct.pack("<IIIIIIIII", 36, 0xfffd0002, w, 1, w, h, xhot, yhot, delay)
        bgra = img_to_premultiplied_bgra(img)
        chunk = img_hdr + bgra
        image_chunks.append(chunk)
        cur_offset += len(chunk)

    return header + b"".join(toc_entries) + b"".join(image_chunks)


def draw_aerodynamic_pointer(target_size: int, show_accent_dot: bool = False) -> tuple:
    # Draw a sleek aerodynamic curved cursor (Bibata / macOS inspired) with 4x supersampling
    scale = 4
    canvas_size = target_size * scale
    im = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

    # Coordinates normalized to 128 canvas
    s = canvas_size / 128.0
    pts = [
        (16 * s, 16 * s),    # Tip
        (22 * s, 92 * s),    # Left barb
        (46 * s, 76 * s),    # Inner waist left
        (68 * s, 118 * s),   # Stem bottom left
        (82 * s, 110 * s),   # Stem bottom right
        (62 * s, 68 * s),    # Inner waist right
        (96 * s, 68 * s),    # Right barb
    ]

    # 1. Soft ambient drop shadow
    shadow = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    shadow_offset = 3 * s
    s_pts = [(x + shadow_offset, y + shadow_offset) for x, y in pts]
    sdraw.polygon(s_pts, fill=COLOR_SHADOW)
    shadow = shadow.filter(ImageFilter.GaussianBlur(5 * s))
    im = Image.alpha_composite(im, shadow)

    draw = ImageDraw.Draw(im)
    # 2. Outer glowing border
    draw.polygon(pts, fill=COLOR_BODY)
    draw.line(pts + [pts[0]], fill=COLOR_EMERALD, width=int(round(4 * s)), joint="curve")

    # 3. Inner contour accent
    inner_contour = [(pts[0][0] + 5*s, pts[0][1] + 8*s), (pts[1][0] + 4*s, pts[1][1] - 10*s), (pts[2][0] + 2*s, pts[2][1] - 8*s)]
    draw.line(inner_contour, fill=COLOR_ACCENT, width=int(round(2.5 * s)))

    if show_accent_dot:
        dot_center = (pts[2][0] + 10 * s, pts[2][1] + 12 * s)
        draw.ellipse([(dot_center[0] - 6*s, dot_center[1] - 6*s), (dot_center[0] + 6*s, dot_center[1] + 6*s)], fill=COLOR_ACCENT)
        draw.ellipse([(dot_center[0] - 3*s, dot_center[1] - 3*s), (dot_center[0] + 3*s, dot_center[1] + 3*s)], fill=COLOR_EMERALD)

    # Downsample with Lanczos anti-aliasing
    final_img = im.resize((target_size, target_size), Image.Resampling.LANCZOS)
    xhot = int(round(4 * (target_size / 32.0)))
    yhot = int(round(4 * (target_size / 32.0)))
    return final_img, xhot, yhot


def draw_pointer_hand(target_size: int) -> tuple:
    # Modern sleek pointer hand (index extended, organic curve)
    scale = 4
    canvas_size = target_size * scale
    s = canvas_size / 128.0
    im = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

    # Shadow
    shadow = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle([(32 * s, 18 * s), (96 * s, 114 * s)], radius=18*s, fill=COLOR_SHADOW)
    shadow = shadow.filter(ImageFilter.GaussianBlur(6 * s))
    im = Image.alpha_composite(im, shadow)

    draw = ImageDraw.Draw(im)
    # Palm and fingers
    draw.rounded_rectangle([(38 * s, 48 * s), (90 * s, 108 * s)], radius=14*s, fill=COLOR_BODY, outline=COLOR_EMERALD, width=int(round(3.5 * s)))
    # Index finger extended
    draw.rounded_rectangle([(38 * s, 16 * s), (58 * s, 72 * s)], radius=10*s, fill=COLOR_BODY, outline=COLOR_EMERALD, width=int(round(3.5 * s)))
    # Subtle inner accent line on index finger
    draw.line([(48 * s, 24 * s), (48 * s, 58 * s)], fill=COLOR_ACCENT, width=int(round(2.5 * s)))

    final_img = im.resize((target_size, target_size), Image.Resampling.LANCZOS)
    xhot = int(round(12 * (target_size / 32.0)))
    yhot = int(round(4 * (target_size / 32.0)))
    return final_img, xhot, yhot


def draw_ibeam_text(target_size: int) -> tuple:
    # High-visibility I-Beam with glowing tips
    scale = 4
    canvas_size = target_size * scale
    s = canvas_size / 128.0
    im = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

    draw = ImageDraw.Draw(im)
    cx, cy = 64 * s, 64 * s

    # Dropshadow
    shadow = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.line([(cx, cy - 42*s), (cx, cy + 42*s)], fill=COLOR_SHADOW, width=int(round(12 * s)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(4 * s))
    im = Image.alpha_composite(im, shadow)

    draw = ImageDraw.Draw(im)
    # Dark stem background
    draw.line([(cx, cy - 40*s), (cx, cy + 40*s)], fill=COLOR_BODY, width=int(round(8 * s)))
    # Glowing accent core
    draw.line([(cx, cy - 38*s), (cx, cy + 38*s)], fill=COLOR_EMERALD, width=int(round(4 * s)))
    # Top & bottom caps
    draw.line([(cx - 18*s, cy - 40*s), (cx + 18*s, cy - 40*s)], fill=COLOR_ACCENT, width=int(round(4 * s)))
    draw.line([(cx - 18*s, cy + 40*s), (cx + 18*s, cy + 40*s)], fill=COLOR_ACCENT, width=int(round(4 * s)))

    final_img = im.resize((target_size, target_size), Image.Resampling.LANCZOS)
    xhot = target_size // 2
    yhot = target_size // 2
    return final_img, xhot, yhot


def draw_crosshair(target_size: int) -> tuple:
    # Precision sniper crosshair
    scale = 4
    canvas_size = target_size * scale
    s = canvas_size / 128.0
    im = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    cx, cy = 64 * s, 64 * s

    draw = ImageDraw.Draw(im)
    # Circle
    draw.ellipse([(cx - 32*s, cy - 32*s), (cx + 32*s, cy + 32*s)], outline=COLOR_EMERALD, width=int(round(3 * s)))
    # Reticle lines
    draw.line([(cx, cy - 44*s), (cx, cy - 12*s)], fill=COLOR_ACCENT, width=int(round(2.5 * s)))
    draw.line([(cx, cy + 12*s), (cx, cy + 44*s)], fill=COLOR_ACCENT, width=int(round(2.5 * s)))
    draw.line([(cx - 44*s, cy), (cx - 12*s, cy)], fill=COLOR_ACCENT, width=int(round(2.5 * s)))
    draw.line([(cx + 12*s, cy), (cx + 44*s, cy)], fill=COLOR_ACCENT, width=int(round(2.5 * s)))
    # Center dot
    draw.ellipse([(cx - 3*s, cy - 3*s), (cx + 3*s, cy + 3*s)], fill=COLOR_EMERALD)

    final_img = im.resize((target_size, target_size), Image.Resampling.LANCZOS)
    return final_img, target_size // 2, target_size // 2


def draw_move(target_size: int) -> tuple:
    # 4-way move arrows
    scale = 4
    canvas_size = target_size * scale
    s = canvas_size / 128.0
    im = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    cx, cy = 64 * s, 64 * s
    draw = ImageDraw.Draw(im)

    # 4 arrow heads
    pts_n = [(cx, cy - 46*s), (cx - 14*s, cy - 26*s), (cx + 14*s, cy - 26*s)]
    pts_s = [(cx, cy + 46*s), (cx - 14*s, cy + 26*s), (cx + 14*s, cy + 26*s)]
    pts_w = [(cx - 46*s, cy), (cx - 26*s, cy - 14*s), (cx - 26*s, cy + 14*s)]
    pts_e = [(cx + 46*s, cy), (cx + 26*s, cy - 14*s), (cx + 26*s, cy + 14*s)]

    for p in [pts_n, pts_s, pts_w, pts_e]:
        draw.polygon(p, fill=COLOR_BODY)
        draw.line(p + [p[0]], fill=COLOR_EMERALD, width=int(round(2.5 * s)))

    draw.line([(cx, cy - 28*s), (cx, cy + 28*s)], fill=COLOR_ACCENT, width=int(round(3 * s)))
    draw.line([(cx - 28*s, cy), (cx + 28*s, cy)], fill=COLOR_ACCENT, width=int(round(3 * s)))

    final_img = im.resize((target_size, target_size), Image.Resampling.LANCZOS)
    return final_img, target_size // 2, target_size // 2


def draw_resize_col(target_size: int) -> tuple:
    # Horizontal column resize double-arrow
    scale = 4
    canvas_size = target_size * scale
    s = canvas_size / 128.0
    im = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    cx, cy = 64 * s, 64 * s
    draw = ImageDraw.Draw(im)

    # Left & Right arrows
    draw.polygon([(cx - 44*s, cy), (cx - 24*s, cy - 14*s), (cx - 24*s, cy + 14*s)], fill=COLOR_BODY, outline=COLOR_EMERALD)
    draw.polygon([(cx + 44*s, cy), (cx + 24*s, cy - 14*s), (cx + 24*s, cy + 14*s)], fill=COLOR_BODY, outline=COLOR_EMERALD)
    draw.line([(cx - 26*s, cy), (cx + 26*s, cy)], fill=COLOR_ACCENT, width=int(round(3.5 * s)))
    # Vertical divider bar
    draw.line([(cx, cy - 24*s), (cx, cy + 24*s)], fill=COLOR_EMERALD, width=int(round(3 * s)))

    final_img = im.resize((target_size, target_size), Image.Resampling.LANCZOS)
    return final_img, target_size // 2, target_size // 2


def draw_resize_row(target_size: int) -> tuple:
    # Vertical row resize double-arrow
    scale = 4
    canvas_size = target_size * scale
    s = canvas_size / 128.0
    im = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    cx, cy = 64 * s, 64 * s
    draw = ImageDraw.Draw(im)

    # Top & Bottom arrows
    draw.polygon([(cx, cy - 44*s), (cx - 14*s, cy - 24*s), (cx + 14*s, cy - 24*s)], fill=COLOR_BODY, outline=COLOR_EMERALD)
    draw.polygon([(cx, cy + 44*s), (cx - 14*s, cy + 24*s), (cx + 14*s, cy + 24*s)], fill=COLOR_BODY, outline=COLOR_EMERALD)
    draw.line([(cx, cy - 26*s), (cx, cy + 26*s)], fill=COLOR_ACCENT, width=int(round(3.5 * s)))
    # Horizontal divider bar
    draw.line([(cx - 24*s, cy), (cx + 24*s, cy)], fill=COLOR_EMERALD, width=int(round(3 * s)))

    final_img = im.resize((target_size, target_size), Image.Resampling.LANCZOS)
    return final_img, target_size // 2, target_size // 2


def draw_resize_nesw(target_size: int) -> tuple:
    # Diagonal resize (top-right to bottom-left)
    scale = 4
    canvas_size = target_size * scale
    s = canvas_size / 128.0
    im = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    cx, cy = 64 * s, 64 * s
    draw = ImageDraw.Draw(im)

    draw.polygon([(cx + 34*s, cy - 34*s), (cx + 14*s, cy - 34*s), (cx + 34*s, cy - 14*s)], fill=COLOR_BODY, outline=COLOR_EMERALD)
    draw.polygon([(cx - 34*s, cy + 34*s), (cx - 14*s, cy + 34*s), (cx - 34*s, cy + 14*s)], fill=COLOR_BODY, outline=COLOR_EMERALD)
    draw.line([(cx - 24*s, cy + 24*s), (cx + 24*s, cy - 24*s)], fill=COLOR_ACCENT, width=int(round(3.5 * s)))

    final_img = im.resize((target_size, target_size), Image.Resampling.LANCZOS)
    return final_img, target_size // 2, target_size // 2


def draw_resize_nwse(target_size: int) -> tuple:
    # Diagonal resize (top-left to bottom-right)
    scale = 4
    canvas_size = target_size * scale
    s = canvas_size / 128.0
    im = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    cx, cy = 64 * s, 64 * s
    draw = ImageDraw.Draw(im)

    draw.polygon([(cx - 34*s, cy - 34*s), (cx - 14*s, cy - 34*s), (cx - 34*s, cy - 14*s)], fill=COLOR_BODY, outline=COLOR_EMERALD)
    draw.polygon([(cx + 34*s, cy + 34*s), (cx + 14*s, cy + 34*s), (cx + 34*s, cy + 14*s)], fill=COLOR_BODY, outline=COLOR_EMERALD)
    draw.line([(cx - 24*s, cy - 24*s), (cx + 24*s, cy + 24*s)], fill=COLOR_ACCENT, width=int(round(3.5 * s)))

    final_img = im.resize((target_size, target_size), Image.Resampling.LANCZOS)
    return final_img, target_size // 2, target_size // 2


def draw_not_allowed(target_size: int) -> tuple:
    # Forbidden / Not-Allowed icon
    scale = 4
    canvas_size = target_size * scale
    s = canvas_size / 128.0
    im = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    cx, cy = 64 * s, 64 * s
    draw = ImageDraw.Draw(im)

    # Coral red forbidden circle with diagonal slash
    draw.ellipse([(cx - 36*s, cy - 36*s), (cx + 36*s, cy + 36*s)], outline=COLOR_CORAL, width=int(round(6 * s)))
    draw.line([(cx - 24*s, cy - 24*s), (cx + 24*s, cy + 24*s)], fill=COLOR_CORAL, width=int(round(6 * s)))

    final_img = im.resize((target_size, target_size), Image.Resampling.LANCZOS)
    return final_img, target_size // 2, target_size // 2


def draw_spinner_frame(target_size: int, frame_idx: int, num_frames: int = 8, with_pointer: bool = False) -> tuple:
    # Smooth modern circular orbital spinner (for wait and progress)
    scale = 4
    canvas_size = target_size * scale
    s = canvas_size / 128.0
    im = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

    if with_pointer:
        ptr, _, _ = draw_aerodynamic_pointer(target_size, False)
        im = ptr.resize((canvas_size, canvas_size), Image.Resampling.NEAREST)
        scx, scy = 88 * s, 88 * s
        sr = 22 * s
    else:
        scx, scy = 64 * s, 64 * s
        sr = 36 * s

    draw = ImageDraw.Draw(im)
    base_angle = (360.0 / num_frames) * frame_idx

    for i in range(num_frames):
        a = math.radians(base_angle + i * (360.0 / num_frames))
        ax = scx + math.cos(a) * sr
        ay = scy + math.sin(a) * sr
        dot_r = (2.0 + 3.5 * (i / num_frames)) * s
        alpha = int(60 + 195 * (i / num_frames))
        col = (COLOR_EMERALD[0], COLOR_EMERALD[1], COLOR_EMERALD[2], alpha)
        draw.ellipse([(ax - dot_r, ay - dot_r), (ax + dot_r, ay + dot_r)], fill=col)

    final_img = im.resize((target_size, target_size), Image.Resampling.LANCZOS)
    xhot = int(round(4 * (target_size / 32.0))) if with_pointer else target_size // 2
    yhot = int(round(4 * (target_size / 32.0))) if with_pointer else target_size // 2
    return final_img, xhot, yhot


def build_cursor_theme() -> None:
    # Build complete cursor theme directory
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)

    out_cursors = OUT_DIR / "cursors"
    out_cursors.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "index.theme").write_text(INDEX_THEME)

    sizes = [24, 32, 48]

    # 1. Base cursor shapes map
    generators = {
        "default": lambda sz: draw_aerodynamic_pointer(sz, False),
        "pointer": lambda sz: draw_pointer_hand(sz),
        "text": lambda sz: draw_ibeam_text(sz),
        "crosshair": lambda sz: draw_crosshair(sz),
        "move": lambda sz: draw_move(sz),
        "col-resize": lambda sz: draw_resize_col(sz),
        "row-resize": lambda sz: draw_resize_row(sz),
        "nesw-resize": lambda sz: draw_resize_nesw(sz),
        "nwse-resize": lambda sz: draw_resize_nwse(sz),
        "not-allowed": lambda sz: draw_not_allowed(sz),
    }

    # Render static cursors
    for name, gen_fn in generators.items():
        frames = []
        for sz in sizes:
            img, xh, yh = gen_fn(sz)
            frames.append((img, xh, yh, 0))
        raw_bytes = make_xcursor(frames)
        (out_cursors / name).write_bytes(raw_bytes)
        print(f"  + generated cursor: {name}")

    # Render animated progress and wait cursors (8 frames @ 60ms delay)
    for name, with_ptr in [("wait", False), ("progress", True)]:
        frames = []
        for f in range(8):
            for sz in sizes:
                img, xh, yh = draw_spinner_frame(sz, f, num_frames=8, with_pointer=with_ptr)
                frames.append((img, xh, yh, 60))
        raw_bytes = make_xcursor(frames)
        (out_cursors / name).write_bytes(raw_bytes)
        print(f"  + generated animated cursor: {name}")

    # Symlink aliases
    aliases = {
        "default": [
            "arrow", "top_left_arrow", "left_ptr", "right_ptr", "center_ptr",
        ],
        "pointer": [
            "hand1", "hand2", "pointing_hand", "e29285e634086352946a0e7090d73106",
            "9d800788f1b08800ae810202380a0822",
        ],
        "text": [
            "xterm", "ibeam",
        ],
        "wait": [
            "watch", "0426c80cad02078e4301040052da300e",
        ],
        "progress": [
            "left_ptr_watch", "3ecb610c1bf2410f44200f48c40d3599",
            "08e8e1c95fe2fc01f976f1e063a24ccd", "00000000000000020006000e7e9ffc3f",
        ],
        "crosshair": [
            "cross", "tcross",
        ],
        "move": [
            "fleur", "all-scroll", "4498f0e0c1937ffe01fd06f973665830",
            "9081237383d90e509aa00f00170e968f",
        ],
        "not-allowed": [
            "circle", "crossed_circle", "03b6e0fcb3499374a867c041f52298f0",
        ],
        "col-resize": [
            "ew-resize", "split_h", "size_hor", "h_double_arrow",
            "028006030e0e7ebffb7f7070c0600140", "e-resize", "w-resize",
        ],
        "row-resize": [
            "ns-resize", "split_v", "size_ver", "v_double_arrow",
            "00008160000006810000408080010102", "n-resize", "s-resize",
        ],
        "nesw-resize": [
            "size_bdiag", "50585d5204e6e9a0397017c60f1e0878",
            "fcf1c3c7cd4491d801f1e1c78f100822", "ne-resize", "sw-resize",
        ],
        "nwse-resize": [
            "size_fdiag", "38c9d0d4e788665001f357607e443022",
            "c7088f0f3e6c8088236ef8e1e3e70000", "nw-resize", "se-resize",
        ],
    }

    for target, symlinks in aliases.items():
        for link_name in symlinks:
            dst = out_cursors / link_name
            if not dst.exists():
                dst.symlink_to(target)

    print(f"Generated {len(aliases)} cursor categories with symlinks into {OUT_DIR}")


if __name__ == "__main__":
    build_cursor_theme()
