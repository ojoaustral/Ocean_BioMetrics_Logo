# app.py
import streamlit as st
import base64
import streamlit.components.v1 as components
from logo_generator import create_logo_svg

# 1. Defaults
DEFAULTS = {
    "s_diameter_px":           600,
    "i_diameter_px":           600,
    "s_wavelength_pct":        0.70,
    "i_wavelength_pct":        0.70,
    "s_amplitude_pct":         0.12,
    "i_amplitude_pct":         0.12,
    "s_line_width_px":         40,
    "i_line_width_px":         40,
    "s_global_projection_pct": 0.00,
    "i_global_projection_pct": 0.00,
    "s_wave_adj_1_pct":        0.00,
    "i_wave_adj_1_pct":        0.00,
    "s_wave_adj_2_pct":        0.00,
    "i_wave_adj_2_pct":        0.00,
    "fg1":                     "#63C5DA",
    "fg2":                     "#C4EF87",
    "bg":                      "#27374D",
}

st.set_page_config(page_title="Logo Designer", layout="wide")
st.title("Ocean BioMetrics Logo Designer")

# Two columns: parameters | preview
param_col, preview_col = st.columns([1, 1], gap="large")

with param_col:
    st.header("Parameters")

    # Reset
    if st.button("🔄 Reset to defaults"):
        for k, v in DEFAULTS.items():
            st.session_state[k] = v

    # Slider + manual input helper
    def slider_with_input(label, mn, mx, default, step):
        key = label.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("%", "pct")
        skey, ikey = f"s_{key}", f"i_{key}"
        if skey not in st.session_state: st.session_state[skey] = default
        if ikey not in st.session_state: st.session_state[ikey] = default

        def s2i(): st.session_state[ikey] = st.session_state[skey]
        def i2s(): st.session_state[skey] = st.session_state[ikey]

        c1, c2 = st.columns([3, 1])
        c1.slider(label, mn, mx,
                  value=st.session_state[skey],
                  step=step,
                  key=skey,
                  on_change=s2i)
        c2.number_input("", mn, mx,
                        value=st.session_state[ikey],
                        step=step,
                        format="%f" if isinstance(default, float) else "%d",
                        key=ikey,
                        on_change=i2s)
        return st.session_state[skey]

    diameter        = slider_with_input("Diameter (px)",         100, 1200, DEFAULTS["s_diameter_px"],   10)
    wavelength_frac = slider_with_input("Wavelength (%)",       0.00,   1.00, DEFAULTS["s_wavelength_pct"], 0.01)
    amplitude_frac  = slider_with_input("Amplitude (%)",        0.00,   1.00, DEFAULTS["s_amplitude_pct"],  0.01)
    line_width      = slider_with_input("Line width (px)",        1,   200,  DEFAULTS["s_line_width_px"],  2)
    wave_proj       = slider_with_input("Global projection (%)", -0.50,   0.50, DEFAULTS["s_global_projection_pct"], 0.01)
    wave_adj1       = slider_with_input("Wave Adj 1 (%)",       -0.20,   0.20, DEFAULTS["s_wave_adj_1_pct"], 0.01)
    wave_adj2       = slider_with_input("Wave Adj 2 (%)",       -0.20,   0.20, DEFAULTS["s_wave_adj_2_pct"], 0.01)

    # Color pickers (keys match DEFAULTS)
    c1, c2, c3 = st.columns(3)
    fg1 = c1.color_picker("Color fg1", DEFAULTS["fg1"], key="fg1")
    fg2 = c2.color_picker("Color fg2", DEFAULTS["fg2"], key="fg2")
    bg  = c3.color_picker("Background", DEFAULTS["bg"], key="bg")

    params = {
        "fg1": fg1, "fg2": fg2, "bg": bg,
        "diameter": diameter,
        "wavelength_frac": wavelength_frac,
        "amplitude_frac": amplitude_frac,
        "line_width": line_width,
        "wave_proj": wave_proj,
        "wave_adj1": wave_adj1,
        "wave_adj2": wave_adj2
    }

with preview_col:
    st.header("Large Preview")

    # Generate SVG string once
    svg_str = create_logo_svg(**params)

    # Encode to Base64
    svg_b64 = base64.b64encode(svg_str.encode("utf-8")).decode("utf-8")

    # Main full-width preview
    main_img = f"<img src='data:image/svg+xml;base64,{svg_b64}' style='width:100%;height:auto;'/>"
    components.html(main_img, height=int(diameter * 1.2))

    # Mini Preview directly below
    st.subheader("Mini Preview")
    thumb_img = f"<img src='data:image/svg+xml;base64,{svg_b64}' width='30'/>"
    components.html(thumb_img, height=50)
