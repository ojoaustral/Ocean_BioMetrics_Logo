#!/usr/bin/env python3
import math, os, shutil, time
import imageio.v2 as imageio
from logo_gen_stand_alone_script import create_logo

def generate_gif(output_gif: str,
                 frames: int = 60,
                 duration: float = 15,
                 amplitude: float = 0.05,
                 keep_frames: bool = False,
                 bg: str = "#27374D"):
    base_dir = "frames"
    if keep_frames:
        stamp = time.strftime("%Y%m%d-%H%M%S")
        frame_dir = os.path.join(base_dir, f"run_{stamp}")
        os.makedirs(frame_dir, exist_ok=True)
    else:
        frame_dir = base_dir
        if os.path.isdir(frame_dir):
            shutil.rmtree(frame_dir)
        os.makedirs(frame_dir, exist_ok=True)

    # Render settings
    diameter = 600
    wavelength_frac = 0.7
    amplitude_frac = 0.12
    line_width = 40
    fg1 = "#63C5DA"
    fg2 = "#C4EF87"

    total_shift_px = 418
    step_px = total_shift_px / (frames - 1) if frames > 1 else total_shift_px

    # Generate frames
    for i in range(frames):
        t = i / frames
        #wa1 = amplitude * math.sin(2 * math.pi * t)
        #wa2 = -amplitude * math.sin(2 * math.pi * t)
        shift_px = i * step_px
        wa1 = shift_px / diameter   # convert px → fraction of diameter
        wa2 = shift_px / diameter
        fn = os.path.join(frame_dir, f"frame_{i:04d}.png")

        create_logo(
            output_file=fn, fmt="PNG",
            fg1=fg1, fg2=fg2, bg=bg,
            diameter=diameter,
            wavelength_frac=wavelength_frac,
            amplitude_frac=amplitude_frac,
            line_width=line_width,
            wave_proj=0.0,
            wave_adj1=wa1,
            wave_adj2=wa2,
            with_text="none",
            font_family="Nunito Regular, Roboto Light, sans-serif",
            text_x_offset_frac=0.15
        )

    # Assemble GIF
    per_frame = duration / frames
    files = [os.path.join(frame_dir, f"frame_{i:04d}.png") for i in range(frames)]
    if not all(os.path.exists(p) for p in files):
        raise RuntimeError(f"Missing frames in {frame_dir}; generated {sum(os.path.exists(p) for p in files)}/{frames}")

    images = [imageio.imread(f) for f in files]
    imageio.mimsave(output_gif, images, duration=per_frame, loop=0, subrectangles=False)

    print(f"GIF written to: {output_gif}")
    if keep_frames:
        print(f"Frames kept in: {frame_dir}")
    else:
        shutil.rmtree(frame_dir)

if __name__ == "__main__":
    # Minimal default run; adjust as needed
    generate_gif(output_gif="animatedlogo2.gif", 
                 frames=200, 
                 duration=1, # doesn't work 
                 amplitude=0.05, 
                 keep_frames=False, 
                 bg="#27374D")
