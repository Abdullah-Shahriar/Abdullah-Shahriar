#!/usr/bin/env python3
"""
make_info_card.py — Generate a terminal-style info card SVG
                     with line-by-line typing reveal animation.

Writes: info-card.svg
"""

# ────────────────────── CONFIG (edit your details here) ──────────────────────
HOST = "abdullah@dev"

ROWS = [
    ("ROLE",       "CSE Undergrad · Bangladesh"),
    ("FOCUS",      "Cross-Functional Orchestration"),
    ("",           "Full Stack Development"),
    ("",           "Zero-to-One Engineering"),
    ("---",        ""),
    ("STACK",      "Python · JavaScript · TypeScript"),
    ("",           "React · Next.js · Node.js"),
    ("",           "C · C++ · Java"),
    ("",           "Git · Linux · Docker"),
    ("---",        ""),
    ("NOW",        "Building systems that matter"),
    ("",           "Software Engineering & AI"),
    ("---",        ""),
    ("LINKS",      "github.com/Abdullah-Shahriar"),
    ("",           "linkedin.com/in/abdullah-shahriar-a24371350"),
]

# Dimensions — adjust H if rows overflow
W = 490
H = 370   # match portrait height
FONT_SIZE = 12
LINE_H = 20
PAD_X = 20
PAD_Y = 45   # below the title bar

# Appearance (monochrome)
BG_COLOR       = "#0d1117"
BORDER_COLOR   = "#30363d"
TITLE_BG       = "#161b22"
TEXT_COLOR      = "#c9d1d9"
LABEL_COLOR    = "#8b949e"
PROMPT_COLOR   = "#58a6ff"
DOT_COLORS     = ["#ff5f56", "#ffbd2e", "#27c93f"]

# Animation
LINE_DELAY     = 0.15     # seconds between each line reveal
TYPING_SPEED   = 0.02     # seconds per character for typing cursor
# ────────────────────── END CONFIG ───────────────────────────────


def generate_info_card() -> str:
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')

    # Background
    parts.append(f'<rect width="{W}" height="{H}" fill="{BG_COLOR}" rx="6" stroke="{BORDER_COLOR}" stroke-width="1"/>')

    # Title bar
    parts.append(f'<rect width="{W}" height="30" fill="{TITLE_BG}" rx="6"/>')
    parts.append(f'<rect x="0" y="24" width="{W}" height="6" fill="{TITLE_BG}"/>')  # cover bottom radius

    # Window dots
    for i, color in enumerate(DOT_COLORS):
        cx = 16 + i * 16
        parts.append(f'<circle cx="{cx}" cy="15" r="5" fill="{color}"/>')

    # Title text
    parts.append(f'<text x="{W // 2}" y="19" text-anchor="middle" fill="{LABEL_COLOR}" '
                 f'font-family="\'Courier New\', monospace" font-size="11">{HOST}</text>')

    # Style for animation
    parts.append("<style>")
    parts.append(f"""
    .info-line {{
        font-family: 'Courier New', Courier, monospace;
        font-size: {FONT_SIZE}px;
        opacity: 0;
        animation: lineReveal 0.3s forwards;
    }}
    @keyframes lineReveal {{
        0% {{ opacity: 0; transform: translateY(5px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}
    .blink {{
        animation: blink 1s steps(2) infinite;
    }}
    @keyframes blink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0; }}
    }}
    """)
    parts.append("</style>")

    # Render rows
    y = PAD_Y
    line_idx = 0
    for label, value in ROWS:
        if label == "---":
            # Separator line
            delay = line_idx * LINE_DELAY
            parts.append(f'<line x1="{PAD_X}" y1="{y + 4}" x2="{W - PAD_X}" y2="{y + 4}" '
                         f'stroke="{BORDER_COLOR}" stroke-width="0.5" opacity="0" '
                         f'style="animation: lineReveal 0.3s {delay:.2f}s forwards"/>')
            y += LINE_H * 0.6
            line_idx += 1
            continue

        delay = line_idx * LINE_DELAY

        if label:
            # Label: value format
            parts.append(f'<text x="{PAD_X}" y="{y}" class="info-line" '
                         f'style="animation-delay: {delay:.2f}s">'
                         f'<tspan fill="{PROMPT_COLOR}">❯ </tspan>'
                         f'<tspan fill="{LABEL_COLOR}">{label}  </tspan>'
                         f'<tspan fill="{TEXT_COLOR}">{_escape(value)}</tspan>'
                         f'</text>')
        else:
            # Continuation line (indented)
            parts.append(f'<text x="{PAD_X + 12}" y="{y}" class="info-line" '
                         f'style="animation-delay: {delay:.2f}s">'
                         f'<tspan fill="{TEXT_COLOR}">  {_escape(value)}</tspan>'
                         f'</text>')

        y += LINE_H
        line_idx += 1

    # Blinking cursor at the end
    cursor_delay = line_idx * LINE_DELAY
    parts.append(f'<text x="{PAD_X}" y="{y + 5}" fill="{PROMPT_COLOR}" '
                 f'font-family="\'Courier New\', monospace" font-size="{FONT_SIZE}" '
                 f'class="blink" style="animation-delay: {cursor_delay:.2f}s">'
                 f'❯ _</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    svg = generate_info_card()
    with open("public/info-card.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[info-card] Generated public/info-card.svg ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
