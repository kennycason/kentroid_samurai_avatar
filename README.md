# Kentroid Samurai PNG-Tuber

A VTuber-style avatar application featuring the Kentroid Samurai character with voice reactivity and multiple view modes.

## Screenshots


<img src="wide_silent.png" width="48%" alt="Wide viewport - Silent"> <img src="wide_talking.png" width="48%" alt="Wide viewport - Talking">

<img src="wide_explosions.png" width="48%" alt="Wide viewport - Explosions"><img src="wide_emoji_party.png" width="48%" alt="Wide viewport - Emoji Party">

<img src="square_talking.png" width="400" alt="Square viewport - Talking">

**Example in action:** [Watch on YouTube](https://www.youtube.com/watch?v=bovZW-hlgkY)

## Features

- **Voice Reactivity**: Neon blue visor glow that pulses when you speak
- **Multiple Zoom Levels**:
  - Zoom 1 (Z+1): Full body view
  - Zoom 2 (Z+2): Face/head zoom (centered on visor area)
- **Viewport Dimensions**:
  - Dimension 1 (D+1): 800x800 square
  - Dimension 2 (D+2): 1200x800 widescreen
- **Smooth Animations**: Subtle head rocking motion
- **Microphone Input**: Real-time audio detection

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:

```bash
pip install -r requirements.txt
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

- **Visor position**: Adjust `visor_center_offset`
- **Zoom settings**: Modify `zoom_levels` array
- **Audio sensitivity**: Change `audio_threshold`
- **Rock animation**: Adjust `max_rock_angle` and `rock_speed`
- **Glow effect**: Modify glow colors and intensity

## Use with OBS

To use this as an overlay in OBS Studio:

1. Run the PNG-Tuber application
2. In OBS, add a "Window Capture" source
3. Select the PNG-Tuber window

## Troubleshooting

**Performance issues:**
- Lower the FPS in the code (change `clock.tick(60)` to a lower value)
- Reduce the glow effect complexity
