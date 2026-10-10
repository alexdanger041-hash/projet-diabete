from PIL import Image, ImageDraw

for s in (192, 512):
    im = Image.new("RGB", (s, s), "#1f4e79")
    d = ImageDraw.Draw(im)
    m = s // 4
    d.ellipse([m, m, s - m, s - m], fill="#ffffff")
    d.ellipse([s * 0.4, s * 0.4, s * 0.6, s * 0.6], fill="#d33a3a")
    im.save(f"frontend/public/icon-{s}.png")