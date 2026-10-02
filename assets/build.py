"""
Builds every SVG the profile README shows, in a dark and a light copy.

The numbers and words below are read off the About ME Next Gen site
(src/data/links.ts and src/i18n/en.ts). Update them here, run

    python assets/build.py

and commit the regenerated files. Nothing in the README itself carries a
figure, so this is the only place one has to change.

The palette is the site's own: --bg, --surface, --muted and the three accents
from src/app/globals.css, the light theme and the dark one. The pixel font in
the small labels is Monocraft, embedded so it renders inside an <img>, where
an SVG cannot load anything from outside itself.
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
        "accent2": "#ff7ad4",
        "accent3": "#56dcf5",
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
        "accent2": "#d94fb0",
        "accent3": "#2fb8d9",
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


def font_face():
    data = base64.b64encode((HERE / "fonts" / "Monocraft.woff2").read_bytes()).decode()
    return (
        "<style>@font-face{font-family:Monocraft;"
        f"src:url(data:font/woff2;base64,{data}) format('woff2');}}</style>"
    )


def gradients(t, prefix, x1=0, x2=W):
    """The site's three accent gradient, spread across a span of user space
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
    """Three soft accent lights drifting behind everything."""
    spots = [
        (t["accent"], 0.10, 0.05, 220, 30),
        (t["accent2"], 0.58, 1.05, 200, -40),
        (t["accent3"], 0.96, 0.00, 180, 36),
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
        font_face(),
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


def text(x, y, s, size, fill, weight=400, family=SANS, anchor="start", extra=""):
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
    ("zpu.lol", None, None),
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


def pill(t, label, icon, colour):
    h, pad, icon_size, gap = 44, 20, 18, 9
    has_icon = icon is not None
    inner = label_width(label) + (icon_size + gap if has_icon else 0)
    w = round(inner + pad * 2)
    r = 14
    primary = icon is None

    if primary:
        body = (
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="{t["accent"]}"/>'
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
    if icon == "spectrum":
        cy = h / 2
        body += (
            f'<circle cx="{x + icon_size / 2}" cy="{cy}" r="{icon_size / 2 - 1}" fill="url(#accent)"/>'
            f'<circle cx="{x + icon_size / 2}" cy="{cy}" r="{icon_size / 2 - 5.5}" fill="{t["surface"]}"/>'
        )
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
    (HERE / "links").mkdir(exist_ok=True)
    for label, icon, colour in LINKS:
        for theme, palette in THEMES.items():
            path = HERE / "links" / f"{slug(label)}-{theme}.svg"
            path.write_text(pill(palette, label, icon, colour), encoding="utf-8")


if __name__ == "__main__":
    main()
