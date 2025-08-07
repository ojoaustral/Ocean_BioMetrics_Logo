# Ocean BioMetrics Logo Designer

A Streamlit-powered app and Python library to generate a split-circle double-wave logo (suggestive of ocean waves and DNA) with real-time, interactive controls.

![Ocean BioMetrics Logo](./output_logos/logo1.png)


---

## Features

- **Pure-Python logo generation** (`logo_gen_stand_alone_script.py`)
  - Numeric root-finding for circle–wave intersections
  - Dynamic SVG viewbox sizing so nothing ever gets clipped
  - Customizable parameters for wave properties, colors, and sizes
  - CairoSVG export to SVG/PNG

- **Pure-Python logo generation** (`logo_generator.py`)
  - Similar to logo_gen_stand_alone_script.py but tweaged for use with streamlit
  - Numeric root-finding for circle–wave intersections
  - Dynamic SVG viewbox sizing so nothing ever gets clipped
  - Customizable parameters for wave properties, colors, and sizes
  - CairoSVG export to SVG/PNG though logo_gen_stand_alone_script.py (not yet implemented in the app)

- **Interactive Streamlit app** (`app.py`)
  - Sliders + paired number-inputs for all geometry parameters
  - Color pickers for foreground & background
  - “Reset to defaults” button to restore initial settings
  - Live full-size and thumbnail previews

---

## Getting Started

### 1. Clone this repository

```bash
git clone https://github.com/<your-username>/ocean-biometrics-logo-designer.git
cd ocean-biometrics-logo-designer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

To generate a logo SVG and save it to a file using the standalone script:

```bash
python src/logo_gen_stand_alone_script.py output.svg
```

To generate a PNG:

```bash
python src/logo_gen_stand_alone_script.py output.png --format PNG
```

To generate a logo with custom parameters:

```bash
python src/logo_gen_stand_alone_script.py --help

python src/logo_gen_stand_alone_script.py logo.svg --diameter 800 --fg1 "#C4EF87" --fg2 "#63C5DA" --bg "#27374D"
```

### 3. Run the interactive Streamlit app

```bash
streamlit run src/app.py
```

### 4. Access the app

Open your web browser and go to `http://localhost:8501` to access the app.

### 5. Generate and download logos

Use the app's controls to customize your logo, then click the "Download SVG" or "Download PNG" button to save your design. TODO for now, the download buttons are not implemented in the app, but you can use the standalone script to generate logos, or copy image directly from app display.

