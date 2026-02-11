import random

# SHAHRIAR centered in 9-row grid (2 top + 5 letter + 2 bottom)
# Inactive cells look like dim contribution cells (not empty)
# Active cells scatter then gather animation

letters = {
    'S': [
        [0,1,1,1,1],
        [0,1,0,0,0],
        [0,1,1,1,1],
        [0,0,0,0,1],
        [0,1,1,1,1],
    ],
    'H': [
        [1,0,0,1,0],
        [1,0,0,1,0],
        [1,1,1,1,0],
        [1,0,0,1,0],
        [1,0,0,1,0],
    ],
    'A': [
        [0,1,1,0,0],
        [1,0,0,1,0],
        [1,1,1,1,0],
        [1,0,0,1,0],
        [1,0,0,1,0],
    ],
    'R': [
        [1,1,1,0,0],
        [1,0,0,1,0],
        [1,1,1,0,0],
        [1,0,1,0,0],
        [1,0,0,1,0],
    ],
    'I': [
        [1,1,1,0,0],
        [0,1,0,0,0],
        [0,1,0,0,0],
        [0,1,0,0,0],
        [1,1,1,0,0],
    ],
}

word = 'SHAHRIAR'
cell_w = 11
cell_gap = 15
rows = 9         # 2 top padding + 5 letter rows + 2 bottom padding
top_pad = 2      # letter starts at row 2
cols_per_letter = 5

total_cols = len(word) * cols_per_letter + (len(word) - 1)

# Map active cells (letter cells offset by top_pad)
active_cells = set()
col_offset = 0
for ch in word:
    grid = letters[ch]
    for r in range(5):
        for c in range(cols_per_letter):
            if grid[r][c]:
                active_cells.add((col_offset + c, top_pad + r))
    col_offset += cols_per_letter + 1

svg_w = total_cols * cell_gap + 30
svg_h = rows * cell_gap + 40

random.seed(42)
# Letter cells use ONLY bright greens for maximum visibility
color_levels = ['--c1', '--c2', '--c1', '--c2']

# Background cells: mostly dark, only ~10% get a very subtle dim green
inactive_levels = {}
for col in range(total_cols):
    for row in range(rows):
        if (col, row) not in active_cells:
            r = random.random()
            if r < 0.90:
                inactive_levels[(col, row)] = 0   # 90% dark
            else:
                inactive_levels[(col, row)] = 1   # 10% very dim green

# Build keyframes for active cells
keyframes_css = []
cell_class_map = {}
cell_idx = 0

for col in range(total_cols):
    for row in range(rows):
        if (col, row) in active_cells:
            tx = random.randint(-350, 350)
            ty = random.randint(-200, 200)
            angle = random.randint(-360, 360)
            target_color = random.choice(color_levels)
            kf_name = f"c{cell_idx}"
            keyframes_css.append(f"""@keyframes {kf_name} {{
    0% {{ transform: translate({tx}px, {ty}px) rotate({angle}deg); opacity: 0 }}
    15% {{ opacity: 0.4 }}
    60% {{ transform: translate(0, 0) rotate(0deg); opacity: 1 }}
    75% {{ fill: var({target_color}) }}
    100% {{ transform: translate(0, 0) rotate(0deg); opacity: 1; fill: var({target_color}) }}
}}
.c.{kf_name} {{ animation-name: {kf_name} }}""")
            cell_class_map[(col, row)] = kf_name
            cell_idx += 1

# Build SVG
lines = []
lines.append(f'<svg width="{svg_w}" height="{svg_h}" class="js-calendar-graph-svg" xmlns="http://www.w3.org/2000/svg">')
lines.append('<style>')
lines.append("""    :root {
        --c0: #161b22;
        --c0border: #21262d;
        --c1: #9be9a8;
        --c2: #40c463;
        --c3: #30a14e;
        --c4: #216e39;
    }
    .o {
        shape-rendering: geometricPrecision;
        outline: 1px solid var(--c0border);
        outline-offset: -1px
    }
    .o[data-level="0"] { fill: var(--c0) }
    .o[data-level="1"] { fill: #0e4429 }
    .c {
        animation-iteration-count: infinite;
        animation-duration: 6s;
        animation-timing-function: cubic-bezier(0.22, 1, 0.36, 1);
    }""")
for kf in keyframes_css:
    lines.append(kf)
lines.append('</style>')

lines.append(f'<rect width="{svg_w}" height="{svg_h}" fill="#0d1117" rx="6"/>')

lines.append(f'<g transform="translate(15, 20)">')
for col in range(total_cols):
    lines.append(f'<g transform="translate({col * cell_gap}, 0)">')
    for row in range(rows):
        y = row * cell_gap
        if (col, row) in cell_class_map:
            cls = f'o c {cell_class_map[(col, row)]}'
            lvl = '0'
        else:
            cls = 'o'
            lvl = str(inactive_levels.get((col, row), 0))
        lines.append(f'<rect width="{cell_w}" height="{cell_w}" x="0" y="{y}" data-level="{lvl}" rx="2" ry="2" class="{cls}"></rect>')
    lines.append('</g>')
lines.append('</g>')
lines.append('</svg>')

output_path = r'c:\Users\abdul\OneDrive\Documents\GitHub\Abdullah-Shahriar\gitartwork.svg'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'SVG generated: {svg_w}x{svg_h}')
print(f'Active cells: {cell_idx}, Grid: {total_cols}x{rows} = {total_cols * rows}')
