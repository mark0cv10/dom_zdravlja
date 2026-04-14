#!/usr/bin/env python3
"""
Generisanje use-case dijagrama za Izdavačku kuću u stilu Visual Paradigm.
Koristi Pillow (PIL).
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Boje (Visual Paradigm stil) ──────────────────────────────
WHITE = (255, 255, 255)
BG_COLOR = (252, 252, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (240, 240, 240)

# Actor boje
ACTOR_COLOR = (60, 60, 60)

# Use case boje — Visual Paradigm svijetloplava
UC_FILL = (220, 235, 255)
UC_OUTLINE = (80, 130, 200)

# System boundary
SYS_FILL = (248, 250, 255)
SYS_OUTLINE = (100, 100, 160)

# Veze
ASSOC_COLOR = (50, 50, 50)
EXTEND_COLOR = (100, 100, 180)
INHERIT_COLOR = (60, 60, 60)

# ── Font utility ─────────────────────────────────────────────
def get_font(size=14, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


# ── Crtanje stick-figure aktora ──────────────────────────────
def draw_actor(draw, cx, cy, label, font, label_color=BLACK):
    """Crta stick-figure aktora sa labelom ispod."""
    head_r = 10
    body_len = 28
    arm_len = 18
    leg_len = 22
    lw = 2

    # Glava
    draw.ellipse(
        (cx - head_r, cy - head_r, cx + head_r, cy + head_r),
        outline=ACTOR_COLOR, width=lw
    )
    # Tijelo
    body_top = cy + head_r
    body_bot = body_top + body_len
    draw.line([(cx, body_top), (cx, body_bot)], fill=ACTOR_COLOR, width=lw)
    # Ruke
    arm_y = body_top + 10
    draw.line([(cx - arm_len, arm_y), (cx + arm_len, arm_y)], fill=ACTOR_COLOR, width=lw)
    # Noge
    draw.line([(cx, body_bot), (cx - leg_len * 0.7, body_bot + leg_len)], fill=ACTOR_COLOR, width=lw)
    draw.line([(cx, body_bot), (cx + leg_len * 0.7, body_bot + leg_len)], fill=ACTOR_COLOR, width=lw)

    # Label ispod
    tw, th = text_size(draw, label, font)
    label_y = body_bot + leg_len + 5
    draw.text((cx - tw // 2, label_y), label, fill=label_color, font=font)

    # Vrati bounding box centar za povezivanje linija
    total_h = head_r * 2 + body_len + leg_len
    return cx, cy + total_h // 2  # sredina figure


def actor_bbox(cy):
    """Vrati y-range aktora za konekcije."""
    head_r = 10
    body_len = 28
    leg_len = 22
    top = cy - head_r
    bot = cy + head_r + body_len + leg_len
    return top, bot


# ── Crtanje use-case elipse ─────────────────────────────────
def draw_usecase(draw, cx, cy, text_str, font, ew=None, eh=40):
    """Crta use-case elipsu sa tekstom unutra."""
    tw, th = text_size(draw, text_str, font)
    if ew is None:
        ew = max(tw + 40, 160)
    # Elipsa
    draw.ellipse(
        (cx - ew // 2, cy - eh // 2, cx + ew // 2, cy + eh // 2),
        fill=UC_FILL, outline=UC_OUTLINE, width=2
    )
    # Tekst
    draw.text((cx - tw // 2, cy - th // 2), text_str, fill=BLACK, font=font)
    return ew, eh


# ── Crtanje linije (asocijacija) ────────────────────────────
def draw_line(draw, x1, y1, x2, y2, color=ASSOC_COLOR, width=2):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)


# ── Crtanje dashed linije sa strelicom (<<extend>>) ─────────
def draw_dashed_arrow(draw, x1, y1, x2, y2, label="«extend»", font=None, color=EXTEND_COLOR, width=2):
    """Crta dashed liniju sa otvorenom strelicom i labelom."""
    # Dashed linija — segmenti
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    if dist == 0:
        return
    dash_len = 8
    gap_len = 5
    dx = (x2 - x1) / dist
    dy = (y2 - y1) / dist
    d = 0
    while d < dist:
        seg_end = min(d + dash_len, dist)
        sx = x1 + dx * d
        sy = y1 + dy * d
        ex = x1 + dx * seg_end
        ey = y1 + dy * seg_end
        draw.line([(sx, sy), (ex, ey)], fill=color, width=width)
        d += dash_len + gap_len

    # Otvorena strelica na kraju
    angle = math.atan2(y2 - y1, x2 - x1)
    arrow_len = 12
    lx = x2 - arrow_len * math.cos(angle - 0.35)
    ly = y2 - arrow_len * math.sin(angle - 0.35)
    rx = x2 - arrow_len * math.cos(angle + 0.35)
    ry = y2 - arrow_len * math.sin(angle + 0.35)
    draw.line([(lx, ly), (x2, y2)], fill=color, width=width)
    draw.line([(rx, ry), (x2, y2)], fill=color, width=width)

    # Label na sredini
    if font:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        tw, th = text_size(draw, label, font)
        # Offset okomito na liniju
        nx = -dy * 12
        ny = dx * 12
        draw.text((int(mx + nx - tw / 2), int(my + ny - th / 2)), label, fill=color, font=font)


# ── Inheritance strelica (trokut) ────────────────────────────
def draw_inheritance_arrow(draw, x1, y1, x2, y2, color=INHERIT_COLOR, width=2):
    """Linija sa praznim trokutom na kraju (generalizacija)."""
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    arrow_len = 14
    p1 = (x2, y2)
    p2 = (x2 - arrow_len * math.cos(angle - 0.4), y2 - arrow_len * math.sin(angle - 0.4))
    p3 = (x2 - arrow_len * math.cos(angle + 0.4), y2 - arrow_len * math.sin(angle + 0.4))
    draw.polygon([p1, p2, p3], fill=WHITE, outline=color)


# ── Tačka na elipsi najbliža datoj tački ────────────────────
def ellipse_edge_point(cx, cy, ew, eh, tx, ty):
    """Tačka na elipsi (cx,cy,ew,eh) najbliža vanjskoj tački (tx,ty)."""
    angle = math.atan2(ty - cy, tx - cx)
    a = ew / 2
    b = eh / 2
    x = cx + a * math.cos(angle)
    y = cy + b * math.sin(angle)
    return int(x), int(y)


# ══════════════════════════════════════════════════════════════
# GLAVNI DIJAGRAM
# ══════════════════════════════════════════════════════════════
def generate():
    W, H = 1500, 1100
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    title_font = get_font(22, bold=True)
    actor_font = get_font(12, bold=True)
    uc_font = get_font(12)
    small_font = get_font(10)
    extend_font = get_font(10)

    # ── Naslov ────────────────────────────────────────────────
    title = "Use Case dijagram — Izdavačka kuća"
    tw, _ = text_size(draw, title, title_font)
    draw.text(((W - tw) // 2, 18), title, fill=(40, 40, 100), font=title_font)

    # ── System boundary ──────────────────────────────────────
    SYS_X = 380
    SYS_Y = 65
    SYS_W = 780
    SYS_H = 1000
    draw.rounded_rectangle(
        (SYS_X, SYS_Y, SYS_X + SYS_W, SYS_Y + SYS_H),
        radius=18, fill=SYS_FILL, outline=SYS_OUTLINE, width=2
    )
    sys_title = "Izdavačka kuća"
    stw, sth = text_size(draw, sys_title, get_font(16, bold=True))
    draw.text((SYS_X + (SYS_W - stw) // 2, SYS_Y + 8), sys_title, fill=SYS_OUTLINE, font=get_font(16, bold=True))

    # ── Pozicije use-case-ova (unutar system boundary) ───────
    # Raspoređeni u 3 kolone
    uc_cx_left = SYS_X + 200
    uc_cx_mid = SYS_X + 400
    uc_cx_right = SYS_X + 590

    uc_ew = 240  # širina elipse
    uc_eh = 42   # visina elipse

    # Definicije: id -> (label, cx, cy)
    usecases = {
        "UC1":  ("Registracija",                       uc_cx_left,   135),
        "UC2":  ("Pregled kataloga knjiga",             uc_cx_left,   205),
        "UC3":  ("Prijava",                             uc_cx_left,   285),
        "UC4":  ("Podešavanje profila",                 uc_cx_left,   355),
        "UC5":  ("Odjava",                              uc_cx_left,   425),
        "UC6":  ("Naručivanje knjiga",                  uc_cx_mid,    205),
        "UC7":  ("Pregled istorije narudžbi",           uc_cx_mid,    290),
        "UC8":  ("Otkazivanje narudžbe",                uc_cx_mid,    375),
        "UC9":  ("Predaja rukopisa",                    uc_cx_left,   510),
        "UC10": ("Pregled statusa rukopisa",            uc_cx_left,   580),
        "UC11": ("Pregled liste pristiglih rukopisa",   uc_cx_right,  510),
        "UC12": ("Recenzija rukopisa",                  uc_cx_right,  580),
        "UC13": ("Upravljanje procesom uređivanja",     uc_cx_right,  655),
        "UC14": ("Odobravanje knjige za štampu",        uc_cx_right,  730),
        "UC15": ("Pregled korisnika",                   uc_cx_right,  830),
        "UC16": ("Unos korisnika",                      uc_cx_right,  900),
        "UC17": ("Izmjena korisnika",                   uc_cx_right,  970),
        "UC18": ("Brisanje korisnika",                  uc_cx_right,  1040),
    }

    # Nacrtaj use-case elipse
    uc_dims = {}
    for uid, (label, cx, cy) in usecases.items():
        ew_actual, eh_actual = draw_usecase(draw, cx, cy, label, uc_font, ew=uc_ew, eh=uc_eh)
        uc_dims[uid] = (cx, cy, ew_actual, eh_actual)

    # ── Pozicije aktora ──────────────────────────────────────
    # Lijevi akteri
    actor_x_left = 120
    actor_x_right = SYS_X + SYS_W + 130

    actors = {
        "Gost":          (actor_x_left,  170),
        "Korisnik":      (actor_x_left,  355),
        "Kupac":         (actor_x_left,  560),
        "Autor":         (actor_x_left,  750),
        "Urednik":       (actor_x_right, 630),
        "Administrator": (actor_x_right, 920),
    }

    # Nacrtaj aktore
    for name, (ax, ay) in actors.items():
        draw_actor(draw, ax, ay, name, actor_font)

    # ── Asocijacije (actor -> use case) ──────────────────────
    associations = [
        ("Gost", "UC1"),
        ("Gost", "UC2"),
        ("Korisnik", "UC3"),
        ("Korisnik", "UC4"),
        ("Korisnik", "UC5"),
        ("Kupac", "UC2"),
        ("Kupac", "UC6"),
        ("Kupac", "UC7"),
        ("Autor", "UC9"),
        ("Autor", "UC10"),
        ("Urednik", "UC11"),
        ("Urednik", "UC12"),
        ("Urednik", "UC13"),
        ("Urednik", "UC14"),
        ("Administrator", "UC15"),
        ("Administrator", "UC16"),
        ("Administrator", "UC17"),
        ("Administrator", "UC18"),
    ]

    for actor_name, uc_id in associations:
        ax, ay = actors[actor_name]
        cx, cy, ew, eh = uc_dims[uc_id]
        # Tačka na elipsi najbliža aktoru
        ex, ey = ellipse_edge_point(cx, cy, ew, eh, ax, ay)
        # Aktor — sredina tijela
        a_top, a_bot = actor_bbox(ay)
        a_mid_y = (a_top + a_bot) // 2
        # Pronadji tačku na aktoru najbližu elipsi
        if ax < cx:
            a_x = ax + 20  # desna strana aktora
        else:
            a_x = ax - 20  # lijeva strana aktora
        draw_line(draw, a_x, a_mid_y, ex, ey, color=ASSOC_COLOR, width=2)

    # ── Inheritance (child --|> parent) ──────────────────────
    inherits = [
        ("Kupac", "Korisnik"),
        ("Autor", "Korisnik"),
        ("Urednik", "Korisnik"),
        ("Administrator", "Korisnik"),
    ]

    for child, parent in inherits:
        cx_c, cy_c = actors[child]
        cx_p, cy_p = actors[parent]
        c_top, c_bot = actor_bbox(cy_c)
        p_top, p_bot = actor_bbox(cy_p)

        # Tačke spajanja
        child_head_top = cy_c - 10
        parent_feet_bot = p_bot + 20  # ispod labele roditelja

        if cx_c == cx_p:
            # Isti stub — vertikalna linija sa strelicom
            draw_inheritance_arrow(draw, cx_c, child_head_top, cx_p, parent_feet_bot,
                                   color=INHERIT_COLOR, width=2)
        else:
            # Razliciti stubovi (Urednik, Administrator desno -> Korisnik lijevo)
            # Lomljena linija: gore od djeteta, horizontalno, pa dolje do roditelja
            bend_y = min(child_head_top, cy_p - 10) - 40  # iznad oba
            # Od djeteta gore do bend_y
            draw_line(draw, cx_c, child_head_top, cx_c, bend_y, color=INHERIT_COLOR, width=2)
            # Horizontalno do roditelja
            draw_line(draw, cx_c, bend_y, cx_p, bend_y, color=INHERIT_COLOR, width=2)
            # Od bend_y dolje do roditelja sa strelicom
            draw_inheritance_arrow(draw, cx_p, bend_y, cx_p, parent_feet_bot,
                                   color=INHERIT_COLOR, width=2)

    # ── Extend relacije ──────────────────────────────────────
    extends = [
        ("UC6", "UC2"),
        ("UC8", "UC7"),
        ("UC12", "UC11"),
        ("UC13", "UC12"),
        ("UC14", "UC13"),
        ("UC16", "UC15"),
        ("UC17", "UC15"),
        ("UC18", "UC15"),
    ]

    for src_id, dst_id in extends:
        src_cx, src_cy, src_ew, src_eh = uc_dims[src_id]
        dst_cx, dst_cy, dst_ew, dst_eh = uc_dims[dst_id]
        # Tačke na ivicama elipsi
        sx, sy = ellipse_edge_point(src_cx, src_cy, src_ew, src_eh, dst_cx, dst_cy)
        dx, dy = ellipse_edge_point(dst_cx, dst_cy, dst_ew, dst_eh, src_cx, src_cy)
        draw_dashed_arrow(draw, sx, sy, dx, dy, label="«extend»", font=extend_font, color=EXTEND_COLOR, width=2)

    # ── Okvir ────────────────────────────────────────────────
    draw.rectangle([(1, 1), (W - 2, H - 2)], outline=GRAY, width=1)

    # ── Sačuvaj ──────────────────────────────────────────────
    out_path = os.path.join(OUTPUT_DIR, "use_case_dijagram.png")
    img.save(out_path, quality=95)
    print(f"✅ Sačuvano: {out_path}")


if __name__ == "__main__":
    generate()

