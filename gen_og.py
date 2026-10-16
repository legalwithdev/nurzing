from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1200, 630
TEAL_DARK = (6, 42, 40)      # #062A28
TEAL_MID  = (10, 64, 60)     # #0A403C
TEAL_600  = (14, 82, 76)
GOLD      = (217, 183, 97)   # #D9B761
GOLD_DEEP = (198, 156, 66)   # #C69C42
CREAM     = (251, 248, 241)
MUTED     = (168, 199, 193)

img = Image.new("RGB", (W, H), TEAL_DARK)
d = ImageDraw.Draw(img)

# vertical gradient
for y in range(H):
    t = y / (H - 1)
    r = int(TEAL_DARK[0] + (TEAL_MID[0]-TEAL_DARK[0]) * t)
    g = int(TEAL_DARK[1] + (TEAL_MID[1]-TEAL_DARK[1]) * t)
    b = int(TEAL_DARK[2] + (TEAL_MID[2]-TEAL_DARK[2]) * t)
    d.line([(0, y), (W, y)], fill=(r, g, b))

# soft gold glow (radial) top-right
glow = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(glow)
cx, cy, rad = 985, 120, 360
for i in range(rad, 0, -6):
    a = int(46 * (1 - i/rad) ** 2)
    gd.ellipse([cx-i, cy-i, cx+i, cy+i], fill=a)
glow_img = Image.new("RGB", (W, H), GOLD)
img = Image.composite(glow_img, img, glow.point(lambda v: min(v, 255)))
d = ImageDraw.Draw(img)

serif_b = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
serif   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
sans    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
sans_b  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f_mark  = ImageFont.truetype(serif_b, 54)
f_brand = ImageFont.truetype(serif_b, 92)
f_tag   = ImageFont.truetype(serif, 44)
f_sub   = ImageFont.truetype(sans, 27)
f_foot  = ImageFont.truetype(sans_b, 24)

# ---- logo mark (gold ring + N) ----
mx, my, mr = 96, 92, 34
d.ellipse([mx-mr, my-mr, mx+mr, my+mr], outline=GOLD_DEEP, width=3)
d.text((mx, my+2), "N", font=f_mark, fill=GOLD, anchor="mm")

# ---- brand wordmark ----
d.text((96, 170), "NURZING", font=f_brand, fill=CREAM)

# gold rule
d.line([(98, 300), (98+150, 300)], fill=GOLD, width=5)

# ---- tagline ----
d.text((96, 330), "Nurses and attendants at your doorstep.", font=f_tag, fill=CREAM)
d.text((96, 402), "Home nursing  \u00b7  Elderly care  \u00b7  Post-surgical care", font=f_sub, fill=MUTED)

# ---- footer band ----
d.line([(96, 520), (W-96, 520)], fill=(255, 255, 255, 30), width=1)
d.text((96, 548), "nurzing.pages.dev", font=f_foot, fill=GOLD)

img.save("public/og-image.png", "PNG", optimize=True)
print("wrote public/og-image.png", img.size)
