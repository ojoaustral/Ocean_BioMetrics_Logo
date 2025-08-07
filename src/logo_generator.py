# logo_generator.py
#!/usr/bin/env python3
"""
Module to generate a split-circle double-wave logo as an SVG string,
with dynamic canvas sizing to fit all geometry including arcs.
"""

import math
import svgwrite

def find_roots(wave_y_func, R, r, iters=60):
    """Find the two x-roots of x^2 + wave_y(x)^2 = r^2 in [-R, R]."""
    lo, hi = 0.0, R
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if mid*mid + wave_y_func(mid)**2 > r*r:
            hi = mid
        else:
            lo = mid
    xr = 0.5 * (lo + hi)

    lo, hi = -R, 0.0
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if mid*mid + wave_y_func(mid)**2 > r*r:
            lo = mid
        else:
            hi = mid
    xl = 0.5 * (lo + hi)
    return xl, xr


def create_logo_svg(
    fg1: str, fg2: str, bg: str,
    diameter: float, wavelength_frac: float, amplitude_frac: float,
    line_width: float, wave_proj: float, wave_adj1: float, wave_adj2: float
) -> str:
    """
    Returns SVG XML string for the logo, resizing canvas to fit all shapes.
    """
    # Core geometry
    R = diameter / 2.0
    r = R - line_width/2.0
    wavelength = diameter * wavelength_frac
    amplitude = diameter * amplitude_frac
    cycles = diameter / wavelength
    base_phase = math.pi/2 - math.pi * cycles

    # Horizontal shifts
    dx1 = wave_adj1 * diameter
    dx2 = wave_adj2 * diameter

    # Wave functions
    def wave1_y(x):
        θ = 2*math.pi * cycles * ((x - dx1 + R) / diameter) + base_phase
        return amplitude * math.sin(θ)

    def wave2_y(x):
        θ = 2*math.pi * cycles * ((x - dx2 + R) / diameter) + base_phase + math.pi
        return amplitude * math.sin(θ)

    # Intersection roots
    x1l, x1r = find_roots(wave1_y, R, r)
    x2l, x2r = find_roots(wave2_y, R, r)

    # Global projection
    def project(x): return x * (1 + wave_proj)
    x1l, x1r = project(x1l), project(x1r)
    x2l, x2r = project(x2l), project(x2r)

    y1l, y1r = wave1_y(x1l), wave1_y(x1r)
    y2l, y2r = wave2_y(x2l), wave2_y(x2r)

    # Sample waves
    steps = 300
    pts1 = [(x1l + (x1r - x1l)*i/steps, wave1_y(x1l + (x1r - x1l)*i/steps))
            for i in range(steps+1)]
    pts2 = [(x2l + (x2r - x2l)*i/steps, wave2_y(x2l + (x2r - x2l)*i/steps))
            for i in range(steps+1)]

    # Combine all points + circle extents
    pts_all = pts1 + pts2 + [(x1l, y1l), (x1r, y1r), (x2l, y2l), (x2r, y2r)]
    xs = [p[0] for p in pts_all] + [-r, r]
    ys = [p[1] for p in pts_all] + [-r, r]

    # Bounds + margin
    margin = diameter * 0.05
    min_x, max_x = min(xs) - margin, max(xs) + margin
    min_y, max_y = min(ys) - margin, max(ys) + margin
    width, height = max_x - min_x, max_y - min_y

    # Build SVG
    dwg = svgwrite.Drawing(size=(width, height), profile='tiny')
    dwg.viewbox(minx=min_x, miny=min_y, width=width, height=height)
    dwg.add(dwg.rect(insert=(min_x, min_y), size=(width, height), fill=bg))

    # Top arc
    dwg.add(dwg.path(
        d=f"M {x1r:.4f},{y1r:.4f} A {r:.4f},{r:.4f} 0 0 0 {x1l:.4f},{y1l:.4f}",
        stroke=fg2, fill="none",
        stroke_width=line_width, stroke_linecap="butt"
    ))
    # Bottom arc
    dwg.add(dwg.path(
        d=f"M {x2l:.4f},{y2l:.4f} A {r:.4f},{r:.4f} 0 0 0 {x2r:.4f},{y2r:.4f}",
        stroke=fg1, fill="none",
        stroke_width=line_width, stroke_linecap="butt"
    ))
    # Waves
    dwg.add(dwg.polyline(points=pts1, stroke=fg2, fill="none",
                         stroke_width=line_width, stroke_linecap="round"))
    dwg.add(dwg.polyline(points=pts2, stroke=fg1, fill="none",
                         stroke_width=line_width, stroke_linecap="round"))

    return dwg.tostring()
