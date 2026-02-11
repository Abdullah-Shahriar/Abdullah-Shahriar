import random

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
lines.append('  <defs>')
lines.append('    <style>')
lines.append('      @keyframes gather {')
lines.append('        0% { opacity: 0; transform: translate(var(--dx), var(--dy)) scale(0.2) rotate(var(--r)); }')
lines.append('        40% { opacity: 0.6; }')
lines.append('        70% { transform: translate(calc(var(--dx)*0.05), calc(var(--dy)*0.05)) scale(1.08) rotate(0deg); }')
lines.append('        100% { opacity: 1; transform: translate(0,0) scale(1) rotate(0deg); }')
lines.append('      }')
lines.append('      @keyframes pulse {')
lines.append('        0%, 100% { opacity: 1; }')
lines.append('        50% { opacity: 0.75; }')
lines.append('      }')
lines.append('      .c {')
lines.append('        animation: gather 2s cubic-bezier(0.22, 1, 0.36, 1) forwards,')
lines.append('                   pulse 4s ease-in-out 2.5s infinite;')
lines.append('        opacity: 0;')
lines.append('      }')
lines.append('    </style>')
lines.append('  </defs>')
lines.append(f'  <rect width="{svg_w}" height="{svg_h}" fill="#0d1117" rx="6"/>')

random.seed(42)
colors = ['#39d353', '#26a641', '#006d32', '#39d353', '#26a641', '#39d353']

for i, (cx, cy, ch) in enumerate(cell_positions):
    x = pad_x + cx * pitch
    y = pad_y + cy * pitch
    color = random.choice(colors)
    dx = random.randint(-120, 120)
    dy = random.randint(-90, 90)
    rot = random.randint(-180, 180)
    delay = round(0.03 * i + random.uniform(0, 0.4), 3)
    style = f"--dx:{dx}px;--dy:{dy}px;--r:{rot}deg;animation-delay:{delay}s"
    lines.append(f'  <rect class="c" x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{color}" style="{style}"/>')

# Decorative scattered dots
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
