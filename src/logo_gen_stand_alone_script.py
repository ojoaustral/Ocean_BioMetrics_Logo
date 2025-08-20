#!/usr/bin/env python3
"""
Generate a split-circle double-wave logo centered at (0,0),
with optional text either side-by-side or stacked. 
The logo replaces the 'O' in 'Ocean' (so the top text is 'cean')
and 'BioMetrics'. 

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
    wave_adj2: float,
    with_text: str = "none",                # "none" | "side-by-side" | "stacked"
    font_family: str = "Nunito Regular, Roboto Light, sans-serif",
    text_x_offset_frac: float = 0.15        # gap between logo and text (fraction of diameter)
):
    """
    Render the logo, optionally with text.
    with_text:
        - "none"         -> logo only (same as previous with_text=False)
        - "side-by-side" -> one-line "cean BioMetrics" to the right (same feel as before)
        - "stacked"      -> two lines: "cean" above, "BioMetrics" below; logo replaces 'O'
    """

    # -------- Internal tuning knobs (edit here; NOT exposed on CLI) --------
    TEXT_COLOR1 = fg1                      # Color for the top word in stacked layout
    TEXT_COLOR2 = fg1                      # Color for the bottom word in stacked layout
    SIDEBYSIDE_X_ADJUST_FRAC     = 0.00   # horizontal nudge for side-by-side (fraction of diameter)
    STACKED_LINE_SPACING_FRAC    = 1.0      # baseline gap for stacked (fraction of diameter)
    STACKED_TOP_X_ADJUST_FRAC    = 0.70   # stacked: + moves top word right, − left
    STACKED_BOTTOM_X_ADJUST_FRAC = -1.00  # stacked: + moves bottom word right, − left
    STACKED_LOGO_X_ADJUST_FRAC   = 0.80   # + right, − left (fraction of diameter)
    STACKED_LOGO_Y_ADJUST_FRAC   = -0.35  # + up,   − down (fraction of diameter) -0.035 for original; -0.21 for base aligned)
    ASCENT_FRAC                  = 0.30   # rough ascent above baseline (× font_size) 0.30 (for original)
    DESCENT_FRAC                 = 0.40   # rough descent below baseline (× font_size) 0.40 (for original)
   
    # --- Outline (underlay) ---
    TEXT_STROKE_ON = False
    TEXT_STROKE_COLOR = "blue"        # outline color "#27374D"
    TEXT_STROKE_WIDTH_FRAC = 0.01       # stroke width ≈ 1% of font size
    TEXT_STROKE_JOIN = "round"           # nicer corners on glyphs
    
    LOGO_STROKE_ON = False
    LOGO_STROKE_COLOR = "blue"     # pick something that contrasts with bg
    LOGO_STROKE_EXTRA_FRAC = 0.05     # extra thickness as a fraction of line_width
    LOGO_STROKE_JOIN = "round"        # for polylines (waves)
     # ----------------------------------------------------------------------

    # -------- Core geometry (shared) --------
    R = diameter / 2.0
    r = R - line_width/2.0
    wavelength = diameter * wavelength_frac
    amplitude  = diameter * amplitude_frac
    cycles     = diameter / wavelength
    base_phase = math.pi/2 - math.pi * cycles

    dx1 = wave_adj1 * diameter
    dx2 = wave_adj2 * diameter

    def wave1_y(x):
        θ = 2*math.pi * cycles * ((x - dx1 + R) / diameter) + base_phase
        return amplitude * math.sin(θ)

    def wave2_y(x):
        θ = 2*math.pi * cycles * ((x - dx2 + R) / diameter) + base_phase + math.pi
        return amplitude * math.sin(θ)

    x1_left,  x1_right  = find_roots(wave1_y, R, r)
    x2_left,  x2_right  = find_roots(wave2_y, R, r)

    def project(x): return x * (1 + wave_proj)
    x1l, x1r = project(x1_left),  project(x1_right)
    x2l, x2r = project(x2_left),  project(x2_right)
    y1l, y1r = wave1_y(x1l), wave1_y(x1r)
    y2l, y2r = wave2_y(x2l), wave2_y(x2r)

    # Build the drawable logo elements into a group centered at (0,0)
    def build_logo_group(dwg):
     grp = dwg.g()

     # Precompute widths
     under_w = line_width * (1 + 2*LOGO_STROKE_EXTRA_FRAC) if LOGO_STROKE_ON else line_width

     # helpers
     def add_arc(d_str, main_color):
        # Underlay
        if LOGO_STROKE_ON:
            grp.add(dwg.path(
                d=d_str, stroke=LOGO_STROKE_COLOR, fill="none",
                stroke_width=under_w, stroke_linecap="butt"
            ))
        # Main stroke on top
        grp.add(dwg.path(
            d=d_str, stroke=main_color, fill="none",
            stroke_width=line_width, stroke_linecap="butt"
        ))

     def add_wave(points, main_color):
        # Underlay
        if LOGO_STROKE_ON:
            grp.add(dwg.polyline(
                points=points, stroke=LOGO_STROKE_COLOR, fill="none",
                stroke_width=under_w, stroke_linecap="round",
                **{"stroke-linejoin": LOGO_STROKE_JOIN}
            ))
        # Main stroke on top
        grp.add(dwg.polyline(
            points=points, stroke=main_color, fill="none",
            stroke_width=line_width, stroke_linecap="round",
            **{"stroke-linejoin": LOGO_STROKE_JOIN}
        ))

     # arcs (same geometry, draw underlay first)
     top_arc_d = f"M {x1r:.4f},{y1r:.4f} A {r:.4f},{r:.4f} 0 0 0 {x1l:.4f},{y1l:.4f}"
     bot_arc_d = f"M {x2l:.4f},{y2l:.4f} A {r:.4f},{r:.4f} 0 0 0 {x2r:.4f},{y2r:.4f}"
     add_arc(top_arc_d, fg2)
     add_arc(bot_arc_d, fg1)

     # waves (polylines)
     steps = 300
     pts1 = [(x1l + (x1r - x1l)*i/steps, wave1_y(x1l + (x1r - x1l)*i/steps)) for i in range(steps+1)]
     pts2 = [(x2l + (x2r - x2l)*i/steps, wave2_y(x2l + (x2r - x2l)*i/steps)) for i in range(steps+1)]
     add_wave(pts1, fg2)
     add_wave(pts2, fg1)

     return grp


    # ---------------------------------------
    # Mode A: logo only
    # ---------------------------------------
    if with_text == "none":
        buffer = diameter * 0.05
        total  = diameter + 2*buffer
        outer  = R + buffer

        dwg = svgwrite.Drawing(size=(total, total), profile='tiny')
        dwg.viewbox(minx=-outer, miny=-outer, width=total, height=total)
        dwg.add(dwg.rect(insert=(-outer, -outer), size=(total, total), fill=bg))

        logo_group = build_logo_group(dwg)
        dwg.add(logo_group)

        if fmt.lower() == 'svg':
            dwg.saveas(output_file)
        else:
            if not CAIROSVG_AVAILABLE:
                raise RuntimeError("CairoSVG is required for PNG output")
            cairosvg.svg2png(bytestring=dwg.tostring(), write_to=output_file)
        print(f"Logo saved to {output_file}")
        return

    # ---------------------------------------
    # Mode B: side-by-side
    # ---------------------------------------
    if with_text == "side-by-side":
        buffer = diameter * 0.25 # 0.1 original, 0.25 for bottom-aligned logo
        outer  = R + buffer
        text_font_size = diameter * 1.0
        gap = diameter * text_x_offset_frac
        text_str = "cean B\u0131oMetr\u0131cs" # Replace i by \u0131 for undotted i, e.g., "B\u0131oMetr\u0131cs"
        #text_str = "cean BioMetrics" 

        # canvas sizing (approx width for text)
        est_char_w = 0.48 * text_font_size
        text_width = len(text_str) * est_char_w
        total_width  = diameter + gap + text_width + 2*buffer
        total_height = diameter + 2*buffer 

        dwg = svgwrite.Drawing(size=(total_width, total_height), profile='full')
        dwg.viewbox(minx=-buffer, miny=-outer, width=total_width, height=total_height,)
        dwg.add(dwg.rect(insert=(-buffer, -outer), size=(total_width, total_height), fill=bg))

              
        # Logo group positioned similarly to your prior translate
        logo_group = build_logo_group(dwg)
        logo_group.translate(diameter * 0.6 + SIDEBYSIDE_X_ADJUST_FRAC * diameter, 
                             diameter * STACKED_LOGO_Y_ADJUST_FRAC)
        dwg.add(logo_group)

        # Text at the right of the logo
        text_x = diameter + gap + SIDEBYSIDE_X_ADJUST_FRAC * diameter
        # Preserve your prior vertical offset feel
        text_y = diameter / 4.0

        stroke_w = text_font_size * TEXT_STROKE_WIDTH_FRAC if TEXT_STROKE_ON else 0

        if TEXT_STROKE_ON:
            dwg.add(dwg.text(
                text_str,
                insert=(text_x, text_y),
                font_size=text_font_size,
                font_family=font_family,
                fill="none",
                stroke=TEXT_STROKE_COLOR,
                stroke_width=stroke_w,
                **{"stroke-linejoin": TEXT_STROKE_JOIN}
            ))
        dwg.add(dwg.text(
            text_str,
            insert=(text_x, text_y),
            font_size=text_font_size,
            font_family=font_family,
            fill=TEXT_COLOR1
        ))

        if fmt.lower() == 'svg':
                dwg.saveas(output_file)
        else:
                if not CAIROSVG_AVAILABLE:
                    raise RuntimeError("CairoSVG is required for PNG support")
                cairosvg.svg2png(bytestring=dwg.tostring(), write_to=output_file)
        print(f"Logo with side-by-side text saved to {output_file}")
        return

    # ---------------------------------------
    # Mode C: stacked ("cean" on top, "BioMetrics" below)
    # ---------------------------------------

    if with_text == "stacked":
        # Text sizing & spacing
        font_size = diameter * 1.0
        gap       = diameter * text_x_offset_frac
        line_gap  = diameter * STACKED_LINE_SPACING_FRAC

        top_text    = "cean"
        bottom_text = "B\u0131oMetr\u0131cs" # Replace i by \u0131 for undotted i, e.g., "B\u0131oMetr\u0131cs"
        #bottom_text = "cean BioMetrics" 
        # Approximate text widths for layout/centering
        est_char_w = 0.48 * font_size
        w_top = max(1, len(top_text))    * est_char_w
        w_bot = max(1, len(bottom_text)) * est_char_w

        # Base X to the right of the logo + per-line horizontal nudges
        text_x_base = R + gap
        text_x_top  = text_x_base + diameter * STACKED_TOP_X_ADJUST_FRAC
        text_x_bot  = text_x_base + diameter * STACKED_BOTTOM_X_ADJUST_FRAC

        # Baselines: keep logo centered between them
        y_top = -line_gap / 2.0
        y_bot =  line_gap / 2.0

        # Logo position adjustments
        logo_x = diameter * STACKED_LOGO_X_ADJUST_FRAC
        logo_y = diameter * STACKED_LOGO_Y_ADJUST_FRAC

        # Extents (include translated logo + both text lines)
        ascent  = ASCENT_FRAC  * font_size
        descent = DESCENT_FRAC * font_size

        logo_left,  logo_right = -R + logo_x, R + logo_x
        leftmost  = min(logo_left, text_x_top, text_x_bot)
        rightmost = max(logo_right, text_x_top + w_top, text_x_bot + w_bot)

        min_text_y = min(y_top - ascent,  y_bot - ascent)
        max_text_y = max(y_top + descent, y_bot + descent)
        min_y = min(-R + logo_y, min_text_y)
        max_y = max( R + logo_y, max_text_y)

        # Canvas margins and final size
        margin = diameter * 0.08
        total_width  = (rightmost - leftmost) + 2 * margin
        total_height = (max_y - min_y)        + 2 * margin
        minx = leftmost - margin
        miny = min_y    - margin

        # Full profile to allow dominant-baseline/text-anchor attributes
        dwg = svgwrite.Drawing(size=(total_width, total_height), profile='full')
        dwg.viewbox(minx=minx, miny=miny, width=total_width, height=total_height)
        dwg.add(dwg.rect(insert=(minx, miny), size=(total_width, total_height), fill=bg))

        # Draw logo (translated)
        logo_group = build_logo_group(dwg)
        logo_group.translate(logo_x, logo_y)
        dwg.add(logo_group)

        # Draw texts
        dwg.add(dwg.text(
            top_text,
            insert=(text_x_top, y_top),
            font_size=font_size,
            font_family=font_family,
            fill=TEXT_COLOR1,
            **{"dominant-baseline": "middle", "text-anchor": "start"}
        ))
        dwg.add(dwg.text(
            bottom_text,
            insert=(text_x_bot, y_bot),
            font_size=font_size,
            font_family=font_family,
            fill=TEXT_COLOR2,
            **{"dominant-baseline": "middle", "text-anchor": "start"}
        ))

        if fmt.lower() == 'svg':
                dwg.saveas(output_file)
        else:
                if not CAIROSVG_AVAILABLE:
                    raise RuntimeError("CairoSVG is required for PNG support")
                cairosvg.svg2png(bytestring=dwg.tostring(), write_to=output_file)
        print(f"Logo with stacked text saved to {output_file}")
        return

    # Fallback if someone passes an unexpected string
    raise ValueError(f"Invalid with_text value: {with_text}. Must be one of: 'none', 'side-by-side', 'stacked'")


# ---------------------------------------
# Main entry point for the script
 
if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Generate split-circle double-wave logo with per-wave shifts and optional text"
    )
    p.add_argument("output_file", help="e.g. logo.svg or logo.png")
    p.add_argument("--format",               choices=["SVG","PNG"], default="SVG")
    p.add_argument("--fg1",                  default="#63C5DA", help="Color for wave2") # default "#63C5DA"
    p.add_argument("--fg2",                  default="#C4EF87", help="Color for wave1") # "#C4EF87"
    p.add_argument("--bg",                   default="#27374D", help="Background color, 'none' for transparent") # "#27374D"
    p.add_argument("--diameter",             type=float, default=600, help="Outer diameter in px")
    p.add_argument("--wavelength_frac",      type=float, default=0.7, help="Wavelength as fraction of diameter")
    p.add_argument("--amplitude_frac",       type=float, default=0.12, help="Amplitude as fraction of diameter")
    p.add_argument("--line_width",           type=float, default=40, help="Line width in px")
    p.add_argument("--wave_projection_frac", type=float, default=0.0, help=">0 extends; 0 matches; <0 contracts")
    p.add_argument("--wave_adj1",            type=float, default=0.0, help="horizontal shift of wave1 (fraction of diameter)")
    p.add_argument("--wave_adj2",            type=float, default=0.0, help="horizontal shift of wave2 (fraction of diameter)")

    # Tri-state with_text
    p.add_argument("--with_text", choices=["none", "side-by-side", "stacked"], default="none",
                   help="Text layout: 'none' (logo only), 'side-by-side' (one line), or 'stacked' (two lines).")

    # Optional: keep these exposed, or hardcode if you prefer
    p.add_argument("--font_family", default="Nunito Regular, Roboto Light, sans-serif",
                   help="CSS font-family stack (first available is used).")
    p.add_argument("--text_x_offset_frac", type=float, default=0.15,
                   help="Gap between logo and text as a fraction of diameter.")

    args = p.parse_args()

    create_logo(
        output_file=args.output_file,
        fmt=args.format,
        fg1=args.fg1,
        fg2=args.fg2,
        bg=args.bg,
        diameter=args.diameter,
        wavelength_frac=args.wavelength_frac,
        amplitude_frac=args.amplitude_frac,
        line_width=args.line_width,
        wave_proj=args.wave_projection_frac,
        wave_adj1=args.wave_adj1,
        wave_adj2=args.wave_adj2,
        with_text=args.with_text,
        font_family=args.font_family,
        text_x_offset_frac=args.text_x_offset_frac
    )
