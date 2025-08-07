import streamlit as st
from logo_generator import create_logo_png_bytes

# 1. Define your defaults in one place:
DEFAULTS = {
    "s_diameter_px":          600,
    "i_diameter_px":          600,
    "s_wavelength_pct":       0.70,
    "i_wavelength_pct":       0.70,
    "s_amplitude_pct":        0.12,
    "i_amplitude_pct":        0.12,
    "s_line_width_px":        40,
    "i_line_width_px":        40,
    "s_global_projection_pct": 0.00,
    "i_global_projection_pct": 0.00,
    "s_wave_adj_1_pct":       0.00,
    "i_wave_adj_1_pct":       0.00,
    "s_wave_adj_2_pct":       0.00,
    "i_wave_adj_2_pct":       0.00,
    "fg1":                 "#63C5DA",
    "fg2":                 "#C4EF87",
    "bg":                  "#27374D",
}

st.set_page_config(page_title="Logo Designer", layout="wide")
st.title("Ocean BioMetrics Logo Designer")

# Top‐left: parameter & reset
param_col, preview_col = st.columns([1, 1], gap="large")
with param_col:
    st.header("Parameters")

    # 2. Reset button
    if st.button("🔄 Reset to defaults"):
        for key, val in DEFAULTS.items():
            st.session_state[key] = val
        

    # 3. Helper that uses those session‐state keys:
    def slider_with_input(label, mn, mx, default, step):
        # derive our keys
        key = label.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("%","pct")
        skey, ikey = f"s_{key}", f"i_{key}"
        # initialize
        if skey not in st.session_state:
            st.session_state[skey] = default
        if ikey not in st.session_state:
            st.session_state[ikey] = default

        # sync callbacks
        def s2i(): st.session_state[ikey] = st.session_state[skey]
        def i2s(): st.session_state[skey] = st.session_state[ikey]

        c1, c2 = st.columns([3,1])
        c1.slider(label, mn, mx,
                  value=st.session_state[skey],
                  step=step, key=skey, on_change=s2i)
        c2.number_input("", mn, mx,
                        value=st.session_state[ikey],
                        step=step,
                        format="%f" if isinstance(default, float) else "%d",
                        key=ikey, on_change=i2s)
        return st.session_state[skey]

    # 4. Your sliders
    diameter        = slider_with_input("Diameter (px)",         100, 1200, DEFAULTS["s_diameter_px"],   10)
    wavelength_frac = slider_with_input("Wavelength (%)",       0.00,   1.00, DEFAULTS["s_wavelength_pct"], 0.01)
    amplitude_frac  = slider_with_input("Amplitude (%)",        0.00,   1.00, DEFAULTS["s_amplitude_pct"],  0.01)
    line_width      = slider_with_input("Line width (px)",        1,   200,  DEFAULTS["s_line_width_px"],  2)
    wave_proj       = slider_with_input("Global projection (%)", -0.50,   0.50, DEFAULTS["s_global_projection_pct"], 0.01)
    wave_adj1       = slider_with_input("Wave Adj 1 (%)",       -0.20,   0.20, DEFAULTS["s_wave_adj_1_pct"], 0.01)
    wave_adj2       = slider_with_input("Wave Adj 2 (%)",       -0.20,   0.20, DEFAULTS["s_wave_adj_2_pct"], 0.01)

    # 5. Color pickers
    c1, c2, c3 = st.columns(3)
    fg1 = c1.color_picker("Color fg1", DEFAULTS["fg1"], key="fg1")
    fg2 = c2.color_picker("Color fg2", DEFAULTS["fg2"], key="fg2")
    bg  = c3.color_picker("Background", DEFAULTS["bg"], key="bg")
    # Ensure color pickers reset to defaults
    if "fg1" not in st.session_state:
        st.session_state["fg1"] = DEFAULTS["fg1"]
    if "fg2" not in st.session_state:
        st.session_state["fg2"] = DEFAULTS["fg2"]
    if "bg" not in st.session_state:
        st.session_state["bg"] = DEFAULTS["bg"]
    params = dict(
        fg1=fg1, fg2=fg2, bg=bg,
        diameter=diameter,
        wavelength_frac=wavelength_frac,
        amplitude_frac=amplitude_frac,
        line_width=line_width,
        wave_proj=wave_proj,
        wave_adj1=wave_adj1,
        wave_adj2=wave_adj2
    )

with preview_col:
    st.header("Large Preview")
    png = create_logo_png_bytes(**params)
    st.image(png, use_container_width=True)
    # 6. Mini preview
    st.subheader("Mini Preview")
    #st.image(png, width=30)  
    thumb_scale = 30 / diameter  # scale factor for thumbnail
    thumb_params = params.copy()
    thumb_params["diameter"] = 30
    thumb_params["line_width"] = int(line_width * thumb_scale)
    thumb_params["amplitude_frac"] = amplitude_frac  # If amplitude is a fraction, it may not need scaling
    # Scale other absolute pixel values if needed
    thumb_png = create_logo_png_bytes(**thumb_params)
    st.image(thumb_png)