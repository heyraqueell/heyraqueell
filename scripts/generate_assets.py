#!/usr/bin/env python3
"""
Gera os SVGs do perfil (banner com chuva estilo Matrix + divisor).

Uso (a partir da raiz do repositório do perfil):
    python3 scripts/generate_assets.py

Saída:
    assets/matrix-banner.svg
    assets/divider.svg

Sem dependências externas (somente biblioteca padrão do Python 3).

Como o SVG funciona no GitHub:
  - O arquivo é usado via <img>, então o navegador NÃO executa scripts.
  - A chuva usa animação CSS e a digitação usa animação SMIL; ambas rodam
    dentro de SVG carregado como imagem.
  - Nenhuma fonte, imagem ou serviço externo é carregado.
  - Os textos do banner ficam todos nas constantes abaixo: edite aqui e
    gere de novo (a chuva é determinística, o resultado só muda se você
    mudar SEED ou as constantes).
"""

import random
from pathlib import Path
from xml.sax.saxutils import escape

# ----------------------------------------------------------------------------
# CONFIGURAÇÃO — edite aqui
# ----------------------------------------------------------------------------
NAME = "Raquel Oliveira"

# Linhas digitadas no terminal do banner.
# Mantenha-as curtas (cabem ~48 caracteres) e sempre verdadeiras.
LINE_1 = "> Estagiária de Cibersegurança (Red Team)"
LINE_2 = "> Eng. de Software | AWS | Cloud Security"

# Caracteres da chuva. Padrão: ASCII (aparece igual em qualquer sistema).
# Katakana dá o visual do filme, mas pode aparecer como "quadrados" em
# computadores sem fonte japonesa. Para testar, troque por:
#   CHARSET = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉ0123456789"
CHARSET = "01234567890123456789ABCDEFXZ<>:=+*|/\\"

SEED = 20261011          # muda o desenho da chuva
OUT_DIR = Path("assets")  # relativo à raiz do repositório

# ----------------------------------------------------------------------------
# PALETA (a mesma do README)
# ----------------------------------------------------------------------------
BG = "#050805"
GREEN = "#00FF41"
GREEN_MID = "#008F11"
GREEN_DIM = "#003B00"
TEXT = "#C9D1D9"
HEAD = "#D6FFE0"      # "cabeça" brilhante de cada coluna
FONT = 'ui-monospace, SFMono-Regular, Menlo, Consolas, "DejaVu Sans Mono", "Liberation Mono", monospace'

W, H = 1000, 320
CHAR_W = 0.6  # largura média de um caractere monoespaçado, em em


def rain_columns(rng: random.Random) -> str:
    """Colunas de caracteres caindo. Cada coluna é um <g> animado por CSS."""
    font = 15
    step = 17
    col_gap = 20
    parts = []
    n_cols = W // col_gap
    for i in range(n_cols):
        x = 10 + i * col_gap
        n = rng.randint(8, 16)
        dur = rng.uniform(7.0, 15.0)
        delay = -rng.uniform(0, dur)  # atraso negativo: já começa "no meio"
        chars = [rng.choice(CHARSET) for _ in range(n)]
        tspans = []
        for k, ch in enumerate(chars):
            # k = 0 é o topo (mais apagado); último é a cabeça (mais brilhante)
            if k == n - 1:
                cls = "h"
            else:
                bucket = min(5, int(k / max(1, n - 1) * 6))
                cls = f"o{bucket}"
            y_attr = f' y="{font}"' if k == 0 else ""
            dy_attr = "" if k == 0 else f' dy="{step}"'
            tspans.append(
                f'<tspan x="{x}"{y_attr}{dy_attr} class="{cls}">{escape(ch)}</tspan>'
            )
        parts.append(
            f'<g class="c" style="animation-duration:{dur:.1f}s;'
            f'animation-delay:{delay:.1f}s"><text>{"".join(tspans)}</text></g>'
        )
    return "\n".join(parts)


def typing_animation(text: str, font_px: int, start: float, per_char: float,
                     total: float, clip_id: str, x: float, y_top: float,
                     height: float) -> str:
    """
    Efeito de digitação: um clipPath cuja largura cresce caractere a caractere.

    A largura BASE do retângulo já é a final, então, se o navegador não
    suportar SMIL, o texto aparece completo (nunca fica invisível).
    O último valor da animação é bem largo para nunca cortar o texto, mesmo
    se a fonte do visitante for um pouco mais larga que o previsto.
    """
    n = len(text)
    cw = font_px * CHAR_W
    typing_time = n * per_char
    vals = [0.0]  # espera inicial com largura 0
    times = [0.0]
    # mantém largura 0 até `start`
    times.append(start / total)
    vals.append(0.0)
    for k in range(1, n + 1):
        t = (start + k * per_char) / total
        vals.append(round(k * cw, 1))
        times.append(min(t, 0.999))
    vals[-1] = 900.0  # garante que a última letra nunca seja cortada
    times.append(1.0)
    vals.append(900.0)
    return (
        f'<clipPath id="{clip_id}"><rect x="{x}" y="{y_top}" width="900" '
        f'height="{height}">'
        f'<animate attributeName="width" begin="0s" dur="{total}s" '
        f'calcMode="discrete" fill="freeze" '
        f'values="{";".join(str(v) for v in vals)}" '
        f'keyTimes="{";".join(f"{t:.4f}" for t in times)}"/>'
        f"</rect></clipPath>"
    )


def build_banner() -> str:
    rng = random.Random(SEED)
    rain = rain_columns(rng)

    # Cronograma da digitação (em segundos) — toca uma vez e permanece.
    total = 9.0
    t1_start, t2_start = 1.0, 3.6
    per_char = 0.05

    clip1 = typing_animation(LINE_1, 26, t1_start, per_char, total, "t1", 80, 170, 34)
    clip2 = typing_animation(LINE_2, 26, t2_start, per_char, total, "t2", 80, 204, 34)

    # Cursor final: aparece depois da digitação, pisca para sempre.
    cursor_begin = t2_start + len(LINE_2) * per_char + 0.2

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">{escape(NAME)}: terminal estilo Matrix</title>
<desc id="d">Banner com caracteres verdes caindo sobre fundo preto e uma janela de terminal com o nome {escape(NAME)} e as linhas: {escape(LINE_1)}; {escape(LINE_2)}.</desc>
<defs>
<style>
.c{{animation-name:fall;animation-timing-function:linear;animation-iteration-count:infinite}}
@keyframes fall{{from{{transform:translateY(-290px)}}to{{transform:translateY({H + 20}px)}}}}
text{{font-family:{FONT}}}
.rain text{{font-size:15px;fill:{GREEN}}}
.o0{{fill-opacity:.10}}.o1{{fill-opacity:.18}}.o2{{fill-opacity:.30}}
.o3{{fill-opacity:.45}}.o4{{fill-opacity:.62}}.o5{{fill-opacity:.80}}
.h{{fill:{HEAD};fill-opacity:.95}}
.prompt{{fill:{GREEN_MID};font-size:22px}}
.cmd{{fill:{GREEN};font-size:22px}}
.name{{fill:{GREEN};font-size:58px;font-weight:700;letter-spacing:1px}}
.line{{fill:{TEXT};font-size:26px}}
.title{{fill:{GREEN_MID};font-size:14px}}
.blink{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.c,.blink{{animation:none}}}}
</style>
<filter id="glow" x="-10%" y="-30%" width="120%" height="160%">
<feGaussianBlur stdDeviation="2.2" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
<rect width="4" height="1" fill="#000" opacity=".28"/>
</pattern>
<linearGradient id="vig" x1="0" x2="1" y1="0" y2="0">
<stop offset="0" stop-color="#000" stop-opacity=".55"/>
<stop offset=".18" stop-color="#000" stop-opacity="0"/>
<stop offset=".82" stop-color="#000" stop-opacity="0"/>
<stop offset="1" stop-color="#000" stop-opacity=".55"/>
</linearGradient>
{clip1}
{clip2}
<clipPath id="frame"><rect width="{W}" height="{H}" rx="10"/></clipPath>
</defs>

<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="{BG}"/>

<g class="rain" opacity=".85">
{rain}
</g>

<rect width="{W}" height="{H}" fill="url(#vig)"/>

<!-- janela de terminal: fundo semitransparente para manter a leitura -->
<rect x="60" y="30" width="880" height="262" rx="8" fill="{BG}" fill-opacity=".78" stroke="{GREEN}" stroke-opacity=".35"/>
<rect x="60" y="30" width="880" height="28" rx="8" fill="{GREEN_DIM}" fill-opacity=".55"/>
<rect x="60" y="48" width="880" height="10" fill="{GREEN_DIM}" fill-opacity=".55"/>
<circle cx="82" cy="44" r="4.5" fill="{GREEN_MID}"/>
<circle cx="100" cy="44" r="4.5" fill="{GREEN_MID}" fill-opacity=".6"/>
<circle cx="118" cy="44" r="4.5" fill="{GREEN_MID}" fill-opacity=".3"/>
<text class="title" x="500" y="49" text-anchor="middle">raquel@perfil: ~</text>

<text x="80" y="98"><tspan class="prompt">$ </tspan><tspan class="cmd">whoami</tspan></text>
<text class="name" x="80" y="156" filter="url(#glow)">{escape(NAME)}</text>

<g clip-path="url(#t1)"><text class="line" x="80" y="196">{escape(LINE_1)}</text></g>
<g clip-path="url(#t2)"><text class="line" x="80" y="230">{escape(LINE_2)}</text></g>

<text x="80" y="272"><tspan class="prompt">$ </tspan><tspan class="cmd blink">_</tspan></text>

<rect width="{W}" height="{H}" fill="url(#scan)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" stroke="{GREEN}" stroke-opacity=".25"/>
</svg>
'''


def build_divider() -> str:
    """Divisor fino e estático (não anima, para não cansar a leitura)."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 24" width="1000" height="24" role="img" aria-label="divisor">
<title>divisor</title>
<defs>
<linearGradient id="g" x1="0" x2="1" y1="0" y2="0">
<stop offset="0" stop-color="{GREEN}" stop-opacity="0"/>
<stop offset=".5" stop-color="{GREEN}" stop-opacity=".75"/>
<stop offset="1" stop-color="{GREEN}" stop-opacity="0"/>
</linearGradient>
</defs>
<rect width="1000" height="24" fill="{BG}"/>
<rect x="40" y="11.5" width="920" height="1" fill="url(#g)"/>
<rect x="488" y="9" width="6" height="6" fill="{GREEN}"/>
<rect x="500" y="9" width="6" height="6" fill="{GREEN}" fill-opacity=".55"/>
<rect x="512" y="9" width="6" height="6" fill="{GREEN}" fill-opacity=".25"/>
</svg>
'''


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    banner = OUT_DIR / "matrix-banner.svg"
    divider = OUT_DIR / "divider.svg"
    banner.write_text(build_banner(), encoding="utf-8")
    divider.write_text(build_divider(), encoding="utf-8")
    for p in (banner, divider):
        print(f"{p}  {p.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
