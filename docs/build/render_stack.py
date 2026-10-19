"""Genera docs/assets/stack.svg: grilla de iconos del stack, agrupada por area.

Iconos de simple-icons (CC0) cacheados en docs/build/icons/, asi el SVG queda
autocontenido (paths embebidos, sin hotlink a ningun servicio).
Las marcas que simple-icons retiro (C#, Java, SQL Server, Playwright, OpenAI)
van como monograma de texto.

Uso: python3 docs/build/render_stack.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets" / "stack.svg"
COLORS = json.loads((ROOT / "icons" / "colors.json").read_text())

# (titulo de fila, [(slug o None, etiqueta, monograma si no hay icono)])
ROWS = [
    ("BACKEND", [("python", "Python", None), ("django", "Django", None), ("fastapi", "FastAPI", None),
                 ("flask", "Flask", None), ("nodedotjs", "Node.js", None), ("nestjs", "NestJS", None),
                 ("dotnet", ".NET", None), (None, "C#", "C#")]),
    ("FRONTEND", [("react", "React", None), ("nextdotjs", "Next.js", None), ("angular", "Angular", None),
                  ("typescript", "TypeScript", None), ("tailwindcss", "Tailwind", None), ("vite", "Vite", None)]),
    ("MÓVIL", [("flutter", "Flutter", None), ("dart", "Dart", None), ("react", "React Native", None),
               ("expo", "Expo", None), ("kotlin", "Kotlin", None)]),
    ("DATOS", [("postgresql", "PostgreSQL", None), (None, "SQL Server", "SQL"), ("mysql", "MySQL", None),
               ("prisma", "Prisma", None), ("typeorm", "TypeORM", None), ("sqlalchemy", "SQLAlchemy", None),
               ("firebase", "Firebase", None)]),
    ("INFRA", [("docker", "Docker", None), ("linux", "Linux", None), ("githubactions", "Actions", None),
               ("nginx", "nginx", None), ("caddy", "Caddy", None), ("cloudflare", "Cloudflare", None),
               ("railway", "Railway", None)]),
    ("IA Y TESTS", [("anthropic", "Claude", None), (None, "OpenAI", "AI"), ("pytest", "pytest", None),
                    ("jest", "Jest", None), ("vitest", "Vitest", None), (None, "Playwright", "PW")]),
]

W = 880
LABEL_W = 132
TILE = 58
GAP = 16
ROW_H = 96
PAD_Y = 30
BG, TILE_BG, TILE_BORDER = "#0b0f17", "#141a26", "#232b3b"
LABEL, NAME = "#7d8aa3", "#c9d1e0"
SANS = "'Segoe UI','Inter','Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','DejaVu Sans Mono',Consolas,monospace"


def luminance(hex_):
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def icon_path(slug):
    return re.search(r'<path d="([^"]+)"', (ROOT / "icons" / f"{slug}.svg").read_text()).group(1)


def tile(x, y, slug, name, mono):
    out = [f'<rect x="{x}" y="{y}" width="{TILE}" height="{TILE}" rx="14" fill="{TILE_BG}" stroke="{TILE_BORDER}"/>']
    if slug:
        color = "#" + COLORS[slug]
        lum = luminance(COLORS[slug])
        if lum < 0.18:  # marcas negras (Next, Prisma...) no se ven en fondo oscuro
            color = "#e6edf3"
        elif lum < 0.35:  # marcas oscuras (.NET, Flutter, MySQL): aclarar hacia blanco
            color = "#" + "".join(f"{int(int(COLORS[slug][i:i + 2], 16) * 0.45 + 255 * 0.55):02x}" for i in (0, 2, 4))
        s = 30 / 24
        out.append(f'<path transform="translate({x + (TILE - 30) / 2} {y + (TILE - 30) / 2}) scale({s})" '
                   f'fill="{color}" d="{icon_path(slug)}"/>')
    else:
        out.append(f'<text x="{x + TILE / 2}" y="{y + TILE / 2 + 7}" text-anchor="middle" font-family="{MONO}" '
                   f'font-size="19" font-weight="700" fill="#e6edf3">{mono}</text>')
    out.append(f'<text x="{x + TILE / 2}" y="{y + TILE + 17}" text-anchor="middle" font-family="{SANS}" '
               f'font-size="11.5" fill="{NAME}">{name}</text>')
    return "\n".join(out)


def main():
    h = PAD_Y * 2 + ROW_H * len(ROWS) - 18
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
             f'role="img" aria-label="Stack: ' + ", ".join(n for _, r in ROWS for _, n, _ in r) + '">',
             f'<rect width="{W}" height="{h}" rx="18" fill="{BG}"/>']
    for i, (label, items) in enumerate(ROWS):
        y = PAD_Y + i * ROW_H
        parts.append(f'<text x="32" y="{y + TILE / 2 + 4}" font-family="{MONO}" font-size="12" '
                     f'letter-spacing="2" fill="{LABEL}">{label}</text>')
        for j, (slug, name, mono) in enumerate(items):
            parts.append(tile(32 + LABEL_W + j * (TILE + GAP + 14), y, slug, name, mono))
    parts.append("</svg>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(parts), encoding="utf-8")
    # ponytail: check minimo, la fila mas larga tiene que caber en el ancho
    longest = max(len(r) for _, r in ROWS)
    assert 32 + LABEL_W + longest * (TILE + GAP + 14) - GAP - 14 <= W - 24, "fila desbordada"
    print(OUT)


if __name__ == "__main__":
    main()
