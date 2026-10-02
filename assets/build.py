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
        "blob_alpha": 0.42,
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
        "blob_alpha": 0.26,
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

# Three rows of four, the way the about page prints them: the channel, the
# community, the work. The last column of each row is a clock.
STATS = [
    ("CHANNEL", "since 2017", [
        ("8M+", "Total views"),
        ("80K+", "YouTube subscribers"),
        ("793+", "Videos uploaded"),
        ("9+", "Years on YouTube"),
    ]),
    ("COMMUNITY", "since 2021", [
        ("110K+", "Community members"),
        ("447M+", "Total executions"),
        ("240K+", "Total sales"),
        ("5+", "Years of community"),
    ]),
    ("WORK", "since 2019", [
        ("$891K+", "Total volume"),
        ("73K+", "Customers"),
        ("24+", "Projects shipped"),
        ("5+", "Years coding"),
    ]),
]

# The years that turned the story get a bigger node, as on the site.
MAJOR = {"2017", "2021", "2024", "2025"}

TIMELINE = [
    ("2017", "The first upload"),
    ("2018", "First real money"),
    ("2019", "The first shop"),
    ("2020", "Working during the pandemic"),
    ("2021", "First code, first community"),
    ("2022", "Paid for the first time"),
    ("2023", "The mystery box business"),
    ("2024", "Spectrum"),
    ("2025", "The year I felt low"),
    ("2026", "Where things stand"),
]

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
        (t["accent"], 0.18, 0.15, 340, 30),
        (t["accent2"], 0.62, 0.95, 300, -40),
        (t["accent3"], 0.92, 0.10, 260, 36),
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
        text(cx + 32, cy + 46, "THE GOAL I SET AT EIGHT", 12, t["muted"], family=MONO),
        f'<text x="{cx + 32}" y="{cy + 108}" font-family="{SANS}" font-weight="800" fill="{t["text"]}">'
        f'<tspan font-size="52" letter-spacing="-1.5">{sub:,}</tspan>'
        f'<tspan font-size="22" font-weight="600" fill="{t["muted"]}" dx="8">/ {goal:,}</tspan></text>',
        text(cx + 32, cy + 136, "YouTube subscribers", 15, t["muted"]),
        f'<rect x="{cx + 32}" y="{cy + 158}" width="{bar_w}" height="10" rx="5" fill="{t["line"]}" fill-opacity="{t["line_alpha"] * 1.5:.2f}"/>',
        f'<rect x="{cx + 32}" y="{cy + 158}" width="{fill_w:.1f}" height="10" rx="5" fill="url(#bar)">'
        f'<animate attributeName="width" from="0" to="{fill_w:.1f}" dur="1.6s" begin="0.3s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/></rect>',
        text(cx + 32, cy + 194, f"{share:.0%} THERE  /  {goal - sub:,} TO GO", 12, t["accent"], family=MONO),
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


# --- Stats --------------------------------------------------------------------


def stats(t):
    pad, label_w, gap = 56, 172, 16
    tile_w = (W - pad * 2 - label_w - gap * 3) / 4
    tile_h = 112
    h = pad * 2 + tile_h * 3 + gap * 2

    body = []
    for r, (name, since, tiles) in enumerate(STATS):
        y = pad + r * (tile_h + gap)
        body.append(text(pad, y + 50, name, 14, t["text"], family=MONO))
        body.append(text(pad, y + 74, since, 14, t["muted"]))
        for c, (value, label) in enumerate(tiles):
            x = pad + label_w + c * (tile_w + gap)
            clock = c == 3
            delay = 0.1 + (r * 4 + c) * 0.06
            body.append(
                f'<g opacity="0">{fade_in(delay)}'
                + glass(t, round(x, 1), y, round(tile_w, 1), tile_h, 18)
                + text(f"{x + 24:.1f}", y + 58, value, 38, "url(#accent)" if clock else t["text"], 800,
                       extra=' letter-spacing="-1"')
                + text(f"{x + 24:.1f}", y + 86, label, 15, t["muted"])
                + "</g>"
            )

    defs = gradients(t, "accent", pad + label_w + 3 * (tile_w + gap), W - pad)
    return frame(t, int(h), "".join(body), defs, seed=1)


# --- Timeline -----------------------------------------------------------------


def wrap(s, width=16):
    lines, line = [], ""
    for word in s.split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    lines.append(line)
    return lines


def timeline(t):
    h = 360
    pad = 88
    axis = h / 2
    step = (W - pad * 2) / (len(TIMELINE) - 1)

    body = [
        f'<line x1="{pad}" y1="{axis}" x2="{W - pad}" y2="{axis}" stroke="{t["line"]}" stroke-opacity="{t["line_alpha"] * 1.5:.2f}" stroke-width="2"/>',
        f'<line x1="{pad}" y1="{axis}" x2="{W - pad}" y2="{axis}" stroke="url(#accent)" stroke-width="2" '
        f'stroke-dasharray="{W - pad * 2}" stroke-dashoffset="{W - pad * 2}">'
        f'<animate attributeName="stroke-dashoffset" from="{W - pad * 2}" to="0" dur="2.2s" begin="0.2s" fill="freeze"/></line>',
    ]

    for i, (year, title) in enumerate(TIMELINE):
        x = pad + step * i
        major = year in MAJOR
        above = i % 2 == 1
        delay = 0.2 + i * 0.2
        lines = wrap(title)
        size = 16 if major else 14
        colour = t["text"] if major else t["muted"]
        weight = 700 if major else 500
        leading = size + 5

        g = [f'<g opacity="0">{fade_in(delay, 0.5)}']
        if major:
            g.append(f'<circle cx="{x:.1f}" cy="{axis}" r="13" fill="{t["accent"]}" fill-opacity="0.18"/>')
            g.append(f'<circle cx="{x:.1f}" cy="{axis}" r="7" fill="{t["accent"]}"/>')
        else:
            g.append(f'<circle cx="{x:.1f}" cy="{axis}" r="5" fill="{t["bg"]}" stroke="{t["muted"]}" stroke-width="2"/>')

        year_fill = t["accent"] if major else t["muted"]
        if above:
            g.append(text(f"{x:.1f}", axis - 32, year, 14, year_fill, family=MONO, anchor="middle"))
            top = axis - 58 - leading * (len(lines) - 1)
            for j, line in enumerate(lines):
                g.append(text(f"{x:.1f}", f"{top + j * leading:.1f}", line, size, colour, weight, anchor="middle"))
        else:
            g.append(text(f"{x:.1f}", axis + 44, year, 14, year_fill, family=MONO, anchor="middle"))
            for j, line in enumerate(lines):
                g.append(text(f"{x:.1f}", f"{axis + 72 + j * leading:.1f}", line, size, colour, weight, anchor="middle"))
        g.append("</g>")
        body.append("".join(g))

    defs = gradients(t, "accent", pad, W - pad)
    return frame(t, h, "".join(body), defs, seed=2)


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
    builds = {"hero": hero, "stats": stats, "timeline": timeline, "footer": footer}
    for name, build in builds.items():
        for theme, palette in THEMES.items():
            path = HERE / f"{name}-{theme}.svg"
            path.write_text(build(palette), encoding="utf-8")
            print(f"{path.name}  {path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
