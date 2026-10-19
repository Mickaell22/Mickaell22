"""Genera docs/assets/banner.svg: hero animado del perfil (estilo "marquee").

Tres capas SMIL, sin JS ni servicios externos:
  - un destello que recorre el borde (stroke-dashoffset),
  - frases de rol que rotan con fade + deslizamiento vertical,
  - una cinta de tecnologias que se desplaza en bucle infinito.
GitHub anima SMIL dentro de <img>; donde se rasteriza se ve el primer frame.

Uso: python3 docs/build/render_banner.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "banner.svg"

NAME = "Mickaell Morán"
ROLES = [
    "Fullstack: de la base de datos a la app móvil",
    "Pasante de desarrollo en un ERP corporativo",
    "Co-fundador de un SaaS en producción",
    "IA aplicada: Whisper, LLMs y servidores MCP",
]
TECH = ["Python", "Django", "FastAPI", "NestJS", ".NET", "React", "Angular", "Next.js", "Flutter",
        "React Native", "PostgreSQL", "SQL Server", "Docker", "Linux", "Claude", "Whisper"]

W, H = 1000, 300
STEP = 3.2  # segundos por frase
ACC1, ACC2 = "#22d3ee", "#a78bfa"
SANS = "'Segoe UI','Inter','Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','DejaVu Sans Mono',Consolas,monospace"
CHAR = 15 * 0.6  # ancho por caracter de la mono a 15px


def roles():
    n, total = len(ROLES), STEP * len(ROLES)
    a = STEP / total  # fraccion del ciclo que ocupa cada frase
    kt = f"0;{a * 0.12:.4f};{a * 0.88:.4f};{a:.4f};1"
    out = []
    for i, text in enumerate(ROLES):
        out.append(
            f'<g opacity="{1 if i == 0 else 0}"><text x="{W / 2}" y="168" text-anchor="middle" font-family="{MONO}" '
            f'font-size="21" fill="#9fb0c8">{text}</text>'
            f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="{kt}" dur="{total}s" '
            f'begin="{i * STEP}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 14;0 0;0 0;0 -14;0 -14" '
            f'keyTimes="{kt}" dur="{total}s" begin="{i * STEP}s" repeatCount="indefinite"/></g>')
    return "\n".join(out)


def marquee():
    line = "   ·   ".join(TECH) + "   ·   "
    width = len(line) * CHAR
    txt = lambda x: (f'<text x="{x:.1f}" y="250" font-family="{MONO}" font-size="15" letter-spacing="0" '
                     f'fill="#5f6f8a">{line}</text>')
    return (f'<g clip-path="url(#band)" mask="url(#edges)"><g>{txt(0)}{txt(width)}{txt(2 * width)}'
            f'<animateTransform attributeName="transform" type="translate" from="0 0" to="{-width:.1f} 0" '
            f'dur="{width / 40:.1f}s" repeatCount="indefinite"/></g></g>')


def main():
    per = 2 * (W - 4 + H - 4)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{NAME} - {ROLES[0]}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0f17"/><stop offset="1" stop-color="#111827"/></linearGradient>
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f1f5f9"/><stop offset="0.55" stop-color="#e2e8f0"/><stop offset="1" stop-color="{ACC1}"/></linearGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{ACC1}"/><stop offset="1" stop-color="{ACC2}"/></linearGradient>
  <radialGradient id="halo" cx="0.5" cy="0.35" r="0.6"><stop offset="0" stop-color="{ACC2}" stop-opacity="0.22"/><stop offset="1" stop-color="{ACC2}" stop-opacity="0"/></radialGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="#1f2937"/></pattern>
  <clipPath id="band"><rect x="40" y="226" width="{W - 80}" height="36"/></clipPath>
  <linearGradient id="fade" x1="40" y1="0" x2="{W - 40}" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.1" stop-color="#fff"/><stop offset="0.9" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <mask id="edges"><rect x="40" y="226" width="{W - 80}" height="36" fill="url(#fade)"/></mask>
</defs>
<rect width="{W}" height="{H}" rx="22" fill="url(#bg)"/>
<rect width="{W}" height="{H}" rx="22" fill="url(#dots)"/>
<rect width="{W}" height="{H}" rx="22" fill="url(#halo)"/>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="20" fill="none" stroke="#1e293b" stroke-width="2"/>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="20" fill="none" stroke="url(#sweep)" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="260 {per - 260}">
  <animate attributeName="stroke-dashoffset" from="0" to="{-per}" dur="9s" repeatCount="indefinite"/>
</rect>
<circle cx="{W / 2 - 92}" cy="58" r="5" fill="#22c55e"><animate attributeName="opacity" values="1;0.25;1" dur="2s" repeatCount="indefinite"/></circle>
<text x="{W / 2 + 8}" y="63" text-anchor="middle" font-family="{MONO}" font-size="14" letter-spacing="3" fill="#7d8aa3">GUAYAQUIL, EC</text>
<text x="{W / 2}" y="126" text-anchor="middle" font-family="{SANS}" font-size="62" font-weight="800" fill="url(#name)">{NAME}</text>
{roles()}
<line x1="40" y1="212" x2="{W - 40}" y2="212" stroke="#1e293b"/>
{marquee()}
</svg>
'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    # ponytail: check minimo, ninguna frase debe pasarse del ancho util
    assert max(len(r) for r in ROLES) * 21 * 0.6 < W - 80, "frase de rol demasiado larga"
    print(OUT)


if __name__ == "__main__":
    main()
