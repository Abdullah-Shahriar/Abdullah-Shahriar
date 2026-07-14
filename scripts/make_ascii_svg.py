import os
import io
import base64
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ─── CONFIGURATION ──────────────────────────────────────
INPUT_FILE   = 'public/source-prepped.png'
OUTPUT_SVG   = 'public/avi-ascii.svg'
OUTPUT_PNG   = 'public/avi-ascii.png'

WIDTH_CHARS  = 240          # Higher resolution grid for more detail

BLACK_FLOOR  = 12           # Trim pure black background
CONTRAST     = 1.35         # Slight contrast boost for punchier look
GAMMA        = 0.9          # Slight gamma correction

ASCII_CHARS  = ' .,:;+=*#%@'

RENDER_FONT_SIZE = 10       
BG_RGB       = (0, 0, 0)    # Pure black background

TITLE_BAR_H  = 0
ANIM_DURATION = 8.0
STATIC = False
# ────────────────────────────────────────────────────

def load_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/consola.ttf", 
        "C:/Windows/Fonts/lucon.ttf",
        "C:/Windows/Fonts/cour.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    print("[ascii] Warning: Falling back to default font.")
    return ImageFont.load_default()

def measure_cell(font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    cell_w = max(1, int(font.getlength("0")))
    ascent, descent = font.getmetrics()
    cell_h = max(1, ascent + descent)
    return cell_w, cell_h

def render_binary_ascii(img_path: str, font: ImageFont.FreeTypeFont, cell_w: int, cell_h: int) -> Image.Image:
    img = Image.open(img_path).convert("L")
    src_w, src_h = img.size
    aspect_corr = cell_w / cell_h
    height_chars = max(1, round(WIDTH_CHARS * (src_h / src_w) * aspect_corr))
    img = img.resize((WIDTH_CHARS, height_chars), Image.LANCZOS)

    px = np.array(img, dtype=np.float32) / 255.0
    px = np.clip((px - 0.5) * CONTRAST + 0.5, 0.0, 1.0)
    px = np.power(px, GAMMA)
    px_u8 = (px * 255).astype(np.uint8)

    pad = 0
    img_w = cell_w * WIDTH_CHARS + pad * 2
    img_h = cell_h * height_chars + pad * 2

    canvas = Image.new("RGB", (img_w, img_h), BG_RGB)
    draw = ImageDraw.Draw(canvas)

    n_chars = len(ASCII_CHARS)
    rows = []
    
    for y in range(height_chars):
        row_str = []
        for x in range(WIDTH_CHARS):
            val = px_u8[y, x]
            if val < BLACK_FLOOR:
                row_str.append(" ")
                continue
            idx = int((val / 255.0) * (n_chars - 1))
            char = ASCII_CHARS[idx]
            row_str.append(char)
            draw.text((pad + x * cell_w, pad + y * cell_h), char, fill=(val, val, val), font=font)
        rows.append("".join(row_str))

    return canvas

def build_svg(png_bytes: bytes, img_w: int, img_h: int, char_w: int, char_h: int, row_count: int) -> str:
    b64 = base64.b64encode(png_bytes).decode("ascii")
    bg_hex = "#{:02x}{:02x}{:02x}".format(*BG_RGB)
    svg_w, svg_h = img_w, img_h
    img_y = 0

    lines = []
    a = lines.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    a(f'<rect width="{svg_w}" height="{svg_h}" fill="{bg_hex}"/>')
    a(f'<image x="0" y="{img_y}" width="{img_w}" height="{img_h}" href="data:image/png;base64,{b64}" image-rendering="crisp-edges"/>')
    
    if not STATIC:
        steps = row_count
        y_values_bottom = ";".join(str(img_y + (i + 1) * char_h) for i in range(steps + 1))
        h_values_bottom = ";".join(str(max(0, img_h - (i + 1) * char_h)) for i in range(steps + 1))
        y_values_current = ";".join(str(img_y + i * char_h) for i in range(steps + 1))
        y_values_pen = ";".join(str(img_y + i * char_h - int(char_h * 0.5)) for i in range(steps + 1))
        
        x_values_mask = []
        x_values_pen = []
        key_times = []
        
        for i in range(steps):
            t_start = i / steps
            t_end = (i + 1) / steps
            
            if i > 0:
                t_start_safe = t_start + 0.00001
                key_times.append(f"{t_start_safe:.5f}")
            else:
                key_times.append(f"{t_start:.5f}")
                
            if i % 2 == 0:
                # L -> R
                x_values_mask.extend(["0", str(svg_w)])
                x_values_pen.extend(["0", str(svg_w)])
            else:
                # R -> L
                x_values_mask.extend(["0", f"-{svg_w}"])
                x_values_pen.extend([str(svg_w), "0"])
                
            key_times.append(f"{t_end:.5f}")
            
        x_values_mask_str = ";".join(x_values_mask)
        x_values_pen_str = ";".join(x_values_pen)
        key_times_str = ";".join(key_times)
        
        # Rect 1: Covers all rows below the current sketching row
        a(f'<rect x="0" y="{img_y + char_h}" width="{svg_w}" height="{max(0, img_h - char_h)}" fill="{bg_hex}">')
        a(f'  <animate attributeName="y" values="{y_values_bottom}" dur="{ANIM_DURATION}s" calcMode="discrete" fill="freeze"/>')
        a(f'  <animate attributeName="height" values="{h_values_bottom}" dur="{ANIM_DURATION}s" calcMode="discrete" fill="freeze"/>')
        a('</rect>')
        
        # Rect 2: Sweeps left-to-right then right-to-left seamlessly
        a(f'<rect x="0" y="{img_y}" width="{svg_w}" height="{char_h}" fill="{bg_hex}">')
        a(f'  <animate attributeName="y" values="{y_values_current}" dur="{ANIM_DURATION}s" calcMode="discrete" fill="freeze"/>')
        a(f'  <animate attributeName="x" values="{x_values_mask_str}" keyTimes="{key_times_str}" dur="{ANIM_DURATION}s" calcMode="linear" fill="freeze"/>')
        a('</rect>')
        
        # Fast moving pen cursor tracking the seamless shading line
        # Made significantly larger (5x width, 2x height) and neon green to be effortlessly visible at high resolutions
        a(f'<rect x="0" y="0" width="{char_w * 5}" height="{char_h * 2}" fill="#00ff00" rx="{char_w}">')
        a(f'  <animate attributeName="y" values="{y_values_pen}" dur="{ANIM_DURATION}s" calcMode="discrete" fill="freeze"/>')
        a(f'  <animate attributeName="x" values="{x_values_pen_str}" keyTimes="{key_times_str}" dur="{ANIM_DURATION}s" calcMode="linear" fill="freeze"/>')
        a(f'  <animate attributeName="opacity" to="0" begin="{ANIM_DURATION}s" dur="0.1s" fill="freeze"/>')
        a('</rect>')

    a('</svg>')
    return "\n".join(lines)

def main():
    print("[ascii] Rendering binary matrix image...")
    font = load_font(RENDER_FONT_SIZE)
    cell_w, cell_h = measure_cell(font)
    
    ascii_img = render_binary_ascii(INPUT_FILE, font, cell_w, cell_h)
    iw, ih = ascii_img.size
    print(f"[ascii] Canvas size: {iw}x{ih} px")
    
    ascii_img.save(OUTPUT_PNG, optimize=True)
    print(f"[ascii] Saved {OUTPUT_PNG}")

    buf = io.BytesIO()
    ascii_img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    
    row_count = ih // cell_h
    svg = build_svg(buf.read(), iw, ih, cell_w, cell_h, row_count)
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[ascii] Saved {OUTPUT_SVG}")

if __name__ == "__main__":
    main()
