"""Genera las portadas de proyecto (docs/assets/cover-*.png) del README de perfil.

Cada portada: tag, nombre, una frase y chips de stack a la izquierda; a la
derecha la captura REAL del proyecto (si existe) o una composicion con los
iconos de su stack. Todo el texto sale de los README de cada repo: no inventar.

Capturas: se leen de los repos hermanos en disco. La carpeta base se pasa por
env PROJECTS_DIR (default: el padre de este repo).

Uso: python3 docs/build/render_covers.py
"""
import os
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OUT = ROOT.parent / "assets"
PROJECTS = Path(os.environ.get("PROJECTS_DIR", REPO.parent))
FONTS = Path("/usr/share/fonts/truetype/noto")

W, H = 1200, 680
BG = (11, 15, 23)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


F_TAG = font("NotoSansMono-Bold.ttf", 22)
F_TITLE = font("NotoSans-Black.ttf", 70)
F_TEXT = font("NotoSans-Medium.ttf", 32)
F_CHIP = font("NotoSans-SemiBold.ttf", 24)

COVERS = [
    dict(slug="facilito", accent="#22c55e", tag="SAAS · EN PRODUCCIÓN", title="Facilito",
         text="SaaS multitenant para negocios gastronómicos, con un asistente IA que entiende texto, audio y fotos de facturas.",
         chips=["Django", "DRF", "Flutter", "PostgreSQL", "Claude"],
         icons=["django", "flutter", "postgresql", "anthropic"]),
    dict(slug="restoventas", accent="#f97316", tag="APP + PANEL + INFRA", title="RestoVentas",
         text="El mesero dicta el pedido: Whisper lo transcribe y un LLM lo arma, saneado contra el catálogo real.",
         chips=["NestJS", "React Native", "Angular", "Docker"],
         desktop="RestoPanel/docs/img/dashboard-oscuro.png",
         phone="RestoVentas/restoventas-app/docs/screenshots/nueva-venta.png"),
    dict(slug="mcp", accent="#8b5cf6", tag="OPEN SOURCE · HERRAMIENTA PROPIA", title="mcp-context-server",
         text="Memoria semántica de repos para Claude Code: busca con ChromaDB y comprime con DeepSeek antes del contexto.",
         chips=["Python", "ChromaDB", "PostgreSQL", "MCP"],
         desktop="mcp-dashboard/docs/screenshots/dashboard.png", crop=(0, 0, 1100, 640)),
    dict(slug="tiaglenda", accent="#06b6d4", tag="CLIENTE REAL · ENTREGADO", title="Tía Glenda",
         text="Gestión clínica multi-rol y multi-centro: ~130 componentes React y 23 suites de tests.",
         chips=["React", "MUI", "Flask", "PostgreSQL"],
         icons=["react", "flask", "postgresql", "pytest"]),
    dict(slug="motovox", accent="#ef4444", tag="TIEMPO REAL · AUDIO P2P", title="MotoVox",
         text="Intercomunicador para motos: audio P2P por WiFi con sockets TCP y filtro de ruido en C nativo vía FFI.",
         chips=["Flutter", "Dart", "C / FFI", "NDK"],
         waveform=True, icons=["flutter"]),
    dict(slug="facturador", accent="#3b82f6", tag="EN PRODUCCIÓN · NOVAMICKTOOLS", title="Facturador",
         text="Pedidos grupales, clientes y facturación: login con Google, exportación a Excel y enlaces públicos por token.",
         chips=["FastAPI", "SQLAlchemy", "React", "PostgreSQL"],
         icons=["fastapi", "react", "postgresql", "tailwindcss"]),
    dict(slug="surco", accent="#e8762c", tag="ANDROID · APK PUBLICADO", title="Surco",
         text="Reproductor de música local sin cuentas ni anuncios: letras sincronizadas, estadísticas y listas que se arman solas.",
         chips=["Flutter", "Dart", "just_audio", "Android"],
         phones=["Surco/docs/screenshots/listas.png", "Surco/docs/screenshots/configuracion.png"]),
]


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def glow(img, accent):
    """Mancha de color difusa detras de la parte visual."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((620, 40, 1260, 680), fill=hex_rgb(accent) + (95,))
    d.ellipse((-200, 480, 300, 900), fill=hex_rgb(accent) + (40,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(120)))


def rounded(im, r):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *im.size), r, fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def shadowed(img, im, xy, r=18):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((xy[0] + 6, xy[1] + 14, xy[0] + im.width + 6, xy[1] + im.height + 14),
                                         r, fill=(0, 0, 0, 170))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(rounded(im, r), xy)


def browser(shot, width, crop=None):
    """Captura de escritorio dentro de un marco de navegador minimo."""
    im = Image.open(PROJECTS / shot).convert("RGBA")
    if crop:
        im = im.crop(crop)
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    bar = 34
    frame = Image.new("RGBA", (width, im.height + bar), (28, 33, 44, 255))
    d = ImageDraw.Draw(frame)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((14 + i * 22, 11, 26 + i * 22, 23), fill=c)
    frame.paste(im, (0, bar))
    return frame


def phone(shot, height):
    im = Image.open(PROJECTS / shot).convert("RGBA")
    im = im.resize((int(im.width * height / im.height), height), Image.LANCZOS)
    b = 10
    frame = Image.new("RGBA", (im.width + 2 * b, im.height + 2 * b), (20, 22, 28, 255))
    frame.alpha_composite(rounded(im, 26), (b, b))
    return frame


def icon_png(slug, size, color):
    svg = (ROOT / "icons" / f"{slug}.svg").read_text().replace("<svg ", f'<svg fill="{color}" ', 1)
    with tempfile.TemporaryDirectory() as t:
        src, dst = Path(t) / "i.svg", Path(t) / "i.png"
        src.write_text(svg)
        subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), str(src), "-o", str(dst)], check=True)
        return Image.open(dst).convert("RGBA")


def icon_tiles(img, slugs, accent):
    pos = [(690, 120), (930, 170), (720, 360), (960, 410)][:len(slugs)]
    for (x, y), slug in zip(pos, slugs):
        tile = Image.new("RGBA", (190, 190), (22, 28, 40, 255))
        d = ImageDraw.Draw(tile)
        d.rounded_rectangle((0, 0, 189, 189), 40, outline=hex_rgb(accent) + (140,), width=3)
        tile.alpha_composite(icon_png(slug, 104, "#e6edf3"), (43, 43))
        shadowed(img, tile, (x, y), 40)


def waveform(img, accent):
    d = ImageDraw.Draw(img)
    import math
    cx, cy = 900, 340
    for i in range(46):
        x = 650 + i * 11
        amp = 30 + 140 * abs(math.sin(i * 0.45)) * math.exp(-((i - 23) ** 2) / 260)
        d.rounded_rectangle((x, cy - amp, x + 6, cy + amp), 3, fill=hex_rgb(accent) + (230,))


def wrap(text, f, width, d):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def render(c):
    img = Image.new("RGBA", (W, H), BG + (255,))
    glow(img, c["accent"])
    acc = hex_rgb(c["accent"])

    if "desktop" in c:
        shadowed(img, browser(c["desktop"], 600 if "phone" in c else 560, c.get("crop")), (620, 120 if "phone" in c else 150), 14)
    if "phone" in c:
        shadowed(img, phone(c["phone"], 460), (915, 190), 30)
    for i, p in enumerate(c.get("phones", [])):
        shadowed(img, phone(p, 480), (690 + i * 235, 60 + i * 100), 30)
    if c.get("waveform"):
        waveform(img, c["accent"])
    if "icons" in c and not c.get("waveform"):
        icon_tiles(img, c["icons"], c["accent"])

    # columna de texto sobre un velo para que nunca compita con la captura
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    for x in range(640):
        a = 255 if x < 560 else int(255 * (640 - x) / 80)
        vd.line((x, 0, x, H), fill=BG + (a,))
    img.alpha_composite(veil)

    d = ImageDraw.Draw(img)
    pill = tuple(int(b * 0.82 + a * 0.18) for a, b in zip(acc, BG))  # mezcla a mano: ImageDraw no compone alfa
    d.rounded_rectangle((60, 70, 60 + d.textlength(c["tag"], font=F_TAG) + 36, 116), 23,
                        fill=pill, outline=acc, width=2)
    d.text((78, 79), c["tag"], font=F_TAG, fill=acc)
    f_title = F_TITLE
    while d.textlength(c["title"], font=f_title) > 520:  # nombres largos: achicar hasta que entren
        f_title = font("NotoSans-Black.ttf", f_title.size - 4)
    d.text((58, 150 + (70 - f_title.size)), c["title"], font=f_title, fill=(240, 244, 250))
    d.rectangle((62, 262, 142, 268), fill=acc)
    y = 300
    for line in wrap(c["text"], F_TEXT, 490, d):
        d.text((62, y), line, font=F_TEXT, fill=(170, 182, 202))
        y += 45
    x, y = 62, 560
    for chip in c["chips"]:
        w = d.textlength(chip, font=F_CHIP) + 36
        if x + w > 600:
            x, y = 62, y + 56
        d.rounded_rectangle((x, y, x + w, y + 44), 22, fill=(26, 32, 46), outline=(52, 62, 82), width=2)
        d.text((x + 18, y + 7), chip, font=F_CHIP, fill=(214, 222, 235))
        x += w + 12
    assert y < H - 50, f"chips desbordados en {c['slug']}"

    out = rounded(img.convert("RGBA"), 28)
    OUT.mkdir(parents=True, exist_ok=True)
    out.save(OUT / f"cover-{c['slug']}.png", optimize=True)
    print("ok", c["slug"])


if __name__ == "__main__":
    for cover in COVERS:
        render(cover)
