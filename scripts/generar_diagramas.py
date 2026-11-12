#!/usr/bin/env python3
"""Genera los diagramas didácticos del taller en img/.

Dependencia de desarrollo (no está en requirements.txt): matplotlib.
Este script no forma parte de la ejecución del taller ni del flujo de CI;
solo se usa al regenerar las figuras.

Instalación: pip install matplotlib

Uso (desde la raíz del repositorio):

    python scripts/generar_diagramas.py

Los PNG y SVG se escriben en img/. El script es determinista: misma entrada,
mismos archivos. Si están instaladas las fuentes Source Sans Pro, se usan;
si no, se recurre a DejaVu Sans (incluida con matplotlib).
Las consultas se dibujan en DejaVu Sans Mono.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, PathPatch
from matplotlib.path import Path as MplPath


# ---------------------------------------------------------------------------
# Estilo (colores tomados de la figura de referencia de cláusulas)
# ---------------------------------------------------------------------------

NAVY = "#3465A4"
NAVY_DARK = "#2A6099"
CRIMSON = "#BF0041"
GREEN = "#AFD095"
BLUE = "#B4C7DC"
YELLOW = "#E8F2A1"
WHITE = "#FFFFFF"
TEXT = "#1A1A1A"
LIGHT_GREY = "#F7F8FA"

FONT_CANDIDATES = [
    Path("/usr/share/fonts/truetype/sand-box/custom/Source Sans Pro"),
    Path("/usr/share/fonts/truetype/source-sans-pro"),
    Path("/usr/share/fonts/opentype/source-sans-pro"),
]

FAMILY = "DejaVu Sans"
FONT_REGULAR = font_manager.FontProperties(family="DejaVu Sans")
FONT_BOLD = font_manager.FontProperties(family="DejaVu Sans", weight="bold")
FONT_MONO = font_manager.FontProperties(family="DejaVu Sans Mono")
FONT_MONO_BOLD = font_manager.FontProperties(family="DejaVu Sans Mono", weight="bold")
MONO_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
MONO_BOLD_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf")
if MONO_PATH.is_file():
    font_manager.fontManager.addfont(str(MONO_PATH))
    FONT_MONO = font_manager.FontProperties(fname=str(MONO_PATH))
if MONO_BOLD_PATH.is_file():
    font_manager.fontManager.addfont(str(MONO_BOLD_PATH))
    FONT_MONO_BOLD = font_manager.FontProperties(fname=str(MONO_BOLD_PATH))


def _register_fonts() -> None:
    global FAMILY, FONT_REGULAR, FONT_BOLD
    for folder in FONT_CANDIDATES:
        regular = folder / "SourceSansPro-Regular.ttf"
        bold = folder / "SourceSansPro-Bold.ttf"
        if regular.is_file() and bold.is_file():
            font_manager.fontManager.addfont(str(regular))
            font_manager.fontManager.addfont(str(bold))
            FAMILY = font_manager.FontProperties(fname=str(regular)).get_name()
            FONT_REGULAR = font_manager.FontProperties(fname=str(regular))
            FONT_BOLD = font_manager.FontProperties(fname=str(bold))
            return


_register_fonts()

plt.rcParams.update(
    {
        "font.family": FAMILY,
        "text.color": TEXT,
        "svg.fonttype": "path",
        "axes.linewidth": 0,
        "figure.facecolor": WHITE,
        "savefig.facecolor": WHITE,
        "savefig.edgecolor": "none",
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.18,
        "savefig.dpi": 200,
    }
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "img"

# Tamaños en pulgadas del sistema de coordenadas (1 unidad = 1 pulgada).
CELL = 0.42
GAP = 0.09
HEAD_H = 0.78
RADIUS = 0.11
LW = 1.45
LW_HEAD = 1.55


# ---------------------------------------------------------------------------
# Primitivas de dibujo
# ---------------------------------------------------------------------------

def new_canvas(width: float, height: float):
    fig, ax = plt.subplots(figsize=(width, height), dpi=200)
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)
    return fig, ax


def rounded(ax, x, y, w, h, facecolor, edgecolor=NAVY, lw=LW, ls="-", zorder=2, radius=None):
    """Rectángulo redondeado; (x, y) es la esquina inferior izquierda."""
    r = RADIUS if radius is None else radius
    # rounding_size is in data coords; pad=0 so (x,y,w,h) is the outer box.
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=lw,
        linestyle=ls,
        mutation_aspect=1,
        zorder=zorder,
        joinstyle="round",
        capstyle="round",
    )
    ax.add_patch(patch)
    return patch


def cell(ax, cx, cy, text, fill=WHITE, edge=NAVY, lw=LW, size=None, fontsize=11, font=None, zorder=3):
    """Celda cuadrada centrada en (cx, cy) (centro)."""
    s = CELL if size is None else size
    rounded(ax, cx - s / 2, cy - s / 2, s, s, fill, edge, lw=lw, zorder=zorder)
    if text is not None and text != "":
        ax.text(
            cx,
            cy,
            str(text),
            ha="center",
            va="center",
            fontsize=fontsize,
            fontproperties=font or FONT_BOLD,
            color=TEXT,
            zorder=zorder + 1,
            clip_on=False,
        )


def header_box(ax, x, y, w, h, title, icons=None, fontsize=10.5):
    """Caja de cláusula. icons: lista de dicts {text, fill, edge} dibujados a la derecha, dentro de la caja."""
    rounded(ax, x, y, w, h, WHITE, NAVY, lw=LW_HEAD, radius=0.14, zorder=2)
    icons = icons or []
    icon_s = 0.20
    icon_gap = 0.045
    pad = 0.12
    stack = bool(icons) and (len(icons) >= 3 or any(ic.get("stack") for ic in icons))
    if stack:
        icons_w = icon_s
    elif icons:
        icons_w = len(icons) * icon_s + max(0, len(icons) - 1) * icon_gap
    else:
        icons_w = 0
    if icons:
        title_left = x + pad
        title_right = x + w - pad - icons_w - 0.08
        ax.text(
            (title_left + title_right) / 2,
            y + h / 2,
            title,
            ha="center",
            va="center",
            fontsize=fontsize,
            fontproperties=FONT_BOLD,
            color=TEXT,
            zorder=4,
            linespacing=1.05,
        )
        ix_right = x + w - pad - icon_s / 2
        if stack:
            total_h = len(icons) * icon_s + (len(icons) - 1) * 0.04
            iy = y + h / 2 + total_h / 2 - icon_s / 2
            for ic in icons:
                cell(
                    ax,
                    ix_right,
                    iy,
                    ic.get("text"),
                    fill=ic.get("fill", WHITE),
                    edge=ic.get("edge", NAVY),
                    lw=1.05,
                    size=icon_s,
                    fontsize=6.8,
                    zorder=4,
                )
                iy -= icon_s + 0.04
        else:
            ix = x + w - pad - icons_w + icon_s / 2
            for ic in icons:
                cell(
                    ax,
                    ix,
                    y + h / 2,
                    ic.get("text"),
                    fill=ic.get("fill", WHITE),
                    edge=ic.get("edge", NAVY),
                    lw=1.05,
                    size=icon_s,
                    fontsize=6.8,
                    zorder=4,
                )
                ix += icon_s + icon_gap
    else:
        ax.text(
            x + w / 2,
            y + h / 2,
            title,
            ha="center",
            va="center",
            fontsize=fontsize,
            fontproperties=FONT_BOLD,
            color=TEXT,
            zorder=4,
            linespacing=1.05,
        )


def dashed_box(ax, x, y, w, h, radius=0.14):
    rounded(ax, x, y, w, h, "none", NAVY, lw=1.35, ls=(0, (3.2, 2.2)), radius=radius, zorder=1.5)


def curly_brace(ax, x, y0, y1, depth=0.16, color=NAVY, lw=1.7, zorder=4):
    """Llave vertical que apunta a la derecha; el lomo está en x, la punta en x+depth."""
    if y1 < y0:
        y0, y1 = y1, y0
    ym = (y0 + y1) / 2
    d = depth
    # Cuatro cúbicas: gancho superior, curva hacia la punta, curva de salida, gancho inferior.
    tip_gap = min(0.08, (y1 - y0) / 6)
    verts = [
        (x, y1),
        (x + d * 0.15, y1),
        (x + d * 0.55, y1),
        (x + d * 0.55, y1 - tip_gap),
        (x + d * 0.55, ym + tip_gap * 0.7),
        (x + d * 0.55, ym),
        (x + d, ym),
        (x + d * 0.55, ym),
        (x + d * 0.55, ym - tip_gap * 0.7),
        (x + d * 0.55, y0 + tip_gap),
        (x + d * 0.55, y0),
        (x + d * 0.15, y0),
        (x, y0),
    ]
    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
    ]
    ax.add_patch(
        PathPatch(
            MplPath(verts, codes),
            facecolor="none",
            edgecolor=color,
            lw=lw,
            capstyle="round",
            joinstyle="round",
            zorder=zorder,
            clip_on=False,
        )
    )
    return x + d, ym


def caption(ax, x, y, text, fontsize=8.5, ha="center", style="normal", color=TEXT):
    ax.text(
        x,
        y,
        text,
        ha=ha,
        va="top",
        fontsize=fontsize,
        fontproperties=FONT_REGULAR if style == "normal" else FONT_BOLD,
        color=color,
        zorder=5,
        clip_on=False,
        linespacing=1.15,
    )


def sql_banner(ax, x, y, text, fontsize=8.2, ha="left"):
    ax.text(
        x,
        y,
        text,
        ha=ha,
        va="top",
        fontsize=fontsize,
        fontproperties=FONT_REGULAR,
        color=NAVY_DARK,
        zorder=5,
        clip_on=False,
        linespacing=1.35,
    )


def save(fig, stem: str) -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("png", "svg"):
        path = OUT / f"{stem}.{ext}"
        fig.savefig(path, dpi=200, facecolor=WHITE, edgecolor="none", bbox_inches="tight", pad_inches=0.18)
        paths.append(path)
    plt.close(fig)
    return paths


GREY_BOX = "#EEF1F4"
GREY_EDGE = "#C5CDD6"
PILL_H = 0.36
PILL_GAP = 0.075


def pill(ax, cx, cy, text, fill=WHITE, edge=NAVY, w=None, h=None, fontsize=8.5, lw=LW, zorder=3):
    """Célula redondeada de ancho variable, centrada en (cx, cy)."""
    h = PILL_H if h is None else h
    if w is None:
        w = max(CELL, 0.62 * (fontsize / 72) * max(1, len(str(text))) + 0.22)
    rounded(ax, cx - w / 2, cy - h / 2, w, h, fill, edge, lw=lw, zorder=zorder, radius=min(RADIUS, h * 0.30))
    if text is not None and text != "":
        ax.text(
            cx,
            cy,
            str(text),
            ha="center",
            va="center",
            fontsize=fontsize,
            fontproperties=FONT_BOLD,
            color=TEXT,
            zorder=zorder + 1,
            clip_on=False,
        )
    return w


def stack_y(top, n, size=PILL_H, gap=PILL_GAP):
    """Centros y (de arriba hacia abajo) de n pastillas."""
    ys = []
    y = top - size / 2
    for _ in range(n):
        ys.append(y)
        y -= size + gap
    return ys


def code_block(ax, x, y_top, lines, fontsize=8.6, pad_x=0.16, pad_y=0.12, line_h=0.205):
    """Caja gris redondeada con la consulta en monoespaciado. Devuelve (ancho, alto, y_inferior)."""
    char_w = 0.0122 * fontsize  # DejaVu Sans Mono (holgado, para que no se recorte)
    max_chars = max(len(line) for line in lines)
    w = pad_x * 2 + max_chars * char_w + 0.06
    h = pad_y * 2 + len(lines) * line_h
    y = y_top - h
    rounded(ax, x, y, w, h, GREY_BOX, GREY_EDGE, lw=1.0, radius=0.10, zorder=2)
    ty = y_top - pad_y - line_h * 0.55
    for line in lines:
        ax.text(
            x + pad_x,
            ty,
            line,
            ha="left",
            va="center",
            fontsize=fontsize,
            fontproperties=FONT_MONO,
            color=TEXT,
            zorder=5,
            clip_on=False,
        )
        ty -= line_h
    return w, h, y


def orden_evaluacion(ax, x0, x1, y, with_arrow=True):
    """Etiqueta «Orden de evaluación» y, opcionalmente, una flecha delgada de x0 a x1."""
    ax.text(
        (x0 + x1) / 2,
        y,
        "Orden de evaluación",
        ha="center",
        va="bottom",
        fontsize=11,
        fontproperties=FONT_BOLD,
        color=NAVY_DARK,
        zorder=5,
        clip_on=False,
    )
    if with_arrow and x1 - x0 > 0.8:
        ax.annotate(
            "",
            xy=(x1, y - 0.11),
            xytext=(x0, y - 0.11),
            arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.15, mutation_scale=10),
            zorder=4,
            clip_on=False,
        )


# ---------------------------------------------------------------------------
# Datos reales de TheLook (consultas ejecutadas contra data/thelook.duckdb,
# semilla 2026). Los conteos y filas dibujados coinciden con estas consultas.
# ---------------------------------------------------------------------------

# Consulta de la celda adyacente en «Agregaciones» (HAVING), sin FETCH FIRST.
# HAVING COUNT(*) > 35 deja 8 marcas; Estuario (35) y Cobalto (32) no pasan.
QUERY_HAVING = [
    "SELECT brand, COUNT(*) AS productos",
    "FROM products",
    "WHERE department = 'Men'",
    "GROUP BY brand",
    "HAVING COUNT(*) > 35",
    "ORDER BY productos DESC;",
]
# Misma consulta, con FETCH FIRST, para el diagrama del orden lógico.
# La celda adyacente no incluye esa cláusula; el diagrama lo indica.
QUERY_ORDEN = [
    "SELECT brand, COUNT(*) AS productos",
    "FROM products",
    "WHERE department = 'Men'",
    "GROUP BY brand",
    "HAVING COUNT(*) > 35",
    "ORDER BY productos DESC",
    "FETCH FIRST 5 ROWS ONLY;",
]

# Filas de FROM que se muestran (hay más: se indica con «…»).
# (brand, department) tomados de products reales.
FROM_SAMPLE = [
    ("Quetzal", "Women"),
    ("Sierra Alta", "Women"),
    ("Valle Claro", "Women"),
    ("Roble", "Men"),
    ("Lince", "Men"),
    ("Estuario", "Men"),
    ("Cobalto", "Men"),
    ("Altamira", "Men"),
]
WHERE_SAMPLE = [(b, d) for b, d in FROM_SAMPLE if d == "Men"]

# Conteos exactos de products WHERE department = 'Men' GROUP BY brand.
# Se dibujan las 8 que pasan el HAVING, más Estuario y Cobalto (no pasan),
# y un «…» por el resto de marcas.
# GROUP BY no garantiza un orden: se muestran en un orden no ordenado
# para que ORDER BY (productos DESC) se vea con claridad.
GROUP_COUNTS = [
    ("Lince", 38),
    ("Roble", 43),
    ("Estuario", 35),
    ("Pampa", 37),
    ("Altamira", 41),
    ("Cobalto", 32),
    ("Quetzal", 36),
    ("Hilo Fino", 39),
    ("Bosque Norte", 36),
    ("Marea", 39),
]
# Resultado de ORDER BY productos DESC (empates: Hilo Fino antes que Marea,
# Quetzal antes que Bosque Norte, como los devuelve DuckDB).
ORDER_BY_COUNTS = [
    ("Roble", 43),
    ("Altamira", 41),
    ("Hilo Fino", 39),
    ("Marea", 39),
    ("Lince", 38),
    ("Pampa", 37),
    ("Quetzal", 36),
    ("Bosque Norte", 36),
]
FETCH_COUNTS = ORDER_BY_COUNTS[:5]

BRAND_FILL = {
    "Roble": GREEN,
    "Altamira": BLUE,
    "Hilo Fino": YELLOW,
    "Marea": "#F5C6AA",
    "Lince": "#D5C6E8",
    "Pampa": "#C5E4D4",
    "Quetzal": "#F5D0E0",
    "Bosque Norte": "#C9DCF0",
    "Estuario": "#E8E0C8",
    "Cobalto": "#D9D9D9",
    "Sierra Alta": "#F3F3F3",
    "Valle Claro": "#F3F3F3",
}


def brand_fill(name):
    return BRAND_FILL.get(name, "#F3F3F3")


# JOIN: orders 1 (2 artículos) y 2 (1 artículo). SUM(num_of_item) = 5; COUNT(*) = 3.
QUERY_JOIN = [
    "SELECT SUM(o.num_of_item) AS articulos,",
    "       COUNT(*) AS filas",
    "FROM orders AS o",
    "JOIN order_items AS oi",
    "  ON o.order_id = oi.order_id",
    "WHERE o.order_id IN (1, 2);",
]
ORDERS_ROWS = [(1, 2, "A"), (2, 1, "B")]
ITEMS_ROWS = [(1, "A"), (1, "A"), (2, "B")]
JOIN_ROWS = [(1, 2, "A"), (1, 2, "A"), (2, 1, "B")]
ORDER_FILL = {"A": GREEN, "B": BLUE}

# Ventana frente a GROUP BY: cuatro productos reales, dos categorías.
# Jeans: id 41 (173.11), 53 (165.82); Socks: id 30 (10.64), 49 (17.80).
QUERY_GROUP = [
    "SELECT category, COUNT(*) AS productos",
    "FROM products",
    "WHERE id IN (30, 41, 49, 53)",
    "GROUP BY category;",
]
QUERY_WINDOW = [
    "SELECT category, retail_price,",
    "       COUNT(*) OVER (PARTITION BY category) AS productos",
    "FROM products",
    "WHERE id IN (30, 41, 49, 53)",
    "ORDER BY category, id;",
]
WINDOW_ROWS = [
    ("Jeans", 173.11, 2),
    ("Jeans", 165.82, 2),
    ("Socks", 10.64, 2),
    ("Socks", 17.80, 2),
]
CAT_FILL = {"Jeans": GREEN, "Socks": BLUE}

# Álgebra: consulta sin alias, IN ni AND (aún no se han enseñado en «Introducción»).
# El resultado real tiene muchas filas; el diagrama muestra una muestra.
QUERY_ALGEBRA = [
    "SELECT users.id, users.traffic_source",
    "FROM users",
    "JOIN orders",
    "  ON users.id = orders.user_id",
    "WHERE users.traffic_source = 'Search';",
]
NOTE_ALGEBRA = "La sintaxis de JOIN se estudia en “Combinación de tablas y lógica condicional”."
USERS_ROWS = [(2, "Search", "A"), (3, "Search", "A"), (12, "Email", "B")]
ORDERS_ALG = [(1, 2, "A"), (2, 3, "A"), (16, 12, "B")]
JOIN_ALG = [(2, "Search", 1, "A"), (3, "Search", 2, "A"), (12, "Email", 16, "B")]
SELECT_ALG = [(2, "Search", "A"), (3, "Search", "A")]
SRC_FILL = {"A": GREEN, "B": BLUE}


# ===========================================================================
# 1. Orden lógico de ejecución
# ===========================================================================

def _draw_brand_dept_column(ax, x, w, y_hdr, y_data, rows, with_ellipsis=True):
    """Columna de dos pastillas (brand, department). Devuelve ys de las filas de datos."""
    n = len(rows) + (1 if with_ellipsis else 0)
    ys = stack_y(y_data, n)
    pill_w = (w - 0.10) / 2 - 0.04
    c1 = x + w / 2 - (pill_w + 0.05) / 2
    c2 = x + w / 2 + (pill_w + 0.05) / 2
    # encabezado vacío, como en la figura de referencia
    pill(ax, c1, y_hdr, "", fill=WHITE, w=pill_w, h=PILL_H)
    pill(ax, c2, y_hdr, "", fill=WHITE, edge=CRIMSON, w=pill_w, h=PILL_H)
    data_ys = ys[:-1] if with_ellipsis else ys
    for (brand, dept), y in zip(rows, data_ys):
        pill(ax, c1, y, brand, fill=brand_fill(brand), w=pill_w, fontsize=7.6)
        pill(ax, c2, y, dept, fill=WHITE, edge=CRIMSON, w=pill_w, fontsize=7.6)
    if with_ellipsis:
        pill(ax, c1, ys[-1], "…", fill=WHITE, w=pill_w, fontsize=11)
        pill(ax, c2, ys[-1], "…", fill=WHITE, edge=CRIMSON, w=pill_w, fontsize=11)
    return ys, c1, c2, pill_w


def _draw_group_count_having(ax, xs, widths, y_data, show_select=False, select_xs=None):
    """Dibuja GROUP BY (marca), COUNT(*), HAVING y, si aplica, SELECT y ORDER BY."""
    n = len(GROUP_COUNTS) + 1  # + elipsis
    ys = stack_y(y_data, n)
    group_ys = ys[:-1]
    ell_y = ys[-1]
    cxg = xs[0] + widths[0] / 2
    cxc = xs[1] + widths[1] / 2
    cxh = xs[2] + widths[2] / 2
    pw = min(widths[0] - 0.12, 1.15)
    for (brand, nprod), y in zip(GROUP_COUNTS, group_ys):
        pill(ax, cxg, y, brand, fill=brand_fill(brand), w=pw, fontsize=7.6)
        # llave de un solo renglón hacia el conteo
        y_top, y_bot = y + PILL_H / 2 + 0.02, y - PILL_H / 2 - 0.02
        tip_x, tip_y = curly_brace(ax, xs[0] + widths[0] + 0.02, y_bot, y_top, depth=0.14)
        pill(ax, cxc, y, nprod, fill=brand_fill(brand), w=CELL + 0.06, fontsize=9)
        ax.plot([tip_x, cxc - (CELL + 0.06) / 2 - 0.01], [tip_y, y], color=NAVY, lw=1.2, zorder=3, solid_capstyle="round")
        if nprod > 35:
            pill(ax, cxh, y, nprod, fill=brand_fill(brand), w=CELL + 0.06, fontsize=9)
    pill(ax, cxg, ell_y, "…", fill=WHITE, w=pw, fontsize=11)
    # SELECT se alinea con HAVING (aún sin ordenar). ORDER BY reordena.
    if show_select:
        xs_sel, ws_sel, xs_ord, ws_ord = select_xs[:4]
        fetch_spec = select_xs[4:] if len(select_xs) > 4 else None
        having_pairs = [(b, n, y) for (b, n), y in zip(GROUP_COUNTS, group_ys) if n > 35]
        pw2 = min((ws_sel - 0.10) / 2 - 0.03, 1.05)
        c1 = xs_sel + ws_sel / 2 - (pw2 + 0.05) / 2
        c2 = xs_sel + ws_sel / 2 + (pw2 + 0.05) / 2
        for brand, nprod, y in having_pairs:
            pill(ax, c1, y, brand, fill=brand_fill(brand), w=pw2, fontsize=7.4)
            pill(ax, c2, y, nprod, fill=brand_fill(brand), w=CELL + 0.04, fontsize=8.5)
        # ORDER BY: orden productos DESC, compactado arriba para que el cambio se vea.
        ys_o = stack_y(having_pairs[0][2] + PILL_H / 2, len(ORDER_BY_COUNTS))
        c3 = xs_ord + ws_ord / 2 - (pw2 + 0.05) / 2
        c4 = xs_ord + ws_ord / 2 + (pw2 + 0.05) / 2
        for (brand, nprod), y in zip(ORDER_BY_COUNTS, ys_o):
            pill(ax, c3, y, brand, fill=brand_fill(brand), w=pw2, fontsize=7.4)
            pill(ax, c4, y, nprod, fill=brand_fill(brand), w=CELL + 0.04, fontsize=8.5)
        ys_f = None
        if fetch_spec:
            xs_f, ws_f = fetch_spec
            ys_f = stack_y(ys_o[0] + PILL_H / 2, len(FETCH_COUNTS))
            c5 = xs_f + ws_f / 2 - (pw2 + 0.05) / 2
            c6 = xs_f + ws_f / 2 + (pw2 + 0.05) / 2
            for (brand, nprod), y in zip(FETCH_COUNTS, ys_f):
                pill(ax, c5, y, brand, fill=brand_fill(brand), w=pw2, fontsize=7.4)
                pill(ax, c6, y, nprod, fill=brand_fill(brand), w=CELL + 0.04, fontsize=8.5)
        return ys, having_pairs, ys_o, ys_f
    return ys, None, None, None


def diagrama_orden_logico():
    # Consulta arriba a la izquierda (orden escrito). Columnas a la derecha: orden de evaluación.
    col_ws = [2.05, 2.05, 1.36, 0.85, 1.15, 1.95, 1.95, 1.95]
    gaps = [0.22, 0.22, 0.36, 0.22, 0.22, 0.22, 0.22]
    left_cols = 0.25
    n_rows = len(GROUP_COUNTS) + 1
    body_h = n_rows * PILL_H + (n_rows - 1) * PILL_GAP + PILL_H + 0.20
    cols_w = sum(col_ws) + sum(gaps)
    # espacio para el texto + caja de código + nota de FETCH
    top_text = 0.45
    code_est_h = 0.12 * 2 + 7 * 0.205 + 0.55
    mid_gap = 0.70  # etiqueta «Orden de evaluación» + flecha
    bot = 0.70
    width = left_cols + cols_w + 0.25
    height = 0.20 + top_text + code_est_h + mid_gap + HEAD_H + 0.14 + body_h + bot
    fig, ax = new_canvas(width, height)

    # Texto explicativo, separado de la consulta.
    ax.text(
        0.25,
        height - 0.12,
        "Aunque se escribe primero  SELECT,  el motor evalúa las cláusulas en el orden de las columnas.",
        ha="left",
        va="top",
        fontsize=9.2,
        fontproperties=FONT_REGULAR,
        color=NAVY_DARK,
        zorder=5,
        clip_on=False,
    )
    _, code_h, code_bot = code_block(ax, 0.25, height - 0.12 - top_text, QUERY_ORDEN)
    ax.text(
        0.25,
        code_bot - 0.07,
        "La celda adyacente no incluye FETCH FIRST;\nse añade aquí para completar el orden de evaluación.",
        ha="left",
        va="top",
        fontsize=8.0,
        fontproperties=FONT_REGULAR,
        color=NAVY_DARK,
        zorder=5,
        clip_on=False,
    )
    y_label = code_bot - 0.58
    xs = []
    x = left_cols
    for i, w in enumerate(col_ws):
        xs.append(x)
        x += w + (gaps[i] if i < len(gaps) else 0)
    orden_evaluacion(ax, xs[0], xs[-1] + col_ws[-1], y_label, with_arrow=True)

    y_head = y_label - 0.28 - HEAD_H
    y_hdr = y_head - 0.14 - PILL_H / 2
    y_data = y_hdr - PILL_H / 2 - PILL_GAP

    header_box(ax, xs[0], y_head, col_ws[0], HEAD_H, "FROM")
    ys_from, *_ = _draw_brand_dept_column(ax, xs[0], col_ws[0], y_hdr, y_data, FROM_SAMPLE)
    caption(ax, xs[0] + col_ws[0] / 2, ys_from[-1] - PILL_H / 2 - 0.10, "products\n(brand, department)\nalgunas filas")

    header_box(ax, xs[1], y_head, col_ws[1], HEAD_H, "WHERE")
    ys_w, *_ = _draw_brand_dept_column(ax, xs[1], col_ws[1], y_hdr, y_data, WHERE_SAMPLE)
    caption(ax, xs[1] + col_ws[1] / 2, ys_w[-1] - PILL_H / 2 - 0.10, "filtra filas\ndepartment = 'Men'")

    header_box(
        ax,
        xs[2],
        y_head,
        col_ws[2],
        HEAD_H,
        "GROUP\nBY",
        icons=[{"text": "", "fill": GREEN, "edge": NAVY, "stack": True},
               {"text": "", "fill": BLUE, "edge": NAVY, "stack": True},
               {"text": "", "fill": YELLOW, "edge": NAVY, "stack": True}],
        fontsize=10,
    )
    header_box(ax, xs[3], y_head, col_ws[3], HEAD_H, "COUNT(*)", fontsize=9.0)
    header_box(ax, xs[4], y_head, col_ws[4], HEAD_H, "HAVING\n> 35", fontsize=10)
    header_box(ax, xs[5], y_head, col_ws[5], HEAD_H, "SELECT", icons=[{"text": "", "fill": WHITE, "edge": NAVY}], fontsize=10)
    header_box(ax, xs[6], y_head, col_ws[6], HEAD_H, "ORDER BY", fontsize=10)
    header_box(ax, xs[7], y_head, col_ws[7], HEAD_H, "FETCH\nFIRST", fontsize=10)

    ys_g, having_pairs, ys_o, ys_f = _draw_group_count_having(
        ax,
        [xs[2], xs[3], xs[4]],
        [col_ws[2], col_ws[3], col_ws[4]],
        y_data,
        show_select=True,
        select_xs=(xs[5], col_ws[5], xs[6], col_ws[6], xs[7], col_ws[7]),
    )
    caption(ax, xs[2] + col_ws[2] / 2, ys_g[-1] - PILL_H / 2 - 0.10, "una fila por marca\n(sin orden garantizado)")
    caption(ax, xs[4] + col_ws[4] / 2, ys_g[-1] - PILL_H / 2 - 0.10, "filtra grupos\nCOUNT(*) > 35")
    caption(ax, xs[5] + col_ws[5] / 2, ys_g[-1] - PILL_H / 2 - 0.10, "brand, productos")
    if ys_o:
        caption(ax, xs[6] + col_ws[6] / 2, ys_o[-1] - PILL_H / 2 - 0.10, "productos\ndescendente")
    if ys_f:
        caption(ax, xs[7] + col_ws[7] / 2, ys_f[-1] - PILL_H / 2 - 0.10, "5 filas")

    return save(fig, "diagrama_orden_logico")


# ===========================================================================
# 2. WHERE frente a HAVING
# ===========================================================================

def diagrama_where_having():
    col_ws = [2.05, 2.05, 1.32, 0.85, 1.15]
    gaps = [0.22, 0.22, 0.36, 0.22]
    left_cols = 0.25
    n_rows = len(GROUP_COUNTS) + 1
    body_h = n_rows * PILL_H + (n_rows - 1) * PILL_GAP + PILL_H + 0.20
    cols_w = sum(col_ws) + sum(gaps)
    top_text = 0.45
    code_est_h = 0.12 * 2 + 6 * 0.205
    mid_gap = 0.70
    bot = 0.70
    width = left_cols + cols_w + 0.25
    height = 0.20 + top_text + code_est_h + mid_gap + HEAD_H + 0.14 + body_h + bot
    fig, ax = new_canvas(width, height)

    ax.text(
        0.25,
        height - 0.12,
        "WHERE  filtra filas antes de agrupar.    HAVING  filtra grupos después de agregar.",
        ha="left",
        va="top",
        fontsize=9.2,
        fontproperties=FONT_REGULAR,
        color=NAVY_DARK,
        zorder=5,
        clip_on=False,
    )
    _, code_h, code_bot = code_block(ax, 0.25, height - 0.12 - top_text, QUERY_HAVING)
    y_label = code_bot - 0.18
    xs = []
    x = left_cols
    for i, w in enumerate(col_ws):
        xs.append(x)
        x += w + (gaps[i] if i < len(gaps) else 0)
    orden_evaluacion(ax, xs[0], xs[-1] + col_ws[-1], y_label, with_arrow=True)

    y_head = y_label - 0.28 - HEAD_H
    y_hdr = y_head - 0.14 - PILL_H / 2
    y_data = y_hdr - PILL_H / 2 - PILL_GAP

    header_box(ax, xs[0], y_head, col_ws[0], HEAD_H, "FROM")
    ys_from, *_ = _draw_brand_dept_column(ax, xs[0], col_ws[0], y_hdr, y_data, FROM_SAMPLE)
    caption(ax, xs[0] + col_ws[0] / 2, ys_from[-1] - PILL_H / 2 - 0.10, "products\n(brand, department)\nalgunas filas")

    header_box(ax, xs[1], y_head, col_ws[1], HEAD_H, "WHERE")
    ys_w, *_ = _draw_brand_dept_column(ax, xs[1], col_ws[1], y_hdr, y_data, WHERE_SAMPLE)
    caption(ax, xs[1] + col_ws[1] / 2, ys_w[-1] - PILL_H / 2 - 0.10, "filtra filas\n(se descartan las de Women)")

    header_box(
        ax,
        xs[2],
        y_head,
        col_ws[2],
        HEAD_H,
        "GROUP\nBY",
        icons=[{"text": "", "fill": GREEN, "edge": NAVY, "stack": True},
               {"text": "", "fill": BLUE, "edge": NAVY, "stack": True},
               {"text": "", "fill": YELLOW, "edge": NAVY, "stack": True}],
        fontsize=10,
    )
    header_box(ax, xs[3], y_head, col_ws[3], HEAD_H, "COUNT(*)", fontsize=9.0)
    header_box(ax, xs[4], y_head, col_ws[4], HEAD_H, "HAVING\n> 35", fontsize=10)
    ys_g, _, _, _ = _draw_group_count_having(
        ax, [xs[2], xs[3], xs[4]], [col_ws[2], col_ws[3], col_ws[4]], y_data
    )
    caption(ax, xs[2] + col_ws[2] / 2, ys_g[-1] - PILL_H / 2 - 0.10, "una fila por marca")
    caption(ax, xs[4] + col_ws[4] / 2, ys_g[-1] - PILL_H / 2 - 0.10, "filtra grupos\n(se descartan\nEstuario 35 y Cobalto 32)")

    return save(fig, "diagrama_where_having")


# ===========================================================================
# 3. JOIN y duplicación de filas
# ===========================================================================

def diagrama_join_duplicacion():
    two_w = 1.15
    join_w = 1.25
    agg_w = 1.35
    count_w = 0.95
    widths = [two_w, 1.30, join_w, agg_w, count_w]
    gaps = [0.50, 0.50, 0.40, 0.28]
    left_m, right_m = 0.25, 0.25
    body_h = 4 * PILL_H + 3 * PILL_GAP + 0.30
    cols_w = sum(widths) + sum(gaps)
    top_text = 0.42
    code_est_h = 0.12 * 2 + 6 * 0.205
    mid_gap = 0.62
    bot = 0.95
    width = left_m + cols_w + right_m
    height = 0.18 + top_text + code_est_h + mid_gap + HEAD_H + 0.14 + body_h + bot
    fig, ax = new_canvas(width, height)

    ax.text(
        left_m,
        height - 0.12,
        "Una relación 1:N  repite la fila de la izquierda.  SUM(num_of_item)  queda inflada.",
        ha="left",
        va="top",
        fontsize=9.0,
        fontproperties=FONT_REGULAR,
        color=NAVY_DARK,
        zorder=5,
        clip_on=False,
    )
    _, _, code_bot = code_block(ax, left_m, height - 0.12 - top_text, QUERY_JOIN)

    y_label = code_bot - 0.16
    xs = []
    x = left_m
    for i, w in enumerate(widths):
        xs.append(x)
        x += w + (gaps[i] if i < len(gaps) else 0)
    # Los pasos de evaluación son el JOIN y las agregaciones sobre su resultado.
    orden_evaluacion(ax, xs[2], xs[-1] + widths[-1], y_label, with_arrow=True)

    y_head = y_label - 0.26 - HEAD_H
    y_hdr = y_head - 0.14 - PILL_H / 2
    y_data = y_hdr - PILL_H / 2 - PILL_GAP

    header_box(ax, xs[0], y_head, widths[0], HEAD_H, "orders")
    c1 = xs[0] + widths[0] / 2 - (CELL + GAP) / 2
    c2 = xs[0] + widths[0] / 2 + (CELL + GAP) / 2
    cell(ax, c1, y_hdr, "", fill=WHITE)
    cell(ax, c2, y_hdr, "", fill=WHITE, edge=CRIMSON)
    ys_o = stack_y(y_data, 2, size=CELL, gap=GAP + CELL + 0.15)
    for (oid, n, g), y in zip(ORDERS_ROWS, ys_o):
        cell(ax, c1, y, oid, fill=ORDER_FILL[g])
        cell(ax, c2, y, n, fill=WHITE, edge=CRIMSON)
    caption(ax, xs[0] + widths[0] / 2, ys_o[-1] - CELL / 2 - 0.10, "order_id, num_of_item\nuna fila por orden")

    header_box(ax, xs[1], y_head, widths[1], HEAD_H, "order_items", fontsize=9.0)
    cxi = xs[1] + widths[1] / 2
    cell(ax, cxi, y_hdr, "", fill=WHITE)
    ys_i = stack_y(y_data, 3, size=CELL, gap=GAP)
    for (oid, g), y in zip(ITEMS_ROWS, ys_i):
        cell(ax, cxi, y, oid, fill=ORDER_FILL[g])
    caption(ax, xs[1] + widths[1] / 2, ys_i[-1] - CELL / 2 - 0.10, "order_id\nuna fila por artículo")

    header_box(ax, xs[2], y_head, widths[2], HEAD_H, "JOIN")
    cxj1 = xs[2] + widths[2] / 2 - (CELL + GAP) / 2
    cxj2 = xs[2] + widths[2] / 2 + (CELL + GAP) / 2
    cell(ax, cxj1, y_hdr, "", fill=WHITE)
    cell(ax, cxj2, y_hdr, "", fill=WHITE, edge=CRIMSON)
    ys_j = stack_y(y_data, 3, size=CELL, gap=GAP)
    for (oid, n, g), y in zip(JOIN_ROWS, ys_j):
        cell(ax, cxj1, y, oid, fill=ORDER_FILL[g])
        cell(ax, cxj2, y, n, fill=WHITE, edge=CRIMSON)
    y_top_edge = ys_j[0] + CELL / 2 + 0.06
    y_bot_edge = ys_j[1] - CELL / 2 - 0.06
    pad_x = 0.10
    dashed_box(
        ax,
        cxj1 - CELL / 2 - pad_x,
        y_bot_edge,
        (cxj2 + CELL / 2 + pad_x) - (cxj1 - CELL / 2 - pad_x),
        y_top_edge - y_bot_edge,
    )
    caption(ax, xs[2] + widths[2] / 2, ys_j[-1] - CELL / 2 - 0.10, "la orden 1 se repite\n(una vez por artículo)")

    def arrow(x0, y0, x1, y1):
        ax.add_patch(
            FancyArrowPatch(
                (x0, y0),
                (x1, y1),
                arrowstyle="-|>",
                mutation_scale=8,
                lw=1.15,
                color=NAVY,
                zorder=1.2,
                shrinkA=1,
                shrinkB=1,
                capstyle="round",
            )
        )

    for y_i, y_j in zip(ys_i, ys_j):
        arrow(xs[1] + widths[1] / 2 + CELL / 2 + 0.04, y_i, xs[2] - 0.04, y_j)
    arrow(xs[0] + widths[0] + 0.03, ys_o[0], xs[1] - 0.04, ys_i[0])
    arrow(xs[0] + widths[0] + 0.03, ys_o[0], xs[1] - 0.04, ys_i[1])
    arrow(xs[0] + widths[0] + 0.03, ys_o[1], xs[1] - 0.04, ys_i[2])

    header_box(ax, xs[3], y_head, widths[3], HEAD_H, "SUM(\nnum_of_item)", fontsize=8.6)
    cxs = xs[3] + widths[3] / 2
    y_top_all = ys_j[0] + CELL / 2 + 0.04
    y_bot_all = ys_j[-1] - CELL / 2 - 0.04
    tip_x, tip_y = curly_brace(ax, xs[2] + widths[2] + 0.02, y_bot_all, y_top_all, depth=0.18)
    mid_all = (ys_j[0] + ys_j[-1]) / 2
    cell(ax, cxs, mid_all, "5", fill=WHITE, edge=CRIMSON, lw=1.8)
    ax.plot([tip_x, cxs - CELL / 2 - 0.01], [tip_y, mid_all], color=NAVY, lw=1.3, zorder=3, solid_capstyle="round")
    caption(ax, xs[3] + widths[3] / 2, ys_j[-1] - CELL / 2 - 0.10, "suma incorrecta\n(2+2+1 = 5)\nlo correcto es 3")

    header_box(ax, xs[4], y_head, widths[4], HEAD_H, "COUNT(*)", fontsize=9.5)
    cell(ax, xs[4] + widths[4] / 2, mid_all, "3", fill=WHITE, edge=NAVY)
    caption(ax, xs[4] + widths[4] / 2, ys_j[-1] - CELL / 2 - 0.10, "cuenta las filas\ndel JOIN\n(3 artículos)")

    return save(fig, "diagrama_join_duplicacion")


# ===========================================================================
# 4. Función de ventana frente a GROUP BY
# ===========================================================================

def diagrama_ventana_group_by():
    two_w = 1.45
    gb_w = 1.20
    count_w = 0.85
    win_w = 2.15
    widths = [two_w, gb_w, count_w, win_w]
    gaps = [0.48, 0.38, 0.55]
    left_m, right_m = 0.25, 0.25
    body_h = 5 * PILL_H + 4 * PILL_GAP + 0.15
    cols_w = sum(widths) + sum(gaps)
    top_text = 0.42
    code_est_h = 0.12 * 2 + 6 * 0.205
    mid_gap = 0.28
    bot = 0.85
    width = max(left_m + cols_w + right_m, 11.2)
    height = 0.18 + top_text + code_est_h + mid_gap + HEAD_H + 0.14 + body_h + bot
    fig, ax = new_canvas(width, height)

    ax.text(
        left_m,
        height - 0.12,
        "GROUP BY  colapsa las filas a una por grupo.    La función de ventana conserva cada fila y añade una columna.",
        ha="left",
        va="top",
        fontsize=8.8,
        fontproperties=FONT_REGULAR,
        color=NAVY_DARK,
        zorder=5,
        clip_on=False,
    )
    # Dos bloques de consulta, uno por camino, alineados con sus columnas.
    xs = []
    x = left_m
    for i, w in enumerate(widths):
        xs.append(x)
        x += w + (gaps[i] if i < len(gaps) else 0)

    y_code = height - 0.12 - top_text
    w_g, h_g, _ = code_block(ax, left_m, y_code, QUERY_GROUP, fontsize=7.8, line_h=0.190, pad_x=0.14, pad_y=0.10)
    w_w, h_w, _ = code_block(ax, left_m + w_g + 0.22, y_code, QUERY_WINDOW, fontsize=7.8, line_h=0.190, pad_x=0.14, pad_y=0.10)
    code_h = max(h_g, h_w)
    y_head = y_code - code_h - mid_gap - HEAD_H
    y_hdr = y_head - 0.14 - PILL_H / 2
    y_data = y_hdr - PILL_H / 2 - PILL_GAP

    # filas de partida (las 4 de la consulta de ventana, en ORDER BY category, id)
    header_box(ax, xs[0], y_head, widths[0], HEAD_H, "filas")
    pw = 0.72
    c1 = xs[0] + widths[0] / 2 - (pw + 0.05) / 2
    c2 = xs[0] + widths[0] / 2 + (pw + 0.05) / 2
    pill(ax, c1, y_hdr, "", fill=WHITE, w=pw)
    pill(ax, c2, y_hdr, "", fill=WHITE, edge=CRIMSON, w=pw)
    ys = stack_y(y_data, len(WINDOW_ROWS))
    for (cat, price, _), y in zip(WINDOW_ROWS, ys):
        pill(ax, c1, y, cat, fill=CAT_FILL[cat], w=pw, fontsize=8.0)
        pill(ax, c2, y, f"{price:.2f}", fill=WHITE, edge=CRIMSON, w=pw, fontsize=8.0)
    caption(ax, xs[0] + widths[0] / 2, ys[-1] - PILL_H / 2 - 0.10, "category, retail_price")

    header_box(
        ax,
        xs[1],
        y_head,
        widths[1],
        HEAD_H,
        "GROUP\nBY",
        icons=[{"text": "", "fill": GREEN, "edge": NAVY, "stack": True},
               {"text": "", "fill": BLUE, "edge": NAVY, "stack": True}],
        fontsize=10,
    )
    ys_a, ys_b = [ys[0], ys[1]], [ys[2], ys[3]]
    cxg = xs[1] + widths[1] / 2
    for price, y in zip((173.11, 165.82), ys_a):
        pill(ax, cxg, y, f"{price:.2f}", fill=GREEN, edge=CRIMSON, w=0.70, fontsize=8.0)
    for price, y in zip((10.64, 17.80), ys_b):
        pill(ax, cxg, y, f"{price:.2f}", fill=BLUE, edge=CRIMSON, w=0.70, fontsize=8.0)
    for ys_g in (ys_a, ys_b):
        y_top_edge = ys_g[0] + PILL_H / 2 + 0.03
        y_bot_edge = ys_g[-1] - PILL_H / 2 - 0.03
        dashed_box(ax, cxg - 0.70 / 2 - 0.10, y_bot_edge, 0.70 + 0.20, y_top_edge - y_bot_edge)

    header_box(ax, xs[2], y_head, widths[2], HEAD_H, "COUNT(*)", fontsize=9.5)
    cxc = xs[2] + widths[2] / 2
    for ys_g, cat, n in ((ys_a, "Jeans", 2), (ys_b, "Socks", 2)):
        y_top_edge = ys_g[0] + PILL_H / 2 + 0.03
        y_bot_edge = ys_g[-1] - PILL_H / 2 - 0.03
        tip_x, tip_y = curly_brace(ax, xs[1] + widths[1] + 0.02, y_bot_edge + 0.01, y_top_edge - 0.01, depth=0.16)
        mid = (ys_g[0] + ys_g[-1]) / 2
        cell(ax, cxc, mid, n, fill=CAT_FILL[cat])
        ax.plot([tip_x, cxc - CELL / 2 - 0.01], [tip_y, mid], color=NAVY, lw=1.3, zorder=3, solid_capstyle="round")
    caption(ax, (xs[1] + xs[2] + widths[2]) / 2, ys[-1] - PILL_H / 2 - 0.10, "colapsa a una fila\npor grupo")

    header_box(ax, xs[3], y_head, widths[3], HEAD_H, "función de ventana", fontsize=9.5)
    span = 3 * 0.62 + 2 * 0.06
    c0 = xs[3] + widths[3] / 2 - span / 2 + 0.62 / 2
    c1w = c0 + 0.62 + 0.06
    c2w = c1w + 0.62 + 0.06
    pill(ax, c0, y_hdr, "", fill=WHITE, w=0.62)
    pill(ax, c1w, y_hdr, "", fill=WHITE, edge=CRIMSON, w=0.62)
    pill(ax, c2w, y_hdr, "", fill=WHITE, w=0.50)
    for (cat, price, n), y in zip(WINDOW_ROWS, ys):
        pill(ax, c0, y, cat, fill=CAT_FILL[cat], w=0.62, fontsize=8.0)
        pill(ax, c1w, y, f"{price:.2f}", fill=WHITE, edge=CRIMSON, w=0.62, fontsize=8.0)
        pill(ax, c2w, y, n, fill=CAT_FILL[cat], w=0.50, fontsize=8.5)
    caption(ax, xs[3] + widths[3] / 2, ys[-1] - PILL_H / 2 - 0.10, "conserva cada fila\ny añade la cuenta")

    return save(fig, "diagrama_ventana_group_by")


# ===========================================================================
# 5. Álgebra relacional
# ===========================================================================

def diagrama_algebra_relacional():
    two_w = 1.35
    three_w = 1.85
    widths = [two_w, two_w, three_w, three_w, two_w]
    gaps = [0.28, 0.42, 0.32, 0.32]
    left_m, right_m = 0.25, 0.25
    body_h = 6 * PILL_H + 5 * PILL_GAP + 0.15
    cols_w = sum(widths) + sum(gaps)
    top_text = 0.42
    code_est_h = 0.12 * 2 + 5 * 0.205 + 0.42
    mid_gap = 0.70
    bot = 0.90
    width = left_m + cols_w + right_m
    height = 0.18 + top_text + code_est_h + mid_gap + HEAD_H + 0.14 + body_h + bot
    fig, ax = new_canvas(width, height)

    ax.text(
        left_m,
        height - 0.12,
        "Las operaciones se componen:  combinación,  después selección,  después proyección.",
        ha="left",
        va="top",
        fontsize=9.0,
        fontproperties=FONT_REGULAR,
        color=NAVY_DARK,
        zorder=5,
        clip_on=False,
    )
    _, _, code_bot = code_block(ax, left_m, height - 0.12 - top_text, QUERY_ALGEBRA)
    ax.text(
        left_m,
        code_bot - 0.07,
        NOTE_ALGEBRA,
        ha="left",
        va="top",
        fontsize=8.0,
        fontproperties=FONT_REGULAR,
        color=NAVY_DARK,
        zorder=5,
        clip_on=False,
    )
    y_label = code_bot - 0.42
    xs = []
    x = left_m
    for i, w in enumerate(widths):
        xs.append(x)
        x += w + (gaps[i] if i < len(gaps) else 0)
    # Las columnas de pasos (JOIN, WHERE, SELECT) son el orden de evaluación.
    orden_evaluacion(ax, xs[2], xs[-1] + widths[-1], y_label, with_arrow=True)

    y_head = y_label - 0.26 - HEAD_H
    y_hdr = y_head - 0.14 - PILL_H / 2
    y_data = y_hdr - PILL_H / 2 - PILL_GAP

    def two_col(x0, w, rows, left_vals, right_vals, fills, y_start, right_edge=CRIMSON, ellipsis=True):
        pw = min((w - 0.10) / 2 - 0.03, 0.72)
        c1 = x0 + w / 2 - (pw + 0.05) / 2
        c2 = x0 + w / 2 + (pw + 0.05) / 2
        pill(ax, c1, y_hdr, "", fill=WHITE, w=pw)
        pill(ax, c2, y_hdr, "", fill=WHITE, edge=right_edge, w=pw)
        n = len(rows) + (1 if ellipsis else 0)
        ys = stack_y(y_start, n)
        data_ys = ys[:-1] if ellipsis else ys
        for lv, rv, fill, y in zip(left_vals, right_vals, fills, data_ys):
            pill(ax, c1, y, lv, fill=fill, w=pw, fontsize=8.0)
            pill(ax, c2, y, rv, fill=WHITE, edge=right_edge, w=pw, fontsize=8.0)
        if ellipsis:
            pill(ax, c1, ys[-1], "…", fill=WHITE, w=pw, fontsize=11)
            pill(ax, c2, ys[-1], "…", fill=WHITE, edge=right_edge, w=pw, fontsize=11)
        return ys, c1, c2, pw

    def three_col(x0, w, triples, y_start, ellipsis=True):
        pw = 0.58
        span = 3 * pw + 2 * 0.05
        c0 = x0 + w / 2 - span / 2 + pw / 2
        c1 = c0 + pw + 0.05
        c2 = c1 + pw + 0.05
        pill(ax, c0, y_hdr, "", fill=WHITE, w=pw)
        pill(ax, c1, y_hdr, "", fill=WHITE, w=pw)
        pill(ax, c2, y_hdr, "", fill=WHITE, edge=CRIMSON, w=pw)
        n = len(triples) + (1 if ellipsis else 0)
        ys = stack_y(y_start, n)
        data_ys = ys[:-1] if ellipsis else ys
        for (a, src, b, g), y in zip(triples, data_ys):
            fill = SRC_FILL[g]
            pill(ax, c0, y, a, fill=fill, w=pw, fontsize=8.0)
            pill(ax, c1, y, src, fill=fill, w=pw, fontsize=7.6)
            pill(ax, c2, y, b, fill=WHITE, edge=CRIMSON, w=pw, fontsize=8.0)
        if ellipsis:
            pill(ax, c0, ys[-1], "…", fill=WHITE, w=pw, fontsize=11)
            pill(ax, c1, ys[-1], "…", fill=WHITE, w=pw, fontsize=11)
            pill(ax, c2, ys[-1], "…", fill=WHITE, edge=CRIMSON, w=pw, fontsize=11)
        return ys

    header_box(ax, xs[0], y_head, widths[0], HEAD_H, "users", fontsize=10)
    ys_u, *_ = two_col(
        xs[0],
        widths[0],
        USERS_ROWS,
        [r[0] for r in USERS_ROWS],
        [r[1] for r in USERS_ROWS],
        [SRC_FILL[r[2]] for r in USERS_ROWS],
        y_data,
    )
    caption(ax, xs[0] + widths[0] / 2, ys_u[-1] - PILL_H / 2 - 0.10, "id, traffic_source\nalgunas filas")

    header_box(ax, xs[1], y_head, widths[1], HEAD_H, "orders", fontsize=10)
    ys_o, *_ = two_col(
        xs[1],
        widths[1],
        ORDERS_ALG,
        [r[0] for r in ORDERS_ALG],
        [r[1] for r in ORDERS_ALG],
        [SRC_FILL[r[2]] for r in ORDERS_ALG],
        y_data,
    )
    caption(ax, xs[1] + widths[1] / 2, ys_o[-1] - PILL_H / 2 - 0.10, "order_id, user_id\nalgunas filas")

    header_box(ax, xs[2], y_head, widths[2], HEAD_H, "combinación\nJOIN", fontsize=10)
    ys_j = three_col(xs[2], widths[2], JOIN_ALG, y_data)
    caption(ax, xs[2] + widths[2] / 2, ys_j[-1] - PILL_H / 2 - 0.10, "users.id = orders.user_id\nalgunas filas")

    header_box(ax, xs[3], y_head, widths[3], HEAD_H, "selección\nWHERE", fontsize=10)
    selected = [t for t in JOIN_ALG if t[1] == "Search"]
    ys_s = three_col(xs[3], widths[3], selected, y_data)
    caption(ax, xs[3] + widths[3] / 2, ys_s[-1] - PILL_H / 2 - 0.10, "traffic_source = 'Search'\nalgunas filas")

    header_box(ax, xs[4], y_head, widths[4], HEAD_H, "proyección\nSELECT", fontsize=10)
    ys_p, *_ = two_col(
        xs[4],
        widths[4],
        SELECT_ALG,
        [r[0] for r in SELECT_ALG],
        [r[1] for r in SELECT_ALG],
        [SRC_FILL[r[2]] for r in SELECT_ALG],
        y_data,
    )
    caption(ax, xs[4] + widths[4] / 2, ys_p[-1] - PILL_H / 2 - 0.10, "id, traffic_source\nalgunas filas")

    return save(fig, "diagrama_algebra_relacional")


# ===========================================================================
# Main
# ===========================================================================

def main() -> None:
    generators = [
        diagrama_orden_logico,
        diagrama_where_having,
        diagrama_join_duplicacion,
        diagrama_ventana_group_by,
        diagrama_algebra_relacional,
    ]
    written: list[Path] = []
    for fn in generators:
        written.extend(fn())
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
