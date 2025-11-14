# Kentroid Samurai PNG-Tuber

A VTuber-style avatar application featuring the Kentroid Samurai character with voice reactivity and multiple view modes.

## Image Assets

The application uses these samurai images:
- **KentroidSamuraiTopVisorShade.PNG** - Main image (1334x1920 pixels)
- **KentroidSamuraiNoBG.PNG** - Alternative with no background
- **KentroidSamuraiTopNoVisor.PNG** - Version without visor
- **KentroidSamuraiWhiteBG.PNG** - White background version

## Features

- 🎭 **Voice Reactivity**: Neon blue visor glow that pulses when you speak
- 🎬 **Multiple Zoom Levels**:
  - Zoom 1 (Z+1): Full body view
  - Zoom 2 (Z+2): Face/head zoom (centered on visor area)
- 📐 **Viewport Dimensions**:
  - Dimension 1 (D+1): 800x800 square
  - Dimension 2 (D+2): 1200x800 widescreen
- 💫 **Smooth Animations**: Subtle head rocking motion
- 🎤 **Microphone Input**: Real-time audio detection

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### macOS Additional Setup

For PyAudio on macOS, you may need to install PortAudio first:

```bash
brew install portaudio
pip install pyaudio
```

## Usage

Run the application:

```bash
python pngtuber.py
```

### Controls

- **Z + 1**: Switch to full body zoom
- **Z + 2**: Switch to face zoom
- **D + 1**: Switch to square viewport (800x800)
- **D + 2**: Switch to wide viewport (1200x800)
- **ESC**: Quit application

### Adjusting Settings

You can modify these settings in `pngtuber.py`:

- **Visor position**: Adjust `visor_center_offset` (line ~50)
- **Zoom settings**: Modify `zoom_levels` array (lines ~40-55)
- **Audio sensitivity**: Change `audio_threshold` (line ~68)
- **Rock animation**: Adjust `max_rock_angle` and `rock_speed` (lines ~63-64)
- **Glow effect**: Modify glow colors and intensity (lines ~170-180)

## Tips

- **Find the right audio threshold**: If the glow is too sensitive or not sensitive enough, adjust the `audio_threshold` value (higher = less sensitive)
- **Fine-tune zoom positions**: The face zoom offset can be adjusted in the `zoom_levels` array to center perfectly on the visor
- **Visor glow position**: If the blue sphere isn't aligned with the visor, adjust the `visor_center_offset` values

## Use with OBS

To use this as an overlay in OBS Studio:

1. Run the PNG-Tuber application
2. In OBS, add a "Window Capture" source
3. Select the PNG-Tuber window
4. Right-click the source → Filters → Add "Chroma Key"
5. Select black as the key color
6. Adjust similarity and smoothness as needed

## Troubleshooting

**No audio detection:**
- Check that your microphone is connected and set as the default input device
- Try adjusting the `audio_threshold` value in the code

**Image not displaying correctly:**
- Ensure the PNG files are in the same directory as `pngtuber.py`
- Check that the image path is correct (default: `KentroidSamuraiTopVisorShade.PNG`)

**Performance issues:**
- Lower the FPS in the code (change `clock.tick(60)` to a lower value)
- Reduce the glow effect complexity

## License

This is a personal project. The Kentroid Samurai artwork is your property.

