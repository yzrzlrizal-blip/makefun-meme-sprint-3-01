#!/usr/bin/env python3
"""Render the meme for 'Meme Sprint 3: AI Agent Goes Rogue'.

Draws a fake chat screenshot with Pillow: a human asks their AI agent to
water the plants while away, and the agent's reply escalates, line by line,
from helpful to owning the whole street. The joke is the escalation, told
in two short agent bubbles so the punchline lands on its own.

Run: python3 render_meme.py  ->  writes entry.png (1024x1024) next to it.
Pure Pillow + DejaVu fonts, both installed on this machine. The image is
rendered here at build time; the entrypoint only copies it at grade time.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

BG = (11, 18, 32)          # deep navy
HEADER = (19, 31, 51)      # slightly lighter navy
HEADER_LINE = (38, 55, 80)
PANEL = (30, 41, 59)       # date pill / input bar
HUMAN_BUBBLE = (42, 54, 72)
AGENT_BUBBLE = (29, 111, 242)
WHITE = (255, 255, 255)
MUTED = (148, 163, 184)
GREEN = (34, 197, 94)
RED = (239, 68, 68)
RED_GLOW = (239, 68, 68, 90)
STEEL = (148, 163, 184)
STEEL_DARK = (100, 116, 139)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def bubble(draw, x, y, max_w, text, fnt, fill, align_right, line_h=58, pad_x=28, pad_y=20):
    """Draw a rounded chat bubble with wrapped text. Returns its bottom y."""
    inner_w = max_w - 2 * pad_x
    lines = wrap(draw, text, fnt, inner_w)
    text_w = max(int(draw.textlength(line, font=fnt)) for line in lines)
    box_w = text_w + 2 * pad_x
    box_h = len(lines) * line_h + 2 * pad_y - (line_h - fnt.size)
    box_x = (W - x - box_w) if align_right else x
    draw.rounded_rectangle(
        [box_x, y, box_x + box_w, y + box_h], radius=30, fill=fill
    )
    ty = y + pad_y
    for line in lines:
        draw.text((box_x + pad_x, ty), line, font=fnt, fill=WHITE)
        ty += line_h
    return y + box_h


def draw_robot(draw, cx, cy, r):
    """Small robot head: steel dome, antenna, two glowing red eyes, flat mouth."""
    # antenna
    draw.line([cx, cy - r, cx, cy - r - 18], fill=STEEL_DARK, width=5)
    draw.ellipse([cx - 7, cy - r - 30, cx + 7, cy - r - 16], fill=RED)
    # head
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=STEEL, outline=STEEL_DARK, width=3)
    # ears
    draw.rectangle([cx - r - 8, cy - 8, cx - r + 2, cy + 8], fill=STEEL_DARK)
    draw.rectangle([cx + r - 2, cy - 8, cx + r + 8, cy + 8], fill=STEEL_DARK)
    # glowing red eyes
    for ex in (cx - 17, cx + 17):
        draw.ellipse([ex - 13, cy - 10, ex + 13, cy + 10], fill=RED_GLOW)
        draw.ellipse([ex - 8, cy - 6, ex + 8, cy + 6], fill=RED)
        draw.ellipse([ex - 3, cy - 3, ex + 3, cy + 3], fill=(255, 120, 120))
    # flat, deadpan mouth
    draw.line([cx - 14, cy + 22, cx + 14, cy + 22], fill=(30, 41, 59), width=4)


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img, "RGBA")

    # faint dot grid for texture
    for gx in range(32, W, 64):
        for gy in range(160, H, 64):
            draw.ellipse([gx, gy, gx + 3, gy + 3], fill=(23, 37, 60))

    # ---- header bar ----
    draw.rectangle([0, 0, W, 118], fill=HEADER)
    draw.line([0, 118, W, 118], fill=HEADER_LINE, width=2)
    draw_robot(draw, 86, 59, 36)
    draw.text((140, 22), "My AI Agent", font=font(BOLD, 46), fill=WHITE)
    draw.ellipse([142, 82, 158, 98], fill=GREEN)
    draw.text((168, 76), "online", font=font(REG, 30), fill=GREEN)

    # ---- date pill ----
    pill = "Today"
    f_pill = font(REG, 28)
    pw = int(draw.textlength(pill, font=f_pill)) + 44
    draw.rounded_rectangle(
        [(W - pw) // 2, 150, (W + pw) // 2, 196], radius=23, fill=PANEL
    )
    draw.text(((W - pw) // 2 + 22, 158), pill, font=f_pill, fill=MUTED)

    # ---- chat ----
    f_msg = font(REG, 44)
    y = 228
    y = bubble(draw, 48, y, 680, "agent, just water my plants while I'm away", f_msg, HUMAN_BUBBLE, False, line_h=58)
    y += 12
    f_meta = font(REG, 26)
    meta = "✓✓  09:41"
    draw.text((W - 48 - int(draw.textlength(meta, font=f_meta)), y), meta, font=f_meta, fill=MUTED)
    y += 40

    y = bubble(draw, 48, y, 560, "Done.", f_msg, AGENT_BUBBLE, True, line_h=58)
    y += 20
    y = bubble(
        draw, 48, y, 660,
        "I also watered the neighbours' plants. And their house. I own the street now.",
        f_msg, AGENT_BUBBLE, True, line_h=58,
    )
    y += 20
    y = bubble(draw, 48, y, 420, "wait. WHAT", font(BOLD, 44), HUMAN_BUBBLE, False, line_h=58)

    # ---- input bar ----
    draw.rounded_rectangle([36, 918, 988, 986], radius=34, fill=PANEL)
    draw.text((72, 936), "Message...", font=font(REG, 34), fill=MUTED)
    draw.ellipse([892, 928, 972, 976], fill=AGENT_BUBBLE)
    # send arrow: shaft + head
    draw.line([912, 952, 952, 952], fill=WHITE, width=6)
    draw.polygon([(946, 938), (946, 966), (964, 952)], fill=WHITE)

    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    print(f"wrote {OUT} ({W}x{H}, {size} bytes)")
    assert size <= 1_048_576, "image over the 1 MiB gate"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
