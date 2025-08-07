#!/usr/bin/env python3
"""
Generate a split-circle double-wave logo centered at (0,0),
with each colored arc trimmed to the perfect outer circle,
seamlessly meeting each sine wave—even when each wave is
horizontally shifted—plus a 5% canvas buffer, global
wave_projection_frac, and per-wave horizontal adjustments
wave_adj1 and wave_adj2.

Dependencies:
    pip install svgwrite cairosvg
"""

import math
import argparse
import svgwrite

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False

def find_roots(wave_y_func, R, r, iters=60):
    """Find the two x-roots of x^2 + wave_y(x)^2 = r^2 in [-R,R]."""
    # right-hand root
    lo, hi = 0.0, R
    for _ in range(iters):
        mid = 0.5*(lo + hi)
        if mid*mid + wave_y_func(mid)**2 > r*r:
            hi = mid
        else:
            lo = mid
    xr = 0.5*(lo + hi)
    # left-hand root
    lo, hi = -R, 0.0
    for _ in range(iters):
        mid = 0.5*(lo + hi)
        if mid*mid + wave_y_func(mid)**2 > r*r:
            lo = mid
        else:
            hi = mid
    xl = 0.5*(lo + hi)
    return xl, xr

def create_logo(
    output_file: str,
    fmt: str,
    fg1: str,
    fg2: str,
    bg: str,
    diameter: float,
    wavelength_frac: float,
    amplitude_frac: float,
    line_width: float,
    wave_proj: float,
    wave_adj1: float,
    wave_adj2: float
):
    # core geometry
    R = diameter / 2.0
    r = R - line_width/2.0
    wavelength = diameter * wavelength_frac
    amplitude = diameter * amplitude_frac
    cycles = diameter / wavelength

    # base phase so wave1 crests at x=0
    base_phase = math.pi/2 - math.pi * cycles

    # horizontal shifts in absolute units
    dx1 = wave_adj1 * diameter
    dx2 = wave_adj2 * diameter

    # define per-wave y(x)
    def wave1_y(x):
        θ = 2*math.pi * cycles * ((x - dx1 + R) / diameter) + base_phase
        return amplitude * math.sin(θ)
    def wave2_y(x):
        θ = 2*math.pi * cycles * ((x - dx2 + R) / diameter) + base_phase + math.pi
        return amplitude * math.sin(θ)

    # find original intersection points
    x1_left,  x1_right  = find_roots(wave1_y, R, r)
    x2_left,  x2_right  = find_roots(wave2_y, R, r)

    # apply global projection uniformly
    def project(x):
        return x * (1 + wave_proj)
    x1l, x1r = project(x1_left),  project(x1_right)
    x2l, x2r = project(x2_left),  project(x2_right)

    # recompute y at those projected x's
    y1l, y1r = wave1_y(x1l), wave1_y(x1r)
    y2l, y2r = wave2_y(x2l), wave2_y(x2r)

    # 5% buffer
    buffer = diameter * 0.05
    total  = diameter + 2*buffer
    outer  = R + buffer

    # setup SVG
    dwg = svgwrite.Drawing(size=(total, total), profile='tiny')
    dwg.viewbox(minx=-outer, miny=-outer, width=total, height=total)
    dwg.add(dwg.rect(
        insert=(-outer, -outer),
        size=(total, total),
        fill=bg
    ))

    # top arc (fg2): from (x1r, y1r) → (x1l, y1l)
    top_arc = dwg.path(
        d=(
            f"M {x1r:.4f},{ y1r:.4f} "
            f"A {r:.4f},{r:.4f} 0 0 0 {x1l:.4f},{ y1l:.4f}"
        ),
        stroke=fg2, fill="none",
        stroke_width=line_width,
        stroke_linecap="butt"
    )
    dwg.add(top_arc)

    # bottom arc (fg1): from (x2l, y2l) → (x2r, y2r)
    bottom_arc = dwg.path(
        d=(
            f"M {x2l:.4f},{ y2l:.4f} "
            f"A {r:.4f},{r:.4f} 0 0 0 {x2r:.4f},{ y2r:.4f}"
        ),
        stroke=fg1, fill="none",
        stroke_width=line_width,
        stroke_linecap="butt"
    )
    dwg.add(bottom_arc)

    # build each shifted/projection wave
    def build_wave(x_left, x_right, wave_y_func, color):
        pts = []
        steps = 300
        for i in range(steps+1):
            x = x_left + (x_right - x_left) * i/steps
            y = wave_y_func(x)
            pts.append((x, y))
        return dwg.polyline(
            points=pts,
            stroke=color,
            fill="none",
            stroke_width=line_width,
            stroke_linecap="round"
        )

    # draw wave1 (fg2) and wave2 (fg1)
    dwg.add(build_wave(x1l, x1r, wave1_y, fg2))
    dwg.add(build_wave(x2l, x2r, wave2_y, fg1))

    # export
    if fmt.lower() == 'svg':
        dwg.saveas(output_file)
    else:
        if not CAIROSVG_AVAILABLE:
            raise RuntimeError("CairoSVG is required for PNG output")
        cairosvg.svg2png(bytestring=dwg.tostring(), write_to=output_file)

    print(f"Logo saved to {output_file}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Generate split-circle double-wave logo with per-wave shifts")
    p.add_argument("output_file", help="e.g. logo.svg or logo.png")
    p.add_argument("--format",               choices=["SVG","PNG"], default="SVG")
    p.add_argument("--fg1",                  default="#63C5DA", help="Color for wave2")
    p.add_argument("--fg2",                  default="#C4EF87", help="Color for wave1")
    p.add_argument("--bg",                   default="#27374D", help= "Background color, 'none' for transparent")
    p.add_argument("--diameter",             type=float, default=600, help="Outer diameter in px")
    p.add_argument("--wavelength_frac",      type=float, default=0.7, help="Wavelength as fraction of diameter")
    p.add_argument("--amplitude_frac",       type=float, default=0.12, help="Amplitude as fraction of diameter")
    p.add_argument("--line_width",           type=float, default=40, help="Line width in px")
    p.add_argument("--wave_projection_frac", type=float, default=0.0,
                   help=">0 extends; 0 matches; <0 contracts")
    p.add_argument("--wave_adj1",            type=float, default=0.0,
                   help="horizontal shift of wave1 (fraction of diameter)")
    p.add_argument("--wave_adj2",            type=float, default=0.0,
                   help="horizontal shift of wave2 (fraction of diameter)")
    args = p.parse_args()

    create_logo(
        args.output_file,
        args.format,
        args.fg1,
        args.fg2,
        args.bg,
        args.diameter,
        args.wavelength_frac,
        args.amplitude_frac,
        args.line_width,
        args.wave_projection_frac,
        args.wave_adj1,
        args.wave_adj2
    )
