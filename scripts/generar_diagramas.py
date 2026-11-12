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


# Colores por categoría (rastrean el grupo en todos los pasos).
CAT_FILL = {"A": GREEN, "B": BLUE, "C": YELLOW}


# ===========================================================================
# Datos compartidos para los diagramas de agregación
# ===========================================================================
# productos (categoria, precio):
#   A 10, B 20, A 15, C 5, B 25, A 8, C 12, B 30
# WHERE precio >= 10 descarta C 5 y A 8.
# GROUP BY categoria → A: 2, B: 3, C: 1
# HAVING COUNT(*) >= 2 descarta C.
# ORDER BY n DESC coloca B (3) antes que A (2).
# FETCH FIRST 1 ROW ONLY deja B 3.

PRODUCTOS = [
    ("A", 10),
    ("B", 20),
    ("A", 15),
    ("C", 5),
    ("B", 25),
    ("A", 8),
    ("C", 12),
    ("B", 30),
]
WHERE_OK = [(c, p) for c, p in PRODUCTOS if p >= 10]
GROUPS = {
    "A": [p for c, p in WHERE_OK if c == "A"],
    "B": [p for c, p in WHERE_OK if c == "B"],
    "C": [p for c, p in WHERE_OK if c == "C"],
}
GROUP_ORDER = ["A", "B", "C"]  # orden estable, alfabético
COUNTS = {c: len(GROUPS[c]) for c in GROUP_ORDER}
HAVING_OK = [c for c in GROUP_ORDER if COUNTS[c] >= 2]  # A, B
ORDERED = sorted(HAVING_OK, key=lambda c: (-COUNTS[c], c))  # B, A
FETCHED = ORDERED[:1]  # B


def _stack_y(top, n, size=CELL, gap=GAP):
    """Centros y (de arriba hacia abajo) de n celdas cuyo borde superior está en top."""
    ys = []
    y = top - size / 2
    for _ in range(n):
        ys.append(y)
        y -= size + gap
    return ys


def _col_width_two():
    return 2 * CELL + GAP + 0.10


# ===========================================================================
# 1. Orden lógico de ejecución
# ===========================================================================

def diagrama_orden_logico():
    # 7 etapas: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, FETCH FIRST
    # GROUP BY incluye las llaves y el COUNT, para no alargar de más.
    col_w = 1.55
    two_w = 1.22
    one_w = 1.00
    count_w = 0.85
    # FROM two-col, WHERE two-col, GROUP BY (cells+dash), COUNT, HAVING, SELECT, ORDER BY, FETCH
    widths = [two_w, two_w, 1.28, count_w, 0.95, 1.05, 1.05, 1.00]
    gaps = [0.28, 0.28, 0.42, 0.28, 0.28, 0.28, 0.28]
    left_m, right_m, top_m, bot_m = 0.25, 0.25, 1.35, 0.85
    n_from = len(PRODUCTOS)
    body_h = n_from * CELL + (n_from - 1) * GAP + 0.20
    width = left_m + sum(widths) + sum(gaps) + right_m
    height = top_m + HEAD_H + 0.16 + body_h + bot_m
    fig, ax = new_canvas(width, height)

    sql_banner(
        ax,
        left_m,
        height - 0.10,
        "Aunque se escribe primero  SELECT,  el motor evalúa las cláusulas en este orden:",
        fontsize=9.0,
    )
    sql_banner(
        ax,
        left_m,
        height - 0.42,
        "SELECT categoria, COUNT(*) AS n   FROM productos   WHERE precio >= 10\n"
        "GROUP BY categoria   HAVING COUNT(*) >= 2   ORDER BY n DESC   FETCH FIRST 1 ROW ONLY",
        fontsize=8.0,
    )

    y_head = height - top_m - HEAD_H
    y_body_top = y_head - 0.16
    xs = []
    x = left_m
    for i, w in enumerate(widths):
        xs.append(x)
        x += w + (gaps[i] if i < len(gaps) else 0)

    # ---- FROM ----
    header_box(ax, xs[0], y_head, widths[0], HEAD_H, "FROM")
    cx1 = xs[0] + widths[0] / 2 - (CELL + GAP) / 2
    cx2 = xs[0] + widths[0] / 2 + (CELL + GAP) / 2
    # fila de encabezado de columnas
    y_hdr = y_body_top - CELL / 2
    cell(ax, cx1, y_hdr, "", fill=WHITE, fontsize=8)
    cell(ax, cx2, y_hdr, "", fill=WHITE, edge=CRIMSON, fontsize=8)
    # etiqueta diminuta sobre las celdas vacías no: mejor un caption debajo de la columna
    ys = _stack_y(y_body_top - CELL - GAP, len(PRODUCTOS))
    for (cat, precio), y in zip(PRODUCTOS, ys):
        cell(ax, cx1, y, cat, fill=CAT_FILL[cat])
        cell(ax, cx2, y, precio, fill=WHITE, edge=CRIMSON)
    caption(ax, xs[0] + widths[0] / 2, ys[-1] - CELL / 2 - 0.10, "tabla  productos\n(categoria, precio)")

    # ---- WHERE ----
    header_box(
        ax,
        xs[1],
        y_head,
        widths[1],
        HEAD_H,
        "WHERE",
        icons=[{"text": "≥10", "fill": WHITE, "edge": CRIMSON, "stack": True}],
        fontsize=10,
    )
    cx1w = xs[1] + widths[1] / 2 - (CELL + GAP) / 2
    cx2w = xs[1] + widths[1] / 2 + (CELL + GAP) / 2
    cell(ax, cx1w, y_hdr, "", fill=WHITE)
    cell(ax, cx2w, y_hdr, "", fill=WHITE, edge=CRIMSON)
    ys_w = _stack_y(y_body_top - CELL - GAP, len(WHERE_OK))
    for (cat, precio), y in zip(WHERE_OK, ys_w):
        cell(ax, cx1w, y, cat, fill=CAT_FILL[cat])
        cell(ax, cx2w, y, precio, fill=WHITE, edge=CRIMSON)
    caption(ax, xs[1] + widths[1] / 2, ys_w[-1] - CELL / 2 - 0.10, "filtra filas\nprecio ≥ 10")

    # ---- GROUP BY ----
    header_box(
        ax,
        xs[2],
        y_head,
        widths[2],
        HEAD_H,
        "GROUP\nBY",
        icons=[{"text": "", "fill": CAT_FILL[c], "edge": NAVY, "stack": True} for c in GROUP_ORDER],
        fontsize=10,
    )
    cxg = xs[2] + widths[2] / 2
    # Place groups from the same body top, with a little extra gap between groups.
    group_gap = 0.20
    y_cursor = y_body_top - CELL - GAP  # skip header row alignment; start at first data row level
    group_spans = []  # (cat, y_top_edge, y_bot_edge, ys)
    for i, cat in enumerate(GROUP_ORDER):
        vals = GROUPS[cat]
        ys_g = _stack_y(y_cursor, len(vals))
        for precio, y in zip(vals, ys_g):
            cell(ax, cxg, y, precio, fill=CAT_FILL[cat], edge=CRIMSON)
        y_top_edge = ys_g[0] + CELL / 2 + 0.06
        y_bot_edge = ys_g[-1] - CELL / 2 - 0.06
        pad_x = 0.10
        dashed_box(ax, cxg - CELL / 2 - pad_x, y_bot_edge, CELL + 2 * pad_x, y_top_edge - y_bot_edge)
        group_spans.append((cat, y_top_edge, y_bot_edge, ys_g))
        y_cursor = ys_g[-1] - CELL / 2 - group_gap

    # ---- COUNT (braces + result) ----
    header_box(
        ax,
        xs[3],
        y_head,
        widths[3],
        HEAD_H,
        "COUNT(*)",
        fontsize=9.5,
    )
    cxc = xs[3] + widths[3] / 2
    for cat, y_top_edge, y_bot_edge, ys_g in group_spans:
        # brace from right of dashed box to the count cell
        brace_x = xs[2] + widths[2] + 0.02
        tip_x, tip_y = curly_brace(ax, brace_x, y_bot_edge + 0.02, y_top_edge - 0.02, depth=0.18)
        # mid of the group
        mid = (ys_g[0] + ys_g[-1]) / 2
        cell(ax, cxc, mid, COUNTS[cat], fill=CAT_FILL[cat])
        # short connector from brace tip to cell
        ax.plot([tip_x, cxc - CELL / 2 - 0.01], [tip_y, mid], color=NAVY, lw=1.3, zorder=3, solid_capstyle="round")
    caption(ax, (xs[2] + xs[3] + widths[3]) / 2, group_spans[-1][2] - 0.10, "una fila por grupo")

    # ---- HAVING ----
    header_box(
        ax,
        xs[4],
        y_head,
        widths[4],
        HEAD_H,
        "HAVING",
        icons=[{"text": "≥2", "fill": WHITE, "edge": NAVY}],
        fontsize=10,
    )
    cxh = xs[4] + widths[4] / 2
    having_ys = []
    for cat, y_top_edge, y_bot_edge, ys_g in group_spans:
        mid = (ys_g[0] + ys_g[-1]) / 2
        if cat in HAVING_OK:
            cell(ax, cxh, mid, COUNTS[cat], fill=CAT_FILL[cat])
            having_ys.append((cat, mid))
    caption(ax, xs[4] + widths[4] / 2, group_spans[-1][2] - 0.10, "filtra grupos\nCOUNT(*) ≥ 2")

    # ---- SELECT ----
    header_box(
        ax,
        xs[5],
        y_head,
        widths[5],
        HEAD_H,
        "SELECT",
        icons=[{"text": "", "fill": WHITE, "edge": NAVY}],
        fontsize=10,
    )
    cxs1 = xs[5] + widths[5] / 2 - (CELL + GAP) / 2
    cxs2 = xs[5] + widths[5] / 2 + (CELL + GAP) / 2
    # alinear con las filas de HAVING
    for cat, mid in having_ys:
        cell(ax, cxs1, mid, cat, fill=CAT_FILL[cat])
        cell(ax, cxs2, mid, COUNTS[cat], fill=CAT_FILL[cat])
    caption(ax, xs[5] + widths[5] / 2, group_spans[-1][2] - 0.10, "categoria, n")

    # ---- ORDER BY ----
    header_box(ax, xs[6], y_head, widths[6], HEAD_H, "ORDER BY", fontsize=10)
    cxo1 = xs[6] + widths[6] / 2 - (CELL + GAP) / 2
    cxo2 = xs[6] + widths[6] / 2 + (CELL + GAP) / 2
    # Place ordered rows starting at the first having y, downward with normal gap
    if having_ys:
        top_mid = max(y for _, y in having_ys)
        ys_o = _stack_y(top_mid + CELL / 2, len(ORDERED))
        for cat, y in zip(ORDERED, ys_o):
            cell(ax, cxo1, y, cat, fill=CAT_FILL[cat])
            cell(ax, cxo2, y, COUNTS[cat], fill=CAT_FILL[cat])
        caption(ax, xs[6] + widths[6] / 2, ys_o[-1] - CELL / 2 - 0.10, "n  descendente")

    # ---- FETCH FIRST ----
    header_box(ax, xs[7], y_head, widths[7], HEAD_H, "FETCH\nFIRST", fontsize=10)
    cxf1 = xs[7] + widths[7] / 2 - (CELL + GAP) / 2
    cxf2 = xs[7] + widths[7] / 2 + (CELL + GAP) / 2
    if having_ys:
        top_mid = max(y for _, y in having_ys)
        ys_f = _stack_y(top_mid + CELL / 2, len(FETCHED))
        for cat, y in zip(FETCHED, ys_f):
            cell(ax, cxf1, y, cat, fill=CAT_FILL[cat])
            cell(ax, cxf2, y, COUNTS[cat], fill=CAT_FILL[cat])
        caption(ax, xs[7] + widths[7] / 2, ys_f[-1] - CELL / 2 - 0.10, "1 fila")

    return save(fig, "diagrama_orden_logico")


# ===========================================================================
# 2. WHERE frente a HAVING
# ===========================================================================

def diagrama_where_having():
    two_w = 1.22
    one_w = 0.95
    count_w = 0.85
    widths = [two_w, two_w, 1.28, count_w, 0.95]
    gaps = [0.28, 0.28, 0.42, 0.28]
    left_m, right_m, top_m, bot_m = 0.25, 0.25, 1.20, 0.85
    n_from = len(PRODUCTOS)
    body_h = n_from * CELL + (n_from - 1) * GAP + 0.20
    width = left_m + sum(widths) + sum(gaps) + right_m
    height = top_m + HEAD_H + 0.16 + body_h + bot_m
    fig, ax = new_canvas(width, height)

    sql_banner(
        ax,
        left_m,
        height - 0.10,
        "WHERE  filtra filas antes de agrupar.    HAVING  filtra grupos después de agregar.",
        fontsize=9.0,
    )
    sql_banner(
        ax,
        left_m,
        height - 0.40,
        "FROM productos    WHERE precio >= 10    GROUP BY categoria    HAVING COUNT(*) >= 2",
        fontsize=8.0,
    )

    y_head = height - top_m - HEAD_H
    y_body_top = y_head - 0.16
    xs = []
    x = left_m
    for i, w in enumerate(widths):
        xs.append(x)
        x += w + (gaps[i] if i < len(gaps) else 0)

    y_hdr = y_body_top - CELL / 2

    # FROM
    header_box(ax, xs[0], y_head, widths[0], HEAD_H, "FROM")
    cx1 = xs[0] + widths[0] / 2 - (CELL + GAP) / 2
    cx2 = xs[0] + widths[0] / 2 + (CELL + GAP) / 2
    cell(ax, cx1, y_hdr, "", fill=WHITE)
    cell(ax, cx2, y_hdr, "", fill=WHITE, edge=CRIMSON)
    ys = _stack_y(y_body_top - CELL - GAP, len(PRODUCTOS))
    for (cat, precio), y in zip(PRODUCTOS, ys):
        cell(ax, cx1, y, cat, fill=CAT_FILL[cat])
        cell(ax, cx2, y, precio, fill=WHITE, edge=CRIMSON)
    caption(ax, xs[0] + widths[0] / 2, ys[-1] - CELL / 2 - 0.10, "tabla  productos")

    # WHERE
    header_box(
        ax,
        xs[1],
        y_head,
        widths[1],
        HEAD_H,
        "WHERE",
        icons=[{"text": "≥10", "fill": WHITE, "edge": CRIMSON}],
        fontsize=10,
    )
    cx1w = xs[1] + widths[1] / 2 - (CELL + GAP) / 2
    cx2w = xs[1] + widths[1] / 2 + (CELL + GAP) / 2
    cell(ax, cx1w, y_hdr, "", fill=WHITE)
    cell(ax, cx2w, y_hdr, "", fill=WHITE, edge=CRIMSON)
    ys_w = _stack_y(y_body_top - CELL - GAP, len(WHERE_OK))
    for (cat, precio), y in zip(WHERE_OK, ys_w):
        cell(ax, cx1w, y, cat, fill=CAT_FILL[cat])
        cell(ax, cx2w, y, precio, fill=WHITE, edge=CRIMSON)
    caption(ax, xs[1] + widths[1] / 2, ys_w[-1] - CELL / 2 - 0.10, "filtra filas\n(se descartan C 5 y A 8)")

    # GROUP BY
    header_box(
        ax,
        xs[2],
        y_head,
        widths[2],
        HEAD_H,
        "GROUP\nBY",
        icons=[{"text": "", "fill": CAT_FILL[c], "edge": NAVY, "stack": True} for c in GROUP_ORDER],
        fontsize=10,
    )
    cxg = xs[2] + widths[2] / 2
    group_gap = 0.20
    y_cursor = y_body_top - CELL - GAP
    group_spans = []
    for cat in GROUP_ORDER:
        vals = GROUPS[cat]
        ys_g = _stack_y(y_cursor, len(vals))
        for precio, y in zip(vals, ys_g):
            cell(ax, cxg, y, precio, fill=CAT_FILL[cat], edge=CRIMSON)
        y_top_edge = ys_g[0] + CELL / 2 + 0.06
        y_bot_edge = ys_g[-1] - CELL / 2 - 0.06
        pad_x = 0.10
        dashed_box(ax, cxg - CELL / 2 - pad_x, y_bot_edge, CELL + 2 * pad_x, y_top_edge - y_bot_edge)
        group_spans.append((cat, y_top_edge, y_bot_edge, ys_g))
        y_cursor = ys_g[-1] - CELL / 2 - group_gap

    # COUNT
    header_box(ax, xs[3], y_head, widths[3], HEAD_H, "COUNT(*)", fontsize=9.5)
    cxc = xs[3] + widths[3] / 2
    for cat, y_top_edge, y_bot_edge, ys_g in group_spans:
        brace_x = xs[2] + widths[2] + 0.02
        tip_x, tip_y = curly_brace(ax, brace_x, y_bot_edge + 0.02, y_top_edge - 0.02, depth=0.18)
        mid = (ys_g[0] + ys_g[-1]) / 2
        cell(ax, cxc, mid, COUNTS[cat], fill=CAT_FILL[cat])
        ax.plot([tip_x, cxc - CELL / 2 - 0.01], [tip_y, mid], color=NAVY, lw=1.3, zorder=3, solid_capstyle="round")

    # HAVING
    header_box(
        ax,
        xs[4],
        y_head,
        widths[4],
        HEAD_H,
        "HAVING",
        icons=[{"text": "≥2", "fill": WHITE, "edge": NAVY}],
        fontsize=10,
    )
    cxh = xs[4] + widths[4] / 2
    for cat, y_top_edge, y_bot_edge, ys_g in group_spans:
        mid = (ys_g[0] + ys_g[-1]) / 2
        if cat in HAVING_OK:
            cell(ax, cxh, mid, COUNTS[cat], fill=CAT_FILL[cat])
    caption(ax, xs[4] + widths[4] / 2, group_spans[-1][2] - 0.10, "filtra grupos\n(se descarta C, con 1)")

    return save(fig, "diagrama_where_having")


# ===========================================================================
# 3. JOIN y duplicación de filas
# ===========================================================================

def diagrama_join_duplicacion():
    # orders: (1, 2), (2, 1)   — order_id, num_of_item
    # order_items: (1), (1), (2)
    # JOIN: three rows, num_of_item 2 appears twice
    # SUM(num_of_item) = 2+2+1 = 5  (incorrecto; la suma en orders es 3)
    # COUNT(*) = 3
    orders = [("1", 2, "A"), ("2", 1, "B")]  # color by order
    items = [("1", "A"), ("1", "A"), ("2", "B")]
    joined = [("1", 2, "A"), ("1", 2, "A"), ("2", 1, "B")]

    two_w = 1.22
    join_w = 1.22
    agg_w = 0.85
    widths = [two_w, 1.20, join_w, agg_w, agg_w]
    gaps = [0.55, 0.55, 0.42, 0.28]
    left_m, right_m, top_m, bot_m = 0.25, 0.30, 1.15, 0.95
    body_h = 4 * CELL + 3 * GAP + 0.35  # header + 3 join rows + spacing
    width = left_m + sum(widths) + sum(gaps) + right_m
    height = top_m + HEAD_H + 0.16 + body_h + bot_m
    fig, ax = new_canvas(width, height)

    sql_banner(
        ax,
        left_m,
        height - 0.10,
        "Una relación 1:N  repite la fila de la izquierda.  SUM  de una columna de  orders  queda inflada.",
        fontsize=8.8,
    )
    sql_banner(
        ax,
        left_m,
        height - 0.38,
        "FROM orders  JOIN order_items  ON orders.order_id = order_items.order_id",
        fontsize=8.0,
    )

    y_head = height - top_m - HEAD_H
    y_body_top = y_head - 0.16
    xs = []
    x = left_m
    for i, w in enumerate(widths):
        xs.append(x)
        x += w + (gaps[i] if i < len(gaps) else 0)

    y_hdr = y_body_top - CELL / 2

    # orders
    header_box(ax, xs[0], y_head, widths[0], HEAD_H, "orders")
    cx1 = xs[0] + widths[0] / 2 - (CELL + GAP) / 2
    cx2 = xs[0] + widths[0] / 2 + (CELL + GAP) / 2
    cell(ax, cx1, y_hdr, "", fill=WHITE)
    cell(ax, cx2, y_hdr, "", fill=WHITE, edge=CRIMSON)
    # Place order 1 higher, order 2 lower, leaving room so 1 can fan out to two items
    ys_o = _stack_y(y_body_top - CELL - GAP, 2, gap=GAP + CELL + 0.15)
    for (oid, n, g), y in zip(orders, ys_o):
        cell(ax, cx1, y, oid, fill=CAT_FILL[g])
        cell(ax, cx2, y, n, fill=WHITE, edge=CRIMSON)
    caption(ax, xs[0] + widths[0] / 2, ys_o[-1] - CELL / 2 - 0.10, "order_id, num_of_item\nuna fila por orden")

    # order_items
    header_box(ax, xs[1], y_head, widths[1], HEAD_H, "order_items", fontsize=9.5)
    cxi = xs[1] + widths[1] / 2
    cell(ax, cxi, y_hdr, "", fill=WHITE)
    ys_i = _stack_y(y_body_top - CELL - GAP, 3)
    for (oid, g), y in zip(items, ys_i):
        cell(ax, cxi, y, oid, fill=CAT_FILL[g])
    caption(ax, xs[1] + widths[1] / 2, ys_i[-1] - CELL / 2 - 0.10, "order_id\nuna fila por artículo")

    # JOIN result
    header_box(ax, xs[2], y_head, widths[2], HEAD_H, "JOIN")
    cxj1 = xs[2] + widths[2] / 2 - (CELL + GAP) / 2
    cxj2 = xs[2] + widths[2] / 2 + (CELL + GAP) / 2
    cell(ax, cxj1, y_hdr, "", fill=WHITE)
    cell(ax, cxj2, y_hdr, "", fill=WHITE, edge=CRIMSON)
    ys_j = _stack_y(y_body_top - CELL - GAP, 3)
    for (oid, n, g), y in zip(joined, ys_j):
        cell(ax, cxj1, y, oid, fill=CAT_FILL[g])
        cell(ax, cxj2, y, n, fill=WHITE, edge=CRIMSON)
    # dashed box around the two duplicated order-1 rows
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

    # Flechas cortas de cada artículo a la fila del JOIN (la relación 1:N se ve en la caja punteada).
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
    # De la orden 1 salen dos artículos: horquilla 1:N.
    arrow(xs[0] + widths[0] + 0.03, ys_o[0], xs[1] - 0.04, ys_i[0])
    arrow(xs[0] + widths[0] + 0.03, ys_o[0], xs[1] - 0.04, ys_i[1])
    arrow(xs[0] + widths[0] + 0.03, ys_o[1], xs[1] - 0.04, ys_i[2])

    # SUM(num_of_item) incorrect
    header_box(ax, xs[3], y_head, widths[3], HEAD_H, "SUM(n)", fontsize=9.5)
    cxs = xs[3] + widths[3] / 2
    # brace over all three join rows
    y_top_all = ys_j[0] + CELL / 2 + 0.04
    y_bot_all = ys_j[-1] - CELL / 2 - 0.04
    brace_x = xs[2] + widths[2] + 0.02
    tip_x, tip_y = curly_brace(ax, brace_x, y_bot_all, y_top_all, depth=0.18)
    mid_all = (ys_j[0] + ys_j[-1]) / 2
    cell(ax, cxs, mid_all, "5", fill=WHITE, edge=CRIMSON, lw=1.8)
    ax.plot([tip_x, cxs - CELL / 2 - 0.01], [tip_y, mid_all], color=NAVY, lw=1.3, zorder=3, solid_capstyle="round")
    caption(ax, xs[3] + widths[3] / 2, ys_j[-1] - CELL / 2 - 0.10, "suma incorrecta\n(2+2+1 = 5)\nlo correcto es 3")

    # COUNT(*)
    header_box(ax, xs[4], y_head, widths[4], HEAD_H, "COUNT(*)", fontsize=9.5)
    cxc = xs[4] + widths[4] / 2
    cell(ax, cxc, mid_all, "3", fill=WHITE, edge=NAVY)
    caption(ax, xs[4] + widths[4] / 2, ys_j[-1] - CELL / 2 - 0.10, "cuenta las filas\ndel JOIN\n(3 artículos)")

    return save(fig, "diagrama_join_duplicacion")


# ===========================================================================
# 4. Función de ventana frente a GROUP BY
# ===========================================================================

def diagrama_ventana_group_by():
    filas = [("A", 10), ("A", 20), ("B", 15), ("B", 25)]
    # GROUP BY: A 2, B 2  (collapses)
    # ventana: four rows, added column 2, 2, 2, 2
    two_w = 1.22
    gb_w = 1.22
    win_w = 1.55
    widths = [two_w, 1.35, 0.85, win_w]
    gaps = [0.50, 0.40, 0.55]
    left_m, right_m, top_m, bot_m = 0.25, 0.25, 1.05, 0.90
    body_h = 5 * CELL + 4 * GAP + 0.15
    width = left_m + sum(widths) + sum(gaps) + right_m
    height = top_m + HEAD_H + 0.16 + body_h + bot_m
    fig, ax = new_canvas(width, height)

    sql_banner(
        ax,
        left_m,
        height - 0.10,
        "GROUP BY  colapsa las filas a una por grupo.    La función de ventana conserva cada fila y añade una columna.",
        fontsize=8.6,
    )

    y_head = height - top_m - HEAD_H
    y_body_top = y_head - 0.16
    xs = []
    x = left_m
    for i, w in enumerate(widths):
        xs.append(x)
        x += w + (gaps[i] if i < len(gaps) else 0)

    y_hdr = y_body_top - CELL / 2

    # filas de partida
    header_box(ax, xs[0], y_head, widths[0], HEAD_H, "filas")
    cx1 = xs[0] + widths[0] / 2 - (CELL + GAP) / 2
    cx2 = xs[0] + widths[0] / 2 + (CELL + GAP) / 2
    cell(ax, cx1, y_hdr, "", fill=WHITE)
    cell(ax, cx2, y_hdr, "", fill=WHITE, edge=CRIMSON)
    ys = _stack_y(y_body_top - CELL - GAP, len(filas))
    for (cat, val), y in zip(filas, ys):
        cell(ax, cx1, y, cat, fill=CAT_FILL[cat])
        cell(ax, cx2, y, val, fill=WHITE, edge=CRIMSON)
    caption(ax, xs[0] + widths[0] / 2, ys[-1] - CELL / 2 - 0.10, "categoria, valor")

    # GROUP BY groups
    header_box(
        ax,
        xs[1],
        y_head,
        widths[1],
        HEAD_H,
        "GROUP\nBY",
        icons=[{"text": "", "fill": GREEN, "edge": NAVY, "stack": True}, {"text": "", "fill": BLUE, "edge": NAVY, "stack": True}],
        fontsize=10,
    )
    cxg = xs[1] + widths[1] / 2 - (CELL + GAP) / 2
    # show the values grouped
    ys_a = [ys[0], ys[1]]
    ys_b = [ys[2], ys[3]]
    for val, y in zip((10, 20), ys_a):
        cell(ax, xs[1] + widths[1] / 2, y, val, fill=GREEN, edge=CRIMSON)
    for val, y in zip((15, 25), ys_b):
        cell(ax, xs[1] + widths[1] / 2, y, val, fill=BLUE, edge=CRIMSON)
    for ys_g, fill in ((ys_a, GREEN), (ys_b, BLUE)):
        y_top_edge = ys_g[0] + CELL / 2 + 0.03
        y_bot_edge = ys_g[-1] - CELL / 2 - 0.03
        pad_x = 0.10
        cx = xs[1] + widths[1] / 2
        dashed_box(ax, cx - CELL / 2 - pad_x, y_bot_edge, CELL + 2 * pad_x, y_top_edge - y_bot_edge)

    # COUNT collapsed
    header_box(ax, xs[2], y_head, widths[2], HEAD_H, "COUNT(*)", fontsize=9.5)
    cxc = xs[2] + widths[2] / 2
    mids = []
    for ys_g, cat, n in ((ys_a, "A", 2), (ys_b, "B", 2)):
        y_top_edge = ys_g[0] + CELL / 2 + 0.06
        y_bot_edge = ys_g[-1] - CELL / 2 - 0.06
        brace_x = xs[1] + widths[1] + 0.02
        tip_x, tip_y = curly_brace(ax, brace_x, y_bot_edge + 0.02, y_top_edge - 0.02, depth=0.16)
        mid = (ys_g[0] + ys_g[-1]) / 2
        cell(ax, cxc, mid, n, fill=CAT_FILL[cat])
        ax.plot([tip_x, cxc - CELL / 2 - 0.01], [tip_y, mid], color=NAVY, lw=1.3, zorder=3, solid_capstyle="round")
        mids.append(mid)
    caption(ax, (xs[1] + xs[2] + widths[2]) / 2, ys[-1] - CELL / 2 - 0.10, "colapsa a una fila\npor grupo")

    # ventana: all rows + new column
    header_box(ax, xs[3], y_head, widths[3], HEAD_H, "función de ventana", fontsize=9.5)
    # 3 columns: cat, val, count
    span = 3 * CELL + 2 * GAP
    c0 = xs[3] + widths[3] / 2 - span / 2 + CELL / 2
    c1 = c0 + CELL + GAP
    c2 = c1 + CELL + GAP
    cell(ax, c0, y_hdr, "", fill=WHITE)
    cell(ax, c1, y_hdr, "", fill=WHITE, edge=CRIMSON)
    cell(ax, c2, y_hdr, "", fill=WHITE, edge=NAVY)
    for (cat, val), y in zip(filas, ys):
        cell(ax, c0, y, cat, fill=CAT_FILL[cat])
        cell(ax, c1, y, val, fill=WHITE, edge=CRIMSON)
        cell(ax, c2, y, 2, fill=CAT_FILL[cat])
    caption(ax, xs[3] + widths[3] / 2, ys[-1] - CELL / 2 - 0.10, "conserva cada fila\ny añade la cuenta")

    return save(fig, "diagrama_ventana_group_by")


# ===========================================================================
# 5. Álgebra relacional
# ===========================================================================

def diagrama_algebra_relacional():
    # Relación A (id, grupo): 1 a, 2 b, 3 a
    # Relación B (id, a_id):  10 1, 20 2, 30 3
    # JOIN ON A.id = B.a_id (1:1): (1,a,10), (2,b,20), (3,a,30)
    # Selección WHERE grupo = 'a': (1,a,10), (3,a,30)
    # Proyección SELECT id (de A), grupo: (1,a), (3,a)
    A = [("1", "A"), ("2", "B"), ("3", "A")]
    B = [("10", "1", "A"), ("20", "2", "B"), ("30", "3", "A")]
    joined = [("1", "A", "10"), ("2", "B", "20"), ("3", "A", "30")]
    selected = [("1", "A", "10"), ("3", "A", "30")]
    projected = [("1", "A"), ("3", "A")]

    two_w = 1.15
    three_w = 1.55
    widths = [two_w, two_w, three_w, three_w, two_w]
    gaps = [0.32, 0.48, 0.36, 0.36]
    left_m, right_m, top_m, bot_m = 0.25, 0.25, 1.00, 0.85
    body_h = 5 * CELL + 4 * GAP + 0.2
    width = left_m + sum(widths) + sum(gaps) + right_m
    height = top_m + HEAD_H + 0.16 + body_h + bot_m
    fig, ax = new_canvas(width, height)

    sql_banner(
        ax,
        left_m,
        height - 0.10,
        "Las operaciones se componen:  combinación,  después selección,  después proyección.",
        fontsize=9.0,
    )

    y_head = height - top_m - HEAD_H
    y_body_top = y_head - 0.16
    xs = []
    x = left_m
    for i, w in enumerate(widths):
        xs.append(x)
        x += w + (gaps[i] if i < len(gaps) else 0)

    y_hdr = y_body_top - CELL / 2

    def two_col(x0, w, rows, fills, edges2, y_start):
        c1 = x0 + w / 2 - (CELL + GAP) / 2
        c2 = x0 + w / 2 + (CELL + GAP) / 2
        cell(ax, c1, y_hdr, "", fill=WHITE)
        cell(ax, c2, y_hdr, "", fill=WHITE, edge=CRIMSON)
        ys = _stack_y(y_start, len(rows))
        for (a, b), y, fill in zip(rows, ys, fills):
            cell(ax, c1, y, a, fill=fill)
            cell(ax, c2, y, b, fill=WHITE, edge=edges2)
        return ys, c1, c2

    def three_col(x0, w, rows, y_start):
        span = 3 * CELL + 2 * GAP
        c0 = x0 + w / 2 - span / 2 + CELL / 2
        c1 = c0 + CELL + GAP
        c2 = c1 + CELL + GAP
        cell(ax, c0, y_hdr, "", fill=WHITE)
        cell(ax, c1, y_hdr, "", fill=WHITE)
        cell(ax, c2, y_hdr, "", fill=WHITE, edge=CRIMSON)
        ys = _stack_y(y_start, len(rows))
        for (a, g, b), y in zip(rows, ys):
            fill = CAT_FILL[g]
            cell(ax, c0, y, a, fill=fill)
            cell(ax, c1, y, g, fill=fill)
            cell(ax, c2, y, b, fill=WHITE, edge=CRIMSON)
        return ys

    y_data = y_body_top - CELL - GAP

    header_box(ax, xs[0], y_head, widths[0], HEAD_H, "relación A", fontsize=10)
    ys_a, *_ = two_col(
        xs[0], widths[0], [(i, g) for i, g in A], [CAT_FILL[g] for _, g in A], CRIMSON, y_data
    )
    caption(ax, xs[0] + widths[0] / 2, ys_a[-1] - CELL / 2 - 0.10, "id, grupo")

    header_box(ax, xs[1], y_head, widths[1], HEAD_H, "relación B", fontsize=10)
    # B shown as (id, a_id) — color a_id by the matching A group
    c1 = xs[1] + widths[1] / 2 - (CELL + GAP) / 2
    c2 = xs[1] + widths[1] / 2 + (CELL + GAP) / 2
    cell(ax, c1, y_hdr, "", fill=WHITE)
    cell(ax, c2, y_hdr, "", fill=WHITE, edge=CRIMSON)
    ys_b = _stack_y(y_data, len(B))
    for (bid, aid, g), y in zip(B, ys_b):
        cell(ax, c1, y, bid, fill=WHITE, edge=NAVY)
        cell(ax, c2, y, aid, fill=CAT_FILL[g], edge=CRIMSON)
    caption(ax, xs[1] + widths[1] / 2, ys_b[-1] - CELL / 2 - 0.10, "id, a_id")

    header_box(ax, xs[2], y_head, widths[2], HEAD_H, "combinación\nJOIN", fontsize=10)
    ys_j = three_col(xs[2], widths[2], joined, y_data)
    caption(ax, xs[2] + widths[2] / 2, ys_j[-1] - CELL / 2 - 0.10, "A.id = B.a_id")

    header_box(ax, xs[3], y_head, widths[3], HEAD_H, "selección\nWHERE", fontsize=10)
    ys_s = three_col(xs[3], widths[3], selected, y_data)
    caption(ax, xs[3] + widths[3] / 2, ys_s[-1] - CELL / 2 - 0.10, "grupo = A")

    header_box(ax, xs[4], y_head, widths[4], HEAD_H, "proyección\nSELECT", fontsize=10)
    ys_p, *_ = two_col(
        xs[4],
        widths[4],
        projected,
        [CAT_FILL[g] for _, g in projected],
        CRIMSON,
        y_data,
    )
    caption(ax, xs[4] + widths[4] / 2, ys_p[-1] - CELL / 2 - 0.10, "id, grupo")

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
