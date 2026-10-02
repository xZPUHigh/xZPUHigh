"""
Builds every SVG the profile README shows, in a dark and a light copy.

The numbers and words below are read off the About ME Next Gen site
(src/data/links.ts and src/i18n/en.ts). Update them here, run

    python assets/build.py

and commit the regenerated files. Nothing in the README itself carries a
figure, so this is the only place one has to change.

The palette is the site's own: --bg, --surface, --muted and the three accents
from src/app/globals.css, the light theme and the dark one. The pixel font in
the small labels is Monocraft, drawn as outlines: GitHub serves SVGs with CSP
default-src 'none', so nothing embedded or linked (fonts, images) loads.
"""

import base64
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).parent
W = 1280

THEMES = {
    "dark": {
        "bg": "#08080b",
        "surface": "#111117",
        "text": "#f2f2f7",
        "muted": "#8e8ea0",
        "line": "#ffffff",
        "line_alpha": 0.08,
        "accent": "#9d86ff",
        "accent2": "#c9bcff",
        "accent3": "#7b5bff",
        "accent_deep": "#3a1784",
        "blob_alpha": 0.18,
        "glass_alpha": 0.55,
        "dot_alpha": 0.07,
    },
    "light": {
        "bg": "#fbfbfd",
        "surface": "#ffffff",
        "text": "#0b0b12",
        "muted": "#6a6a78",
        "line": "#0a0a14",
        "line_alpha": 0.09,
        "accent": "#6d4aff",
        "accent2": "#9278ff",
        "accent3": "#3a1784",
        "accent_deep": "#3a1784",
        "blob_alpha": 0.12,
        "glass_alpha": 0.72,
        "dot_alpha": 0.09,
    },
}

SANS = "Inter, 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "Monocraft, ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace"

# --- Facts, read off the site ------------------------------------------------

AUDIENCE = {
    "subscribers": 80_131,
    "goal": 100_000,
}

# --- Shared pieces ------------------------------------------------------------


def gradients(t, prefix, x1=0, x2=W):
    """The violet gradient, light to deep, spread across a span of user space
    so a tspan inside a longer line still gets the whole sweep."""
    return (
        f'<linearGradient id="{prefix}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="0" x2="{x2}" y2="0">'
        f'<stop offset="0" stop-color="{t["accent"]}"/>'
        f'<stop offset="0.55" stop-color="{t["accent2"]}"/>'
        f'<stop offset="1" stop-color="{t["accent3"]}"/>'
        "</linearGradient>"
    )


def glass_defs(t):
    """A flat take on the site's liquid glass: a translucent body, a gloss on
    the top half and a rim that is brightest along the top edge."""
    return (
        '<linearGradient id="gloss" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.10"/>'
        '<stop offset="0.5" stop-color="#ffffff" stop-opacity="0.02"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>'
        "</linearGradient>"
        '<linearGradient id="rim" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["line"]}" stop-opacity="{t["line_alpha"] * 3:.2f}"/>'
        f'<stop offset="1" stop-color="{t["line"]}" stop-opacity="{t["line_alpha"]:.2f}"/>'
        "</linearGradient>"
    )


def glass(t, x, y, w, h, r=20):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{t["surface"]}" fill-opacity="{t["glass_alpha"]}"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#gloss)"/>'
        f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{h - 1}" rx="{r}" fill="none" stroke="url(#rim)"/>'
    )


def blobs(t, h, seed=0):
    """Three soft lights drifting behind everything, all in the one violet so
    the backdrop reads as the brand rather than a rainbow."""
    spots = [
        (t["accent"], 0.10, 0.05, 220, 30),
        (t["accent_deep"], 0.58, 1.05, 240, -40),
        (t["accent"], 0.96, 0.00, 180, 36),
    ]
    out = []
    for i, (colour, fx, fy, r, drift) in enumerate(spots):
        cx, cy = W * fx, h * fy
        dur = 16 + 4 * ((i + seed) % 3)
        out.append(
            f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r}" fill="{colour}" fill-opacity="{t["blob_alpha"]}" filter="url(#blur)">'
            f'<animate attributeName="cx" values="{cx:.0f};{cx + drift:.0f};{cx:.0f}" dur="{dur}s" repeatCount="indefinite"/>'
            "</circle>"
        )
    return "".join(out)


def frame(t, h, body, defs="", with_blobs=True, seed=0):
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" fill="none">',
        "<defs>",
        f'<clipPath id="card"><rect width="{W}" height="{h}" rx="28"/></clipPath>',
        '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>',
        '<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1" fill="{t["line"]}" fill-opacity="{t["dot_alpha"]}"/></pattern>',
        glass_defs(t),
        defs,
        "</defs>",
        '<g clip-path="url(#card)">',
        f'<rect width="{W}" height="{h}" fill="{t["bg"]}"/>',
        blobs(t, h, seed) if with_blobs else "",
        f'<rect width="{W}" height="{h}" fill="url(#dots)"/>',
        body,
        "</g>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="28" stroke="{t["line"]}" stroke-opacity="{t["line_alpha"] * 1.5:.2f}"/>',
        "</svg>",
    ]
    return "".join(lines)


_MONO_FONT = None


def mono_path(x, y, s, size, fill, anchor="start", spacing=0.0):
    """Monocraft text as one vector path. GitHub serves SVGs with CSP
    default-src 'none', which blocks an embedded @font-face, so the pixel font
    only shows up drawn as outlines."""
    global _MONO_FONT
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont

    if _MONO_FONT is None:
        _MONO_FONT = TTFont(HERE / "fonts" / "Monocraft.woff2")
    font = _MONO_FONT
    cmap, glyphs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    k = size / font["head"].unitsPerEm

    names = [cmap.get(ord(c), ".notdef") for c in s]
    width = sum(hmtx[n][0] * k for n in names) + spacing * (len(names) - 1)
    pen = SVGPathPen(glyphs)
    cx = x - (width if anchor == "end" else width / 2 if anchor == "middle" else 0)
    for n in names:
        glyphs[n].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
        cx += hmtx[n][0] * k + spacing
    return f'<path d="{pen.getCommands()}" fill="{fill}"/>'


def text(x, y, s, size, fill, weight=400, family=SANS, anchor="start", extra=""):
    if family == MONO:
        import re

        m = re.search(r'letter-spacing="([\d.]+)"', extra)
        return mono_path(x, y, s, size, fill, anchor, float(m.group(1)) if m else 0.0)
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'
    )


def fade_in(delay, dur=0.6):
    return (
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="{dur}s" fill="freeze"/>'
    )


# --- Hero ---------------------------------------------------------------------


def hero(t):
    h = 420
    sub, goal = AUDIENCE["subscribers"], AUDIENCE["goal"]
    share = sub / goal
    left = 64

    body = [
        text(left, 104, "@XZPUHIGH  /  BANGKOK, TH  /  EST. 2017", 14, t["accent"], family=MONO),
        text(left, 214, "ZPU", 128, t["text"], 800, extra=' letter-spacing="-4"'),
        text(left, 270, "Ideas are just the start", 34, t["text"], 700, extra=' letter-spacing="-0.5"'),
        f'<text x="{left}" y="314" font-family="{SANS}" font-size="34" font-weight="700" letter-spacing="-0.5" fill="{t["text"]}">'
        '<tspan fill="url(#accent)">Making them real</tspan> is the fun part</text>',
        text(left, 362, "Chanon, 17. Self taught developer, creator and founder of Spectrum", 18, t["muted"]),
    ]

    # The goal card: the one number the whole story has been chasing.
    cx, cy, cw, ch = 816, 64, 400, 292
    bar_w = cw - 64
    fill_w = bar_w * share
    body += [
        glass(t, cx, cy, cw, ch, 24),
        text(cx + 32, cy + 46, "THE GOAL I SET AT EIGHT", 14, t["muted"], family=MONO),
        f'<text x="{cx + 32}" y="{cy + 108}" font-family="{SANS}" font-weight="800" fill="{t["text"]}">'
        f'<tspan font-size="52" letter-spacing="-1.5">{sub:,}</tspan>'
        f'<tspan font-size="22" font-weight="600" fill="{t["muted"]}" dx="8">/ {goal:,}</tspan></text>',
        text(cx + 32, cy + 136, "YouTube subscribers", 15, t["muted"]),
        f'<rect x="{cx + 32}" y="{cy + 158}" width="{bar_w}" height="10" rx="5" fill="{t["line"]}" fill-opacity="{t["line_alpha"] * 1.5:.2f}"/>',
        f'<rect x="{cx + 32}" y="{cy + 158}" width="{fill_w:.1f}" height="10" rx="5" fill="url(#bar)">'
        f'<animate attributeName="width" from="0" to="{fill_w:.1f}" dur="1.6s" begin="0.3s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/></rect>',
        text(cx + 32, cy + 194, f"{share:.0%} THERE  /  {goal - sub:,} TO GO", 14, t["accent"], family=MONO),
        f'<line x1="{cx + 32}" y1="{cy + 220}" x2="{cx + cw - 32}" y2="{cy + 220}" stroke="{t["line"]}" stroke-opacity="{t["line_alpha"] * 1.5:.2f}"/>',
    ]
    minis = [("67", "games"), ("447M+", "executions"), ("99.94%", "uptime")]
    step = (cw - 64) / 3
    for i, (value, label) in enumerate(minis):
        x = cx + 32 + step * i
        body.append(text(f"{x:.0f}", cy + 254, value, 20, t["text"], 700))
        body.append(text(f"{x:.0f}", cy + 274, label, 13, t["muted"]))

    defs = gradients(t, "accent", left, left + 300) + gradients(t, "bar", cx + 32, cx + cw - 32)
    return frame(t, h, "".join(body), defs)


# --- Link pills ---------------------------------------------------------------

# One image per link, since an <img> can only carry one destination, so each
# pill is sized to its own label. The label is measured with Segoe UI Semibold,
# the face most viewers on Windows get from the stack; other systems land
# within a few pixels, and the label is centred in its slot so the error only
# shifts the padding.
#
# Marks are Simple Icons (CC0), kept in assets/icons, drawn in the brand's
# colour as the site's link chips do. TikTok's is black, so it takes the text
# colour instead.
LINKS = [
    ("zpu.lol", "zpu", None),
    ("Spectrum Cheat", "spectrum", None),
    ("YouTube", "youtube", "#ff0033"),
    ("Discord", "discord", "#5865f2"),
    ("Instagram", "instagram", "#e4405f"),
    ("TikTok", "tiktok", "text"),
]

try:
    from PIL import ImageFont

    _MEASURE = ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf", 15)

    def label_width(label):
        return _MEASURE.getlength(label)
except Exception:  # no Pillow or no Segoe: fall back to an average advance
    def label_width(label):
        return len(label) * 8.2


def icon_path(name):
    import re

    svg = (HERE / "icons" / f"{name}.svg").read_text(encoding="utf-8")
    return re.search(r' d="([^"]+)"', svg).group(1)


def raster_mark(file, size, grid=40):
    """A brand mark redrawn as rows of coloured cells. GitHub serves every SVG
    with CSP default-src 'none', which blocks an embedded data: image, so
    anything inside has to be vector."""
    from PIL import Image

    im = Image.open(HERE / "icons" / file).convert("RGBA")
    im = im.resize((grid, grid), Image.LANCZOS)
    px = im.load()

    def cell(x, y):
        r, g, b, a = px[x, y]
        q = lambda v: min(255, round(v / 8) * 8)
        return (q(r), q(g), q(b), round(a / 32) * 32)

    rects = []
    for y in range(grid):
        x = 0
        while x < grid:
            c = cell(x, y)
            run = 1
            while x + run < grid and cell(x + run, y) == c:
                run += 1
            if c[3]:
                # Opaque runs overlap their neighbours a hair so no seam shows.
                bleed = 0.06 if c[3] >= 255 else 0
                op = "" if c[3] >= 255 else f' fill-opacity="{c[3] / 255:.2f}"'
                rects.append(
                    f'<rect x="{x}" y="{y}" width="{run + bleed}" height="{1 + bleed}" '
                    f'fill="#{c[0]:02x}{c[1]:02x}{c[2]:02x}"{op}/>'
                )
            x += run
    return f'<g transform="scale({size / grid})">{"".join(rects)}</g>'


def pill(t, label, icon, colour):
    h, pad, icon_size, gap = 44, 20, 18, 9
    inner = label_width(label) + icon_size + gap
    w = round(inner + pad * 2)
    r = 14
    primary = icon == "zpu"

    if primary:
        body = (
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="{t["accent_deep"]}"/>'
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="url(#shine)"/>'
            f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="{r - 0.5}" stroke="#ffffff" stroke-opacity="0.22"/>'
        )
        ink = "#ffffff"
    else:
        body = (
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="{t["surface"]}"/>'
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="url(#gloss)"/>'
            f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="{r - 0.5}" stroke="url(#rim)"/>'
        )
        ink = t["text"]

    x = pad
    if icon == "zpu":
        # zpu.lol/brand/Logo Webp/Z-White.webp, white so it reads on the solid
        # accent fill of the primary pill in both themes.
        body += f'<g transform="translate({x} {(h - icon_size) / 2})">{raster_mark("zpu-mark-white-512.webp", icon_size, 48)}</g>'
        x += icon_size + gap
    elif icon == "spectrum":
        theme = "dark" if t is THEMES["dark"] else "light"
        # spectrumcheat.com/images/brand/. Its "dark" copy is the light purple
        # one drawn for dark backgrounds.
        body += f'<g transform="translate({x} {(h - icon_size) / 2})">{raster_mark(f"spectrum-mark-{theme}-512.webp", icon_size)}</g>'
        x += icon_size + gap
    elif icon:
        fill = t["text"] if colour == "text" else colour
        scale = icon_size / 24
        body += (
            f'<path transform="translate({x} {(h - icon_size) / 2}) scale({scale})" d="{icon_path(icon)}" fill="{fill}"/>'
        )
        x += icon_size + gap

    body += text(f"{x + label_width(label) / 2:.1f}", 27.5, label, 15, ink, 600, anchor="middle")
    shine = (
        '<linearGradient id="shine" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.22"/>'
        '<stop offset="0.5" stop-color="#ffffff" stop-opacity="0.04"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0.08"/>'
        "</linearGradient>"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none">'
        f"<defs>{glass_defs(t)}{gradients(t, 'accent', pad, pad + icon_size)}{shine}</defs>"
        f"{body}</svg>"
    )


def slug(label):
    return label.lower().replace(" ", "-").replace(".", "-")


# --- Stack --------------------------------------------------------------------

# Icons are skillicons.dev tiles, cached in icons/skill/ (one per theme) and
# inlined, since an SVG shown through <img> fetches nothing.
STACK_ICONS = [
    ("Languages", "ts js lua py cs cpp go rust php bash html css", True),
    ("Frontend", "react nextjs svelte tailwind", False),
    ("Infrastructure", "cloudflare vercel docker ubuntu git github vscode", False),
    ("Backend and data", "nodejs bun deno express supabase postgres mysql mongodb redis sqlite", True),
]

# Words with no tile. A flag of True marks a chip drawn in the accent tint.
STACK_WORDS = [
    ("Reverse engineering", [(w, False) for w in
                             ("Ghidra", "radare2", "Frida", "x64dbg", "GDB", "Wireshark", "Burp Suite", "Metasploit")]),
    ("Creative", [(w, False) for w in
                  ("Photoshop", "Premiere Pro", "DaVinci Resolve", "VEGAS Pro", "CapCut", "Canva", "ibisPaint")]),
    ("Spoken", [("Thai", True), ("English", True)] + [(w, False) for w in
                                                      ("Chinese", "Vietnamese", "Spanish", "Japanese")]),
]

try:
    from PIL import ImageFont

    _CHIP = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)

    def chip_width(word):
        return _CHIP.getlength(word)
except Exception:
    def chip_width(word):
        return len(word) * 7.4


def skill_icon(name, theme, x, y, size):
    """The tile's own SVG, inlined. An embedded data: image would be blocked
    by the CSP GitHub serves SVGs with. Ids get the icon's name as a prefix so
    two tiles never share a gradient or clip path."""
    import re

    svg = (HERE / "icons" / "skill" / f"{name}-{theme}.svg").read_text(encoding="utf-8")
    svg = re.sub(r">\s+<", "><", svg.strip())
    svg = re.sub(r'id="([^"]+)"', rf'id="{name}-\1"', svg)
    svg = re.sub(r"url\(#([^)]+)\)", rf"url(#{name}-\1)", svg)
    svg = re.sub(r'^<svg [^>]*>', f'<svg x="{x:.1f}" y="{y}" width="{size}" height="{size}" viewBox="0 0 256 256" fill="none">', svg)
    return svg


def stack(t, theme):
    m, gap, pad = 48, 20, 28
    full = W - m * 2
    half = (full - gap) / 2
    third = (full - gap * 2) / 3
    icon, icon_gap = 48, 12
    card_h = 64 + icon + pad
    body, order = [], 0

    def label(x, y, w, name, count):
        return (
            text(x + pad, y + 40, name.upper(), 13, t["accent"], family=MONO, extra=' letter-spacing="1.2"')
            + text(round(x + w - pad, 1), y + 40, f"{count:02d}", 13, t["muted"], family=MONO, anchor="end")
        )

    def icon_card(x, y, w, name, ids):
        nonlocal order
        ids = ids.split()
        out = [glass(t, round(x, 1), y, round(w, 1), card_h), label(x, y, w, name, len(ids))]
        for i, n in enumerate(ids):
            ix = x + pad + i * (icon + icon_gap)
            out.append(
                f'<g opacity="0">{fade_in(0.15 + order * 0.035, 0.4)}{skill_icon(n, theme, ix, y + 64, icon)}</g>'
            )
            order += 1
        return "".join(out)

    # Header.
    body.append(text(m, 62, "STACK", 13, t["accent"], family=MONO, extra=' letter-spacing="1.6"'))
    body.append(text(m, 102, "What I build with", 34, t["text"], 700, extra=' letter-spacing="-0.6"'))

    y = 136
    (lang, lang_ids, _), (fe, fe_ids, _), (infra, infra_ids, _), (be, be_ids, _) = STACK_ICONS
    body.append(icon_card(m, y, full, lang, lang_ids))
    y += card_h + gap
    body.append(icon_card(m, y, half, fe, fe_ids))
    body.append(icon_card(m + half + gap, y, half, infra, infra_ids))
    y += card_h + gap
    body.append(icon_card(m, y, full, be, be_ids))
    y += card_h + gap

    # Word cards: chips wrap inside the card, every card takes the tallest height.
    chip_h, chip_pad, chip_gap = 30, 12, 8
    inner = third - pad * 2
    layouts = []
    for name, words in STACK_WORDS:
        rows, cx, cy = [], 0, 0
        for word, strong in words:
            w = round(chip_width(word) + chip_pad * 2)
            if cx and cx + w > inner:
                cx, cy = 0, cy + chip_h + chip_gap
            rows.append((cx, cy, w, word, strong))
            cx += w + chip_gap
        layouts.append((name, rows, cy + chip_h))
    words_h = 60 + max(h for _, _, h in layouts) + pad
    for i, (name, chips, _) in enumerate(layouts):
        x = m + i * (third + gap)
        body.append(glass(t, round(x, 1), y, round(third, 1), words_h))
        body.append(label(x, y, third, name, len(chips)))
        for cx, cy, w, word, strong in chips:
            px, py = x + pad + cx, y + 60 + cy
            fill, fop, ink = (t["accent"], 0.16, t["text"]) if strong else (t["line"], t["line_alpha"] * 0.7, t["text"])
            stroke = t["accent"] if strong else t["line"]
            sop = 0.45 if strong else t["line_alpha"] * 1.6
            body.append(
                f'<g opacity="0">{fade_in(0.6 + order * 0.02, 0.4)}'
                f'<rect x="{px:.1f}" y="{py}" width="{w}" height="{chip_h}" rx="9" fill="{fill}" fill-opacity="{fop:.2f}" '
                f'stroke="{stroke}" stroke-opacity="{sop:.2f}"/>'
                + text(round(px + w / 2, 1), py + 20, word, 14, ink, 500, anchor="middle")
                + "</g>"
            )
            order += 1
    h = y + words_h + m
    return frame(t, h, "".join(body), seed=2)


# --- Footer -------------------------------------------------------------------


def footer(t):
    h = 160
    body = [
        text(W / 2, 74, "Still keeping the habit that started all of it", 26, t["text"], 700, anchor="middle",
             extra=' letter-spacing="-0.4"'),
        f'<text x="{W / 2}" y="108" font-family="{SANS}" font-size="26" font-weight="700" letter-spacing="-0.4" '
        f'fill="url(#accent)" text-anchor="middle">finishing what I begin</text>',
    ]
    defs = gradients(t, "accent", W / 2 - 150, W / 2 + 150)
    return frame(t, h, "".join(body), defs, seed=1)


def main():
    builds = {"hero": hero, "footer": footer}
    for name, build in builds.items():
        for theme, palette in THEMES.items():
            path = HERE / f"{name}-{theme}.svg"
            path.write_text(build(palette), encoding="utf-8")
            print(f"{path.name}  {path.stat().st_size / 1024:.0f} KB")
    for theme, palette in THEMES.items():
        path = HERE / f"stack-{theme}.svg"
        path.write_text(stack(palette, theme), encoding="utf-8")
        print(f"{path.name}  {path.stat().st_size / 1024:.0f} KB")
    (HERE / "links").mkdir(exist_ok=True)
    for label, icon, colour in LINKS:
        for theme, palette in THEMES.items():
            path = HERE / "links" / f"{slug(label)}-{theme}.svg"
            path.write_text(pill(palette, label, icon, colour), encoding="utf-8")


if __name__ == "__main__":
    main()
