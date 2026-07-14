import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'public/backgrounless2.png'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'public/source-prepped.png'

    print(f"[prep] Loading {input_file} ...")
    try:
        img = Image.open(input_file).convert('RGBA')
    except Exception as e:
        print(f"[prep] Error: {e}")
        return

    # Composite transparent PNG onto a solid black background
    print("[prep] Compositing transparent image onto black background...")
    black_bg = Image.new('RGBA', img.size, (0, 0, 0, 255))
    img = Image.alpha_composite(black_bg, img).convert('RGB')

    # Convert to OpenCV format (BGR) for contrast enhancement
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    print("[prep] Applying CLAHE ...")
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    print("[prep] Contrast stretch ...")
    enhanced = cv2.normalize(enhanced, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    # Convert back to PIL
    final_img = Image.fromarray(enhanced)

    # Crop out pure black margins automatically
    print("[prep] Cropping ...")
    bbox = final_img.point(lambda p: 255 if p > 5 else 0).getbbox()
    if bbox:
        margin = 15
        l = max(0, bbox[0] - margin)
        t = max(0, bbox[1] - margin)
        r = min(final_img.width, bbox[2] + margin)
        b = min(final_img.height, bbox[3] + margin)
        final_img = final_img.crop((l, t, r, b))

    # Optional slight sharpen
    final_img = final_img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=100))

    final_img.save(output_file)
    print(f"[prep] Output: {final_img.size[0]}x{final_img.size[1]} px -> {output_file}")

if __name__ == '__main__':
    main()
