# Builds the web-ready gallery photos in assets/img/gallery/ from the camera
# originals in assets/img/.  Run:  python tools/make-photo-assets.py
# Needs: pillow
#
# The originals are 13-16 MB PNGs and .JPGs straight off a phone, several stored
# sideways with an EXIF rotation flag. For each selected photo this writes:
#   <slug>-thumb.jpg   600x600 square, for the gallery grid
#   <slug>.jpg         1400px long edge, uncropped, for the lightbox
#
# FOCUS is the vertical anchor for the square crop (0 = top, 1 = bottom).
# Tune it per photo when the subject isn't centred.

from PIL import Image, ImageOps
import pathlib

IMG = pathlib.Path(__file__).resolve().parent.parent / "assets" / "img"
OUT = IMG / "gallery"
OUT.mkdir(exist_ok=True)

#        source filename                                  slug                 focus
PHOTOS = [
    # Landscape: focus shifts the crop right, off the treehouse and onto the
    # lawn, hedge and beehives.
    ("011 AP Backyard South with Bee Hives.JPG",          "backyard-treehouse",   0.70),
    ("016 AP School Bed with Painted Picket Fence.jpeg",   "painted-picket-fence", 0.50),
    ("040 AP Child Pruning.png",                           "child-pruning",        0.35),
    ("007 AP Watercolor Hearts.png",                       "watercolor-hearts",    0.50),
    ("022 AP Older Student Cat Art.png",                   "cat-painting",         0.40),
    ("042 AP Fall Garden Baskets.png",                     "fall-baskets",         0.50),
    ("023 AP Garden Basket w Seeds.jpeg",                  "garden-basket",        0.50),
    ("031 AP Fresh Bread.png",                             "fresh-bread",          0.50),
    ("046 AP Carrots and Hummus.png",                      "carrots-hummus",       0.50),
    ("045 AP Stump with Flower.png",                       "stump-flower",         0.45),
    ("020 AP Sunny Squash.jpeg",                           "sunny-squash",         0.50),
    ("037 AP Squirrel.png",                                "squirrel",             0.45),
    ("044 Fall White Pumpkin with Colored Wax.png",        "wax-pumpkin",          0.50),
]

THUMB, LARGE = 600, 1400


def square(im, focus):
    """Square crop anchored along whichever axis actually gets cropped.

    focus 0 = left / top edge, 0.5 = centred, 1 = right / bottom edge.
    A landscape photo is cropped horizontally, a portrait one vertically, so
    one knob serves both. 0.5 reproduces a plain centre crop.
    """
    w, h = im.size
    s = min(w, h)
    if w >= h:
        left, top = int((w - s) * focus), 0
    else:
        left, top = 0, int((h - s) * focus)
    return im.crop((left, top, left + s, top + s))


def main():
    total_in = total_out = 0
    for name, slug, focus in PHOTOS:
        src = IMG / name
        if not src.exists():
            print(f"  MISSING: {name}")
            continue
        total_in += src.stat().st_size

        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")  # bake rotation in

        t = square(im, focus).resize((THUMB, THUMB), Image.LANCZOS)
        t.save(OUT / f"{slug}-thumb.jpg", "JPEG", quality=82, optimize=True, progressive=True)

        big = im.copy()
        big.thumbnail((LARGE, LARGE), Image.LANCZOS)   # uncropped, long edge capped
        big.save(OUT / f"{slug}.jpg", "JPEG", quality=84, optimize=True, progressive=True)

        out = (OUT / f"{slug}-thumb.jpg").stat().st_size + (OUT / f"{slug}.jpg").stat().st_size
        total_out += out
        print(f"  {slug:22} {im.size[0]}x{im.size[1]} -> thumb+large {out/1024:5.0f} KB")

    print(f"\noriginals {total_in/1048576:6.1f} MB  ->  web {total_out/1048576:.1f} MB"
          f"  ({total_in/max(total_out,1):.0f}x smaller)")


if __name__ == "__main__":
    main()
