# Kentroid Samurai PNG-Tuber

A VTuber-style avatar application featuring the Kentroid Samurai character with voice reactivity and multiple view modes.

## Screenshots


<img src="wide_silent.png" width="48%" alt="Wide viewport - Silent"> <img src="wide_talking.png" width="48%" alt="Wide viewport - Talking">

<img src="wide_explosions.png" width="48%" alt="Wide viewport - Explosions"><img src="wide_emoji_party.png" width="48%" alt="Wide viewport - Emoji Party">

<img src="square_talking.png" width="400" alt="Square viewport - Talking">

**Example in action:** [Watch on YouTube](https://www.youtube.com/watch?v=bovZW-hlgkY)

## Features

- **Voice Reactivity**: Dynamic visor glow that changes color based on audio intensity
  - Idle: Deep blue
  - Low volume: Cyan
  - Medium: Green
  - High: Pink/Magenta
  - Very high: Purple
- **Multiple Zoom Levels** (Z+1 to Z+7):
  - Zoom 1: Full body view
  - Zoom 2-7: Progressive face/head zooms (increasingly closer)
- **Viewport Dimensions**:
  - Dimension 1 (D+1): 800x800 square
  - Dimension 2 (D+2): 1200x800 widescreen
- **Backgrounds** (B+1 to B+9):
  - Black, Rainbow, Samus Ship (2 variants)
  - Crateria, Brinstar, Hellway, Tourian
  - **CHAOS** - Mathematical madness background 🌀✨💫
- **Visual Effects**:
  - Effect 1 (E+1): RAGE mode (red tint + explosions)
  - Effect 2 (E+2): EMOJI PARTY (bouncing emojis)
- **Smooth Animations**: Dynamic head rocking/bobbing patterns
- **Microphone Input**: Real-time audio detection with device selection

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the application:

```bash
python pngtuber.py
```

### Audio Device Selection

List available audio input devices:

```bash
python pngtuber.py --list-devices
```

Use a specific audio device:

```bash
python pngtuber.py --device <index>
```

Example:
```bash
python pngtuber.py --device 3
```

### Controls

**Zoom Levels:**
- **Z + 1-7**: Switch between zoom levels (1=full body, 2-7=progressive face zooms)

**Viewport:**
- **D + 1**: Square viewport (800x800)
- **D + 2**: Wide viewport (1200x800)

**Backgrounds:**
- **B + 1**: Black background
- **B + 2**: Rainbow background
- **B + 3-8**: Metroid-themed backgrounds (Ship, Crateria, Brinstar, Hellway, Tourian)
- **B + 9**: CHAOS background (Mathematical madness! 🌀)

**Effects:**
- **E + 1**: Toggle RAGE effect (red tint + explosions)
- **E + 2**: Toggle EMOJI PARTY effect (bouncing emojis)

**Other:**
- **T**: Toggle UI text overlay
- **ESC**: Quit application

### Adjusting Settings

You can modify these settings in `pngtuber.py`:

- **Visor position**: Adjust `visor_center_offset`
- **Zoom settings**: Modify `zoom_levels` array
- **Audio sensitivity**: Change `audio_threshold`
- **Rock animation**: Adjust `max_rock_angle` and `rock_speed`
- **Glow effect**: Modify glow colors and intensity

## Building as a Mac App

You can package the PNG-Tuber as a standalone macOS `.app` bundle:

```bash
# Install py2app (already in requirements.txt)
pip install py2app

# Build the app
python setup.py py2app

# The app will be in the dist/ folder
open dist/pngtuber.app
```

See **[BUILD_APP.md](BUILD_APP.md)** for detailed instructions, troubleshooting, and advanced options.

## Use with OBS

To use this as an overlay in OBS Studio:

1. Run the PNG-Tuber application (from command line or as a Mac app)
2. In OBS, add a "Window Capture" source
3. Select the PNG-Tuber window

## Troubleshooting

**Performance issues:**
- Lower the FPS in the code (change `clock.tick(60)` to a lower value)
- Reduce the glow effect complexity
