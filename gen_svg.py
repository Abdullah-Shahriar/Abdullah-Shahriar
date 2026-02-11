import random

# SMIL animations (no CSS!) - GitHub strips <style> but allows <animate>/<animateTransform>
letters = {
    'S': [[1,1,1,1],[1,0,0,0],[1,1,1,1],[0,0,0,1],[1,1,1,1]],
    'H': [[1,0,0,1],[1,0,0,1],[1,1,1,1],[1,0,0,1],[1,0,0,1]],
    'A': [[0,1,1,0],[1,0,0,1],[1,1,1,1],[1,0,0,1],[1,0,0,1]],
    'R': [[1,1,1,0],[1,0,0,1],[1,1,1,0],[1,0,1,0],[1,0,0,1]],
    'I': [[1,1,1],[0,1,0],[0,1,0],[0,1,0],[1,1,1]],
}

word = 'SHAHRIAR'
letter_gap = 2
cell_positions = []
col_offset = 0

for ch in word:
    lt = letters[ch]
    cols = len(lt[0])
    for row in range(5):
        for col in range(cols):
            if lt[row][col]:
                cell_positions.append((col_offset + col, row, ch))
    col_offset += cols + letter_gap

total_cols = col_offset - letter_gap
cell_size = 11
gap = 2
pitch = cell_size + gap
pad_x = 25
pad_y = 25
svg_w = total_cols * pitch - gap + 2 * pad_x
svg_h = 5 * pitch - gap + 2 * pad_y + 35

lines = []
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">')
lines.append(f'  <rect width="{svg_w}" height="{svg_h}" fill="#0d1117" rx="6"/>')

random.seed(42)
colors = ['#39d353', '#26a641', '#006d32', '#39d353', '#26a641', '#39d353']

total = len(cell_positions)
for i, (cx, cy, ch) in enumerate(cell_positions):
    x = pad_x + cx * pitch
    y = pad_y + cy * pitch
    color = random.choice(colors)
    dx = random.randint(-200, 200)
    dy = random.randint(-150, 150)
    delay = round(0.02 * i + random.uniform(0, 0.3), 2)
    dur = "1.5s"
    begin = f"{delay}s"

    lines.append(f'  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{color}" opacity="0">')
    # Fade in
    lines.append(f'    <animate attributeName="opacity" from="0" to="1" dur="{dur}" begin="{begin}" fill="freeze"/>')
    # Gather from random position to final position
    lines.append(f'    <animateTransform attributeName="transform" type="translate" from="{dx} {dy}" to="0 0" dur="{dur}" begin="{begin}" fill="freeze"/>')
    lines.append(f'  </rect>')

# Decorative scattered dots at the bottom
dec_y = pad_y + 5 * pitch + 12
for i in range(total_cols):
    x = pad_x + i * pitch
    if random.random() < 0.45:
        c = random.choice(['#0e4429', '#161b22', '#0e4429'])
        op = round(random.uniform(0.15, 0.45), 2)
        lines.append(f'  <rect x="{x}" y="{dec_y}" width="9" height="9" rx="2" fill="{c}" opacity="{op}"/>')

lines.append('</svg>')

output_path = r'c:\Users\abdul\OneDrive\Documents\GitHub\Abdullah-Shahriar\gitartwork.svg'
with open(output_path, 'w') as f:
    f.write('\n'.join(lines))

print(f'SVG generated: {svg_w}x{svg_h}, {len(cell_positions)} cells')
