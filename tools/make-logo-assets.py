# Regenerates the logo assets in assets/img/ from the original PCGS Logo.jpg.
# Run with: python tools/make-logo-assets.py  (needs pillow + numpy)
# The source is a 500x500 lockup on a cream field: emblem (hand + seedling on a
# sage disc) above a "Pasadena Country / GARDEN SCHOOL" wordmark.
from PIL import Image
import pathlib, numpy as np

IMG = pathlib.Path(r"c:\Users\aphgo\OneDrive\Documents\01_Active_Projects\Pasadena Country Garden School\Pasadena Country Garden School V3\assets\img")
src = Image.open(IMG / "pcgs-logo.jpg").convert("RGB")
a = np.asarray(src).astype(np.int16)

CREAM = np.array([248, 255, 237])
# Distance from the cream field, per pixel.
dist = np.abs(a - CREAM).max(axis=2)

# Ramp to alpha so antialiased edges keep their softness instead of stair-stepping.
T0, T1 = 5.0, 20.0
alpha = np.clip((dist - T0) / (T1 - T0), 0, 1) * 255
alpha = alpha.astype(np.uint8)

rgba = np.dstack([np.asarray(src).astype(np.uint8), alpha])
out = Image.fromarray(rgba, "RGBA")

# --- work out where the emblem ends and the wordmark begins ---------------
rows = (alpha > 25).sum(axis=1)
nz = np.nonzero(rows)[0]
print("content rows:", nz.min(), "->", nz.max())
# find the widest empty band between emblem and wordmark
gaps, run = [], None
for y in range(nz.min(), nz.max() + 1):
    if rows[y] == 0:
        run = y if run is None else run
    elif run is not None:
        gaps.append((y - run, run, y)); run = None
print("gaps (len, start, end):", gaps)
# The emblem/wordmark boundary is the FIRST gap. The largest gap is the one
# between the two wordmark lines ("Pasadena Country" / "GARDEN SCHOOL"), which
# would slice the wordmark in half instead.
first = min(gaps, key=lambda g: g[1])
split = first[1] + first[0] // 2
print("split row:", split)

def tight(img, box=None):
    im = img.crop(box) if box else img
    bb = im.getbbox()
    return im.crop(bb)

# Emblem only — for the header and footer, paired with HTML type.
mark = tight(out, (0, 0, 500, split))
mark.save(IMG / "logo-mark.png")
print("logo-mark.png ", mark.size)

# Full lockup — favicon / social / anywhere the whole logo belongs.
full = tight(out)
full.save(IMG / "logo-full.png")
print("logo-full.png ", full.size)

# Square favicon from the emblem, padded so it isn't cropped by rounding.
side = max(mark.size)
fav = Image.new("RGBA", (side, side), (0, 0, 0, 0))
fav.paste(mark, ((side - mark.width) // 2, (side - mark.height) // 2), mark)
fav.resize((180, 180), Image.LANCZOS).save(IMG / "favicon-180.png")
fav.resize((32, 32), Image.LANCZOS).save(IMG / "favicon-32.png")
print("favicons written")

# Open Graph card: 1200x630, logo centred on the brand cream.
og = Image.new("RGB", (1200, 630), (248, 255, 237))
h = 520
w = round(full.width * h / full.height)
og.paste(full.resize((w, h), Image.LANCZOS), ((1200 - w) // 2, (630 - h) // 2), full.resize((w, h), Image.LANCZOS))
og.save(IMG / "og-card.jpg", quality=88)
print("og-card.jpg   ", og.size)
