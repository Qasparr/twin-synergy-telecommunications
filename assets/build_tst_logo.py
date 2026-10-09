#!/usr/bin/env python3
################################################################################
# BUILD_TST_LOGO.py — THE FORGE OF THE TWIN SYNERGY MARK
#
#   "For I am divided for love's sake, for the chance of union."
#       — Liber AL vel Legis, I:29
#
# WHAT THIS PROGRAM IS
#   A vector-logo forge. It computes — from closed-form mathematics, never
#   from a designer's hand — the trademark master of TWIN SYNERGY
#   TELECOMMUNICATIONS, and renders it twice: once as SVG (the master,
#   infinitely scalable) and once as PNG (a 1600px document render via PIL).
#
# THE CONCEPT (dictated meaning, John's doctrine)
#   TWIN  = duality: inner/outer, micro/macro — the two nodes hidden in
#           plain sight, one the micro/inner with an inward eye, one the
#           macro/outer as outward radiance.
#   SYNERGY = the whole beyond its parts: two signal paths phase-locking
#           into one emergent carrier — constructive interference, drawn
#           honestly. The mark is called THE TWIN PHASE-LOCK.
#
# THE GEOMETRY (all of it computed)
#   Two sine waves share one carrier period over the signal span [X0, X1].
#   Their phase split delta(t) collapses from PI (counter-phase — the Twin
#   in opposition, crossing like a flat double helix) to 0 (phase-locked —
#   one form). The arithmetic mean of the two is drawn as a third, brighter
#   stroke: at t=0 it is degenerate (flat on the baseline); it GROWS as the
#   waves lock — the emergent form literally emerging. The ribbon between
#   the two waves is filled gold: a chain of narrowing vesicae (the ancient
#   two-become-one figure), wide at the source, collapsing to a point where
#   the signal pours into the macro ring.
#   The twin nodes bookend the span, exactly tangent to it: the micro disc
#   (gold, indigo heart — the inward eye) at the origin, the bold macro
#   ring (outward radiance, with a faint halo) at the arrival. Beneath it
#   all, a computed diamond lattice on a baseline rule — the shared ground
#   the signals rise from — with hairlines rising at the carrier's
#   zero-crossings to meet the wave nodes: the lattice and the signal are
#   one circuit, joined at computed points.
#
# DESIGN CHOICE, STATED FOR THE RED PEN
#   Twin waveforms were chosen over twin {13/5} star polygons because a
#   telecommunications mark should speak signal, not only sigil — and
#   because phase-lock is the honest physics of synergy. The star-node
#   alternative (two interlocked thirteen-pointed stars) is held OPEN for
#   his ruling; the forge is parameterized so the swap is mechanical.
#
# Date: Sol in Libra 2026 e.v.  Method: Scientific Illuminism.  93.
# Authorship: Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# Notice: All Rights Reserved, Without Prejudice.  Support: CashApp $axoneme
# Forged by the LOGO worker, at his order, from his dictated doctrine.
################################################################################

import math
import os

# --- House colors ------------------------------------------------------------
# MECHANISM: the palette is data, declared once, referenced everywhere — so a
#   red-pen color ruling changes one line, never twenty.
# DOCTRINE: gold on deep indigo is the house of his prior sigil work. The
#   lighter gold HIGHLIGHT is a tint of the house gold (same hue family),
#   used only for the emergent carrier — the synergy is the same gold, lit.
GOLD      = "#d4af37"   # house gold
HIGHLIGHT = "#e8c85e"   # house gold, lit — the emergent carrier only
INDIGO    = "#150826"   # deep indigo field
INK       = "#150826"   # the micro node's heart is the field color itself

# --- The canvas --------------------------------------------------------------
# MECHANISM: one coordinate space (SVG user units). The PNG renderer scales
#   every coordinate by S, so the two renders are the same drawing.
W, H = 1200, 900          # master canvas
S = 1600 / W              # PNG scale factor -> 1600 x 1200 px document render

# --- The signal span ---------------------------------------------------------
# MECHANISM: every x in the mark derives from X0/X1. N samples per curve;
#   721 points over 680 units = sub-pixel smoothness at any sane size.
X0, X1 = 260.0, 940.0     # signal span: twin nodes sit tangent at both ends
Y0     = 480.0            # carrier baseline (the waves oscillate about this)
CYCLES = 3                # carrier cycles across the span — computed, not felt
AMP    = 150.0            # base amplitude; envelope grows it 0.55 -> 1.0
N      = 721              # samples per curve

# --- The twin nodes (hidden in plain sight) ----------------------------------
# MECHANISM: tangency is arithmetic, not eyeballing —
#   disc right edge (240 + 20) == X0 == wave origin;
#   ring left edge (968 - 28) == X1 == wave terminus.
MICRO_C, MICRO_R, HEART_R = (240.0, Y0), 20.0, 6.5     # gold disc, indigo heart
MACRO_C, MACRO_R, MACRO_W = (968.0, Y0), 28.0, 12.0    # bold gold ring
HALO_R = 95.0                                          # outward radiance

# --- The shared lattice base -------------------------------------------------
LATTICE_Y = 560.0         # the ground the signals rise from
LATTICE_N = 25            # diamonds, evenly spaced, computed
LATTICE_X0, LATTICE_X1 = 220.0, 980.0

# --- The wordmark ------------------------------------------------------------
WORD_Y, WORD_SIZE, WORD_TRACK = 712.0, 66.0, 20.0
SUB_Y,  SUB_SIZE,  SUB_TRACK  = 762.0, 23.0, 11.0
RULE_Y, RULE_X0, RULE_X1 = 788.0, 430.0, 770.0
TAG_Y,  TAG_SIZE,  TAG_TRACK  = 820.0, 17.0, 6.0

# === THE MATHEMATICS =========================================================
# MECHANISM: t is normalized position along the span, 0 at the micro node,
#   1 at the macro ring. Everything below is a pure function of t.

def envelope(t):
    # MECHANISM: linear rise 0.55 -> 1.0. The signals are born small at the
    #   source and reach full voice at the ring — ascendance, computed.
    return 0.55 + 0.45 * t

def phase_split(t):
    # MECHANISM: the Twin's separation. At t=0 the waves are PI apart
    #   (counter-phase: sin(x+PI/2) = cos x vs sin(x-PI/2) = -cos x — they
    #   cross at the carrier nodes like a flattened double helix). At t=1
    #   the split is 0: one wave, phase-locked.
    # DOCTRINE: duality resolving into unity is the whole mark in one
    #   function. No hand-drawn morphing — the equation IS the doctrine.
    return (math.pi / 2.0) * (1.0 - t)

def carrier(t):
    # MECHANISM: the shared carrier both waves ride: 3 full cycles.
    return 2.0 * math.pi * CYCLES * t

def wave_a(t):
    # MECHANISM: twin path A — the carrier advanced by half the split.
    return Y0 - AMP * envelope(t) * math.sin(carrier(t) + phase_split(t))

def wave_b(t):
    # MECHANISM: twin path B — the carrier retarded by half the split.
    return Y0 - AMP * envelope(t) * math.sin(carrier(t) - phase_split(t))

def wave_emergent(t):
    # MECHANISM: the arithmetic mean — (A+B)/2 = A*env*cos(split)*sin(car).
    #   At t=0, cos(PI/2) = 0: the emergent form is degenerate, a flat line
    #   on the baseline. It GROWS as the split collapses — synergy as the
    #   constructive-interference gain of two locking signals. Honest
    #   physics: this is what phase-locking two equal carriers does.
    return Y0 - AMP * envelope(t) * math.cos(phase_split(t)) * math.sin(carrier(t))

def sample(fn, n=N):
    # MECHANISM: sample curve fn at n evenly spaced t in [0, 1], mapping t
    #   to x in [X0, X1]. Returns [(x, y), ...].
    return [(X0 + (X1 - X0) * i / (n - 1), fn(i / (n - 1))) for i in range(n)]

def zero_crossings():
    # MECHANISM: the carrier sin(2*PI*3*t) is zero at t = k/6, k = 0..6 —
    #   seven computed points where both waves pierce the baseline. The
    #   lattice hairlines rise exactly here: signal and ground joined at
    #   mathematics, not decoration.
    return [X0 + (X1 - X0) * k / 6.0 for k in range(7)]

def lattice_points():
    # MECHANISM: LATTICE_N diamonds evenly spaced across the base.
    return [LATTICE_X0 + (LATTICE_X1 - LATTICE_X0) * i / (LATTICE_N - 1)
            for i in range(LATTICE_N)]

# === THE SVG MASTER ==========================================================
def _path(pts):
    # MECHANISM: polyline path from sampled points, 2-decimal precision —
    #   compact but lossless at any display size.
    return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts)

def build_svg():
    # MECHANISM: assemble the master SVG as text. Layer order is meaning:
    #   field -> halo -> lattice -> ribbon -> hairlines -> waves ->
    #   emergent -> nodes -> wordmark. Each layer drawn over the last.
    a, b, e = sample(wave_a), sample(wave_b), sample(wave_emergent)
    # The vesica ribbon: down wave A, back along wave B — the polygon
    # self-intersects at the wave crossings; the nonzero fill rule turns
    # each crossing into a lens. Wide at the source, a point at the ring.
    ribbon = _path(a) + " L " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in reversed(b)) + " Z"
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    lines.append("<!-- TWIN SYNERGY TELECOMMUNICATIONS — trademark master (design stage, not filed) -->")
    lines.append("<defs>")
    # MECHANISM: vertical gold gradient for the ribbon — strongest where the
    #   interference field is widest (the source), dissolving toward the
    #   baseline as duality resolves. userSpaceOnUse: gradient geometry is
    #   computed in canvas units, so it survives any scaling.
    lines.append(f'<linearGradient id="ribbonGrad" gradientUnits="userSpaceOnUse" '
                 f'x1="600" y1="330" x2="600" y2="630">')
    lines.append(f'<stop offset="0" stop-color="{GOLD}" stop-opacity="0.34"/>')
    lines.append(f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0.06"/>')
    lines.append("</linearGradient>")
    # MECHANISM: radial halo — the macro node's outward radiance, computed
    #   concentric with the ring itself.
    lines.append(f'<radialGradient id="halo" gradientUnits="userSpaceOnUse" '
                 f'cx="{MACRO_C[0]}" cy="{MACRO_C[1]}" r="{HALO_R}">')
    lines.append(f'<stop offset="0" stop-color="{GOLD}" stop-opacity="0.16"/>')
    lines.append(f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>')
    lines.append("</radialGradient>")
    lines.append("</defs>")
    lines.append(f'<rect width="{W}" height="{H}" fill="{INDIGO}"/>')
    lines.append(f'<circle cx="{MACRO_C[0]}" cy="{MACRO_C[1]}" r="{HALO_R}" fill="url(#halo)"/>')
    # Lattice base: rule + computed diamonds.
    lines.append(f'<line x1="200" y1="{LATTICE_Y}" x2="1000" y2="{LATTICE_Y}" '
                 f'stroke="{GOLD}" stroke-width="2" opacity="0.5"/>')
    for x in lattice_points():
        r = 5.0
        lines.append(f'<polygon points="{x},{LATTICE_Y - r} {x + r},{LATTICE_Y} '
                     f'{x},{LATTICE_Y + r} {x - r},{LATTICE_Y}" '
                     f'fill="{GOLD}" opacity="0.35"/>')
    # The interference ribbon (vesicae), under the waves.
    lines.append(f'<path d="{ribbon}" fill="url(#ribbonGrad)"/>')
    # Zero-crossing hairlines: lattice joined to signal at computed points.
    for x in zero_crossings():
        lines.append(f'<line x1="{x:.2f}" y1="{Y0}" x2="{x:.2f}" y2="{LATTICE_Y}" '
                     f'stroke="{GOLD}" stroke-width="1.5" opacity="0.22"/>')
    # The twin waves.
    lines.append(f'<path d="{_path(a)}" fill="none" stroke="{GOLD}" '
                 f'stroke-width="5" stroke-linecap="round" opacity="0.85"/>')
    lines.append(f'<path d="{_path(b)}" fill="none" stroke="{GOLD}" '
                 f'stroke-width="5" stroke-linecap="round" opacity="0.85"/>')
    # The emergent carrier — the one form, brighter.
    lines.append(f'<path d="{_path(e)}" fill="none" stroke="{HIGHLIGHT}" '
                 f'stroke-width="4.5" stroke-linecap="round" opacity="0.95"/>')
    # The micro node: gold disc, indigo heart — the inward eye.
    lines.append(f'<circle cx="{MICRO_C[0]}" cy="{MICRO_C[1]}" r="{MICRO_R}" fill="{GOLD}"/>')
    lines.append(f'<circle cx="{MICRO_C[0]}" cy="{MICRO_C[1]}" r="{HEART_R}" fill="{INK}"/>')
    # The macro node: bold gold ring — the outward radiance. The indigo disc
    # is drawn first so the ring reads as a ring even over its own halo.
    lines.append(f'<circle cx="{MACRO_C[0]}" cy="{MACRO_C[1]}" r="{MACRO_R + MACRO_W / 2}" fill="{INDIGO}"/>')
    lines.append(f'<circle cx="{MACRO_C[0]}" cy="{MACRO_C[1]}" r="{MACRO_R}" '
                 f'fill="none" stroke="{GOLD}" stroke-width="{MACRO_W}"/>')
    # The wordmark — positions computed, tracking set, centered.
    lines.append(f'<text x="600" y="{WORD_Y}" text-anchor="middle" '
                 f'font-family="DejaVu Sans, Helvetica, Arial, sans-serif" '
                 f'font-size="{WORD_SIZE}" letter-spacing="{WORD_TRACK}" fill="{GOLD}">'
                 f'TWIN SYNERGY</text>')
    lines.append(f'<text x="600" y="{SUB_Y}" text-anchor="middle" '
                 f'font-family="DejaVu Sans, Helvetica, Arial, sans-serif" '
                 f'font-size="{SUB_SIZE}" letter-spacing="{SUB_TRACK}" fill="{GOLD}" opacity="0.8">'
                 f'TELECOMMUNICATIONS</text>')
    lines.append(f'<line x1="{RULE_X0}" y1="{RULE_Y}" x2="{RULE_X1}" y2="{RULE_Y}" '
                 f'stroke="{GOLD}" stroke-width="1.5" opacity="0.45"/>')
    lines.append(f'<text x="600" y="{TAG_Y}" text-anchor="middle" '
                 f'font-family="DejaVu Sans, Helvetica, Arial, sans-serif" '
                 f'font-size="{TAG_SIZE}" letter-spacing="{TAG_TRACK}" fill="{GOLD}" opacity="0.55">'
                 f'THE WHOLE BEYOND ITS PARTS</text>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"

# === THE PNG DOCUMENT RENDER ==================================================
def _hex(h):
    # MECHANISM: "#d4af37" -> (212, 175, 55). PIL speaks tuples, not hex.
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))

def _tracked(draw, cx, y, text, font, tracking, fill):
    # MECHANISM: PIL has no letter-spacing, so tracking is computed by hand:
    #   measure every glyph, add the tracking between glyphs, center the
    #   total, then draw glyph by glyph. Same numbers as the SVG.
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2.0
    for ch, wch in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill, anchor="lm")
        x += wch + tracking

def build_png(path):
    # MECHANISM: re-derive every element in scaled coordinates — the PNG is
    #   the same mathematics, rasterized, not a screenshot of the SVG. Two
    #   independent renderers from one geometry = the geometry is verified
    #   twice.
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (1600, 1200), _hex(INDIGO))
    dr = ImageDraw.Draw(img, "RGBA")
    sc = lambda v: v * S  # the one scaling function — every coordinate passes through it

    a = [(sc(x), sc(y)) for x, y in sample(wave_a)]
    b = [(sc(x), sc(y)) for x, y in sample(wave_b)]
    e = [(sc(x), sc(y)) for x, y in sample(wave_emergent)]

    # Halo: concentric translucent discs, fading outward — the radiance.
    # MECHANISM: per-layer alpha is tiny on purpose — 24 stacked discs add
    #   up, so each must be faint or the center saturates into a solid blob
    #   (the first render taught this: the macro ring drowned in its own
    #   halo). Total center alpha lands near 24/255, matching the SVG halo.
    cxm, cym = sc(MACRO_C[0]), sc(MACRO_C[1])
    for i in range(24, 0, -1):
        r = sc(HALO_R) * i / 24.0
        alpha = int(2.0 * (1.0 - i / 24.0))
        dr.ellipse([cxm - r, cym - r, cxm + r, cym + r], fill=_hex(GOLD) + (alpha,))

    # Lattice base: rule + diamonds.
    dr.line([sc(200), sc(LATTICE_Y), sc(1000), sc(LATTICE_Y)],
            fill=_hex(GOLD) + (128,), width=max(1, int(2 * S)))
    for x in lattice_points():
        xs, ys, r = sc(x), sc(LATTICE_Y), sc(5.0)
        dr.polygon([(xs, ys - r), (xs + r, ys), (xs, ys + r), (xs - r, ys)],
                   fill=_hex(GOLD) + (89,))

    # Vesica ribbon: draw on its own layer through a mask, then apply a
    # vertical gradient — the same gold field as the SVG's ribbonGrad.
    # MECHANISM: mask = white polygon on black; gradient = vertical alpha
    #   ramp; the ribbon layer is gold * mask * gradient, composited over.
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).polygon(a + b[::-1], fill=255)
    grad = Image.new("L", img.size, 0)
    gd = ImageDraw.Draw(grad)
    y_top, y_bot = sc(330.0), sc(630.0)
    for yy in range(int(y_bot)):
        t = min(1.0, max(0.0, (yy - y_top) / (y_bot - y_top)))
        gd.line([(0, yy), (1600, yy)], fill=int(96 * (1.0 - t) + 16 * t))
    from PIL import ImageChops
    alpha = ImageChops.multiply(mask, grad)
    ribbon_layer = Image.new("RGBA", img.size, _hex(GOLD) + (0,))
    ribbon_layer.putalpha(alpha)
    img = Image.alpha_composite(img.convert("RGBA"), ribbon_layer)
    dr = ImageDraw.Draw(img, "RGBA")

    # Zero-crossing hairlines.
    for x in zero_crossings():
        dr.line([sc(x), sc(Y0), sc(x), sc(LATTICE_Y)],
                fill=_hex(GOLD) + (56,), width=max(1, int(1.5 * S)))

    # The twin waves + the emergent carrier.
    dr.line(a, fill=_hex(GOLD) + (217,), width=int(5 * S), joint="curve")
    dr.line(b, fill=_hex(GOLD) + (217,), width=int(5 * S), joint="curve")
    dr.line(e, fill=_hex(HIGHLIGHT) + (242,), width=int(4.5 * S), joint="curve")

    # The micro node: gold disc, indigo heart — the inward eye.
    mx, my = sc(MICRO_C[0]), sc(MICRO_C[1])
    dr.ellipse([mx - sc(MICRO_R), my - sc(MICRO_R), mx + sc(MICRO_R), my + sc(MICRO_R)],
               fill=_hex(GOLD) + (255,))
    dr.ellipse([mx - sc(HEART_R), my - sc(HEART_R), mx + sc(HEART_R), my + sc(HEART_R)],
               fill=_hex(INK) + (255,))
    # The macro node: bold gold ring — the outward radiance. The indigo disc
    # clears the halo beneath so the ring reads as a ring, as in the master.
    dr.ellipse([cxm - sc(MACRO_R + MACRO_W / 2), cym - sc(MACRO_R + MACRO_W / 2),
                cxm + sc(MACRO_R + MACRO_W / 2), cym + sc(MACRO_R + MACRO_W / 2)],
               fill=_hex(INDIGO) + (255,))
    dr.ellipse([cxm - sc(MACRO_R), cym - sc(MACRO_R), cxm + sc(MACRO_R), cym + sc(MACRO_R)],
               outline=_hex(GOLD) + (255,), width=int(MACRO_W * S))

    # The wordmark — same sizes, tracking, and positions as the master.
    f_word = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                                int(WORD_SIZE * S))
    f_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                               int(SUB_SIZE * S))
    f_tag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                               int(TAG_SIZE * S))
    _tracked(dr, sc(600), sc(WORD_Y), "TWIN SYNERGY", f_word, sc(WORD_TRACK),
             _hex(GOLD) + (255,))
    _tracked(dr, sc(600), sc(SUB_Y), "TELECOMMUNICATIONS", f_sub, sc(SUB_TRACK),
             _hex(GOLD) + (204,))
    dr.line([sc(RULE_X0), sc(RULE_Y), sc(RULE_X1), sc(RULE_Y)],
            fill=_hex(GOLD) + (115,), width=max(1, int(1.5 * S)))
    _tracked(dr, sc(600), sc(TAG_Y), "THE WHOLE BEYOND ITS PARTS", f_tag, sc(TAG_TRACK),
             _hex(GOLD) + (140,))
    img.convert("RGB").save(path)
    return path

# === THE FORGE ENTRY ==========================================================
def main():
    # MECHANISM: one command forges both artifacts from the same geometry.
    #   The printed lines are the build receipt — byte counts are the
    #   checksums of this pipeline. If a count changes, the geometry changed:
    #   read the diff before you trust the mark.
    here = os.path.dirname(os.path.abspath(__file__))
    svg_path = os.path.join(here, "twin-synergy-logo.svg")
    png_path = os.path.join(here, "twin-synergy-logo.png")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(build_svg())
    print("forged", svg_path, "bytes:", os.path.getsize(svg_path))
    build_png(png_path)
    print("forged", png_path, "bytes:", os.path.getsize(png_path))

if __name__ == "__main__":
    main()
    # "Live, Love, and let Love, Live." — his reiteration for the Aeon of
    # Ma'at; the comma stays, because love — and will — is the foundation.
    print("93. The Twin Phase-Lock stands. Two divided for love's sake — one, for the chance of union.")
