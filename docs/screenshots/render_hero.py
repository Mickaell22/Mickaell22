#!/usr/bin/env python3
"""Hero de terminal del perfil. Adaptado de readme-chulo/assets/render_terminal.py.
Todos los datos salen del CV / de la API de GitHub — no inventar nada aqui.
    python3 docs/screenshots/render_hero.py
Requiere Pillow. Sin deps de red."""
from PIL import Image, ImageDraw, ImageFont

# ------- CONFIG (datos REALES: CV + api.github.com/users/Mickaell22) -------
OUT = "docs/screenshots/hero.png"
PROMPT = [("$ ", "cyan"), ("mickaell ", "white"), ("▸ ", "cyan"), ("whoami", "green")]
BOX_TITLE = " Mickaell Morán Vera "
BOX_LINE1 = [("Fullstack Developer", "fg"), ("   ·   ", "magenta"), ("Guayaquil, Ecuador", "fg")]
BOX_LINE2 = "Ing. de Software, 9no semestre · GPA 8.98/10 · Universidad de Guayaquil"
BOX_LINE3 = "Co-founder de EcuaInventario · Freelance desde 2025 · Inglés B2"
COL_HEADERS = ("Área", "Stack")
ROWS = [
    ("backend",   "Python · Django · FastAPI · Node.js · Express · C# · Java"),
    ("frontend",  "React · Next.js · TypeScript · Tailwind CSS · Vite"),
    ("mobile",    "Flutter · Dart · Riverpod · Firebase"),
    ("data",      "PostgreSQL · SQLAlchemy · Alembic · Firestore · SQLite"),
    ("infra",     "Docker · Railway · Git · Linux · Postman"),
    ("security",  "Kali Linux · Nmap · Wireshark"),
]
SHOWN = 13
REST_LABEL = "… y {n} más"
TOTAL = len(ROWS)
FOOTER = "52 repos públicos · certificados Google de Cybersecurity y UX Design en curso"
# --------------------------------------------------

C = {"bg": "#0d0d0f", "fg": "#e6edf3", "dim": "#6e7681", "cyan": "#39d3e8",
     "green": "#3fdd78", "magenta": "#e05fd8", "white": "#f0f6fc"}
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
PAD, LH, FS, W = 70, 46, 30, 1640
# ponytail: columna 2 fija a la izquierda (no W-360 como el asset original):
# aqui la col B es la larga, asi que el corte va despues de la etiqueta corta.
COL2 = 400

def fnt(sz, bold=False):
    return ImageFont.truetype(MONO_B if bold else MONO, sz)

# ponytail: se dibuja en un lienzo holgado y al final se recorta a la altura
# real usada (y_final + PAD). Mas simple que predecir n_lines a mano.
img = Image.new("RGB", (W, 2000), C["bg"]); d = ImageDraw.Draw(img)
base, bold = fnt(FS), fnt(FS, True)

for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
    d.ellipse([60 + i*46, 55, 90 + i*46, 85], fill=c)

def line(segs, yy, f, x0=PAD):
    x = x0
    for text, col in segs:
        d.text((x, yy), text, font=f, fill=C.get(col, col)); x += d.textlength(text, font=f)

y = 150
line(PROMPT, y, bold); y += LH*2

bx0, bx1, by0 = PAD, W-PAD, y
tw = d.textlength(BOX_TITLE, font=bold); tcx = (bx0+bx1)/2 - tw/2
d.line([bx0+16, by0, tcx-12, by0], fill=C["magenta"], width=2)
d.line([tcx+tw+12, by0, bx1-16, by0], fill=C["magenta"], width=2)
d.text((tcx, by0-FS//2-2), BOX_TITLE, font=bold, fill=C["magenta"])
iy, ip = by0+28, PAD+22
line(BOX_LINE1, iy, base, ip)
line([(BOX_LINE2, "dim")], iy+LH, base, ip)
line([(BOX_LINE3, "dim")], iy+LH*2, base, ip)
by1 = iy + LH*3 + 8
for seg in ([bx0, by0, bx0, by1], [bx1, by0, bx1, by1], [bx0, by1, bx1, by1]):
    d.line(seg, fill=C["magenta"], width=2)
y = by1 + LH*2

line([(COL_HEADERS[0], "cyan")], y, bold)
d.text((COL2, y), COL_HEADERS[1], font=bold, fill=C["cyan"]); y += LH-8
d.line([PAD, y, W-PAD, y], fill="#30363d", width=3); y += 14
for a, b in ROWS[:SHOWN]:
    d.text((PAD, y), a, font=base, fill=C["fg"]); d.text((COL2, y), b, font=base, fill=C["green"]); y += LH
rest = TOTAL - min(SHOWN, len(ROWS))
if rest > 0:
    d.text((PAD, y), REST_LABEL.format(n=rest), font=base, fill=C["dim"]); y += LH
y += LH
line([("  " + FOOTER, "dim")], y, base)

img.crop((0, 0, W, y + FS + PAD)).save(OUT, "PNG"); print("OK ->", OUT)
