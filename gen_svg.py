import random

# Exact same technique as tubakhxn/gitartwork (proven to work on GitHub)
# CSS <style> with per-cell @keyframes rotation + var() colors

letters = {
    'S': [
        [0,1,1,1,1],
        [0,1,0,0,0],
        [0,1,1,1,1],
        [0,0,0,0,1],
        [0,1,1,1,1],
        [0,0,0,0,0],
        [0,0,0,0,0],
    ],
    'H': [
        [1,0,0,1,0],
        [1,0,0,1,0],
        [1,1,1,1,0],
        [1,0,0,1,0],
        [1,0,0,1,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
    ],
    'A': [
        [0,1,1,0,0],
        [1,0,0,1,0],
        [1,1,1,1,0],
        [1,0,0,1,0],
        [1,0,0,1,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
    ],
    'R': [
        [1,1,1,0,0],
        [1,0,0,1,0],
        [1,1,1,0,0],
        [1,0,1,0,0],
        [1,0,0,1,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
    ],
    'I': [
        [1,1,1,0,0],
        [0,1,0,0,0],
        [0,1,0,0,0],
        [0,1,0,0,0],
        [1,1,1,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
    ],
}

word = 'SHAHRIAR'
cell_w = 11
cell_gap = 15  # pitch between cells (matches GitHub contribution graph)
rows = 7
cols_per_letter = 5

# Build the full grid: figure out total columns
total_letter_cols = len(word) * cols_per_letter
# Add 1-col gap between letters
total_cols = total_letter_cols + (len(word) - 1)

# Map which (col, row) cells are "active" (part of a letter)
active_cells = set()
col_offset = 0
for ch in word:
    grid = letters[ch]
    for row in range(rows):
        for col in range(cols_per_letter):
            if grid[row][col]:
                active_cells.add((col_offset + col, row))
    col_offset += cols_per_letter + 1  # +1 for gap between letters

svg_w = total_cols * cell_gap + 30  # padding
svg_h = rows * cell_gap + 40

random.seed(42)
color_levels = ['--c1', '--c2', '--c3', '--c4']

# Build keyframes for each active cell
keyframes_css = []
cell_class_map = {}
cell_idx = 0

for col in range(total_cols):
    for row in range(rows):
        if (col, row) in active_cells:
            angle = random.randint(-400, 400)
            target_color = random.choice(color_levels)
            kf_name = f"c{cell_idx}"
            keyframes_css.append(f"""@keyframes {kf_name} {{
    from {{ transform: rotate({angle}deg) }}
    60% {{ transform: rotate(0deg) }}
    to {{ fill: var({target_color}) }}
}}
.c.{kf_name} {{ animation-name: {kf_name} }}""")
            cell_class_map[(col, row)] = kf_name
            cell_idx += 1

# Build SVG
lines = []
lines.append(f'<svg width="{svg_w}" height="{svg_h}" class="js-calendar-graph-svg" xmlns="http://www.w3.org/2000/svg">')
lines.append('<style>')
lines.append("""    :root {
        --c0: rgba(27, 31, 35, 0.06);
        --c1: #9be9a8;
        --c2: #40c463;
        --c3: #30a14e;
        --c4: #216e39;
    }
    .o, .o[data-level="0"] {
        fill: var(--c0);
        shape-rendering: geometricPrecision;
        outline: 1px solid var(--c0);
        outline-offset: -1px
    }
    .c {
        animation-iteration-count: infinite;
        animation-duration: 5s;
    }""")
for kf in keyframes_css:
    lines.append(kf)
lines.append('</style>')

# Grid of cells
lines.append(f'<g transform="translate(15, 20)">')
for col in range(total_cols):
    lines.append(f'<g transform="translate({col * cell_gap}, 0)">')
    for row in range(rows):
        y = row * cell_gap
        if (col, row) in cell_class_map:
            cls = f'o c {cell_class_map[(col, row)]}'
        else:
            cls = 'o'
        lines.append(f'<rect width="{cell_w}" height="{cell_w}" x="0" y="{y}" data-level="0" rx="2" ry="2" class="{cls}"></rect>')
    lines.append('</g>')
lines.append('</g>')
lines.append('</svg>')

output_path = r'c:\Users\abdul\OneDrive\Documents\GitHub\Abdullah-Shahriar\gitartwork.svg'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'SVG generated: {svg_w}x{svg_h}')
print(f'Active cells: {cell_idx}')
print(f'Total grid: {total_cols}x{rows} = {total_cols * rows} cells')
