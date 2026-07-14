#!/usr/bin/env python3
"""
render_heatmap_svg.py — Render a GitHub-style contribution heatmap SVG
                         with cell-by-cell reveal animation.

Reads:  contributions.json
Writes: contrib-heatmap.svg
"""

import json
import math
from datetime import datetime, timedelta

# ────────────────────── CONFIG ──────────────────────
INPUT_FILE  = "contributions.json"
OUTPUT_FILE = "public/contrib-heatmap.svg"

CELL_SIZE   = 11       # px
CELL_GAP    = 3        # px between cells
CELL_ROUND  = 2        # border radius
PAD_LEFT    = 35       # space for month labels
PAD_TOP     = 25       # space for day labels
PAD_RIGHT   = 15
PAD_BOTTOM  = 40       # space for legend + stats

# Monochrome green palette (GitHub-style)
COLORS = {
    0: "#161b22",   # empty
    1: "#0e4429",   # low
    2: "#006d32",   # medium-low
    3: "#26a641",   # medium-high
    4: "#39d353",   # high
}
BG_COLOR     = "transparent"
TEXT_COLOR   = "#8b949e"
BORDER_COLOR = "#21262d"

# Animation
REVEAL_DELAY = 0.005   # seconds between each cell reveal
# ────────────────────── END CONFIG ──────────────────


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS   = ["Mon", "Wed", "Fri"]


def render_heatmap(data: dict) -> str:
    days = data["days"]
    if not days:
        # Generate empty grid
        days = []

    # Organize days into weeks (columns) × days-of-week (rows)
    # GitHub shows Sun at top (row 0) through Sat (row 6)
    weeks = []
    current_week = [None] * 7

    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        dow = dt.weekday()  # 0=Mon, 6=Sun
        # GitHub layout: Sun=0, Mon=1, ..., Sat=6
        gh_dow = (dow + 1) % 7

        if gh_dow == 0 and any(c is not None for c in current_week):
            weeks.append(current_week)
            current_week = [None] * 7

        current_week[gh_dow] = d

    if any(c is not None for c in current_week):
        weeks.append(current_week)

    num_weeks = len(weeks)
    step = CELL_SIZE + CELL_GAP

    svg_w = PAD_LEFT + num_weeks * step + PAD_RIGHT
    svg_h = PAD_TOP + 7 * step + PAD_BOTTOM

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')

    # Style
    parts.append("""<style>
    .hm-cell {
        opacity: 0;
        animation: cellReveal 0.3s forwards;
    }
    @keyframes cellReveal {
        0% { opacity: 0; transform: scale(0); }
        60% { transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1); }
    }
    .hm-text {
        font-family: 'Segoe UI', -apple-system, sans-serif;
        fill: """ + TEXT_COLOR + """;
    }
</style>""")

    # Background
    if BG_COLOR != "transparent":
        parts.append(f'<rect width="{svg_w}" height="{svg_h}" fill="{BG_COLOR}" rx="6"/>')

    # Day labels (Mon, Wed, Fri)
    day_positions = {1: "Mon", 3: "Wed", 5: "Fri"}
    for row, label in day_positions.items():
        y = PAD_TOP + row * step + CELL_SIZE * 0.75
        parts.append(f'<text x="{PAD_LEFT - 5}" y="{y}" text-anchor="end" '
                     f'class="hm-text" font-size="9">{label}</text>')

    # Month labels
    month_labels_placed = set()
    for week_idx, week in enumerate(weeks):
        for d in week:
            if d is not None:
                dt = datetime.strptime(d["date"], "%Y-%m-%d")
                month_key = (dt.year, dt.month)
                if month_key not in month_labels_placed and dt.day <= 7:
                    x = PAD_LEFT + week_idx * step
                    parts.append(f'<text x="{x}" y="{PAD_TOP - 8}" '
                                 f'class="hm-text" font-size="9">{MONTHS[dt.month - 1]}</text>')
                    month_labels_placed.add(month_key)
                break

    # Grid cells
    cell_idx = 0
    for week_idx, week in enumerate(weeks):
        x = PAD_LEFT + week_idx * step
        for row in range(7):
            y = PAD_TOP + row * step
            d = week[row]
            level = d["level"] if d else 0
            color = COLORS.get(level, COLORS[0])
            delay = cell_idx * REVEAL_DELAY

            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                f'rx="{CELL_ROUND}" ry="{CELL_ROUND}" fill="{color}" '
                f'class="hm-cell" style="animation-delay: {delay:.3f}s; '
                f'transform-origin: {x + CELL_SIZE/2}px {y + CELL_SIZE/2}px"/>'
            )
            cell_idx += 1

    # Legend
    legend_y = PAD_TOP + 7 * step + 15
    legend_x = svg_w - PAD_RIGHT - 150

    parts.append(f'<text x="{legend_x}" y="{legend_y + 9}" '
                 f'class="hm-text" font-size="9">Less</text>')

    for i, (lvl, color) in enumerate(COLORS.items()):
        bx = legend_x + 30 + i * (CELL_SIZE + 2)
        parts.append(f'<rect x="{bx}" y="{legend_y}" width="{CELL_SIZE}" '
                     f'height="{CELL_SIZE}" rx="2" fill="{color}"/>')

    parts.append(f'<text x="{legend_x + 30 + 5 * (CELL_SIZE + 2) + 2}" y="{legend_y + 9}" '
                 f'class="hm-text" font-size="9">More</text>')

    # Stats
    stats_y = legend_y
    total = data.get("total_contributions", 0)
    cur_streak = data.get("current_streak", 0)
    max_streak = data.get("max_streak", 0)

    parts.append(f'<text x="{PAD_LEFT}" y="{stats_y + 9}" class="hm-text" font-size="10">'
                 f'{total} contributions in the last year'
                 f'</text>')

    # Second line of stats
    parts.append(f'<text x="{PAD_LEFT}" y="{stats_y + 22}" class="hm-text" font-size="9">'
                 f'Current streak: {cur_streak} days  ·  '
                 f'Longest streak: {max_streak} days'
                 f'</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[heatmap] Loaded {len(data.get('days', []))} days from {INPUT_FILE}")
    svg = render_heatmap(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[heatmap] Generated {OUTPUT_FILE} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
