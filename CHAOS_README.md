# 🌀 CHAOS EFFECT VIEWER 🌀

## Pure Mathematical Visual Madness

A standalone application showcasing computational beauty through chaos theory, fractals, and mathematical visualizations.

## 🎨 What's Inside

This viewer combines **7 mathematical visualization systems** running simultaneously:

### 1. **Voronoi Diagrams** 🎨
- Animated cellular automata-like patterns
- Moving seed points create organic, flowing regions
- Color-coded by distance and hue

### 2. **Particle System** ✨
- Up to 200 particles with full physics simulation
- Attraction/repulsion forces creating vortex patterns
- Rotational velocity fields
- Rainbow color cycling
- Motion trails

### 3. **Lorenz Strange Attractor** 🦋
- Real-time 3D chaos system simulation
- Classic butterfly-shaped attractor trajectory
- Demonstrates sensitive dependence on initial conditions
- Rainbow-colored path traces

**Mathematics:**
```
dx/dt = σ(y - x)
dy/dt = x(ρ - z) - y  
dz/dt = xy - βz
```

### 4. **Recursive Fractals** 🔺
- Sierpinski-inspired triangular patterns
- Self-similar structures at different scales
- Animated rotation and depth variation
- Color changes with recursion depth

### 5. **Lissajous Curves** 〰️
- Parametric curves: x = sin(at + δ), y = sin(bt)
- Beautiful figure-8 and complex harmonic patterns
- Parameters: a=3, b=4 with phase shift
- Full spectrum color gradients

### 6. **Geometric Chaos** 🔷
- 8 rotating squares orbiting the center
- Individual rotation speeds and phases
- Size oscillation based on time
- Creates mesmerizing mandala-like patterns

### 7. **Kaleidoscope Effect** 🎡
- N-fold radial symmetry (adjustable 1-9)
- Oscillating radial lines
- Pulsing circles at endpoints
- Breathing alternation effect

## 🚀 How to Run

### Basic Usage
```bash
python chaos_viewer.py
```

### Custom Window Size
```bash
python chaos_viewer.py --width 1920 --height 1080
```

### Fullscreen Mode (EPIC!)
```bash
python chaos_viewer.py --fullscreen
```

## 🎮 Interactive Controls

| Key | Action |
|-----|--------|
| **ESC** or **Q** | Quit the viewer |
| **F** | Toggle FPS counter |
| **I** | Toggle info overlay |
| **R** | Regenerate Voronoi points (new pattern!) |
| **SPACE** | Spawn 50 extra particles |
| **1-9** | Set kaleidoscope segments (1-9) |

## 🎯 Usage Tips

1. **Press R repeatedly** to see different Voronoi configurations
2. **Press SPACE** to create particle bursts
3. **Try different kaleidoscope segments** (8 is gorgeous!)
4. **Run in fullscreen** for the full immersive experience
5. **Watch the strange attractor** form its iconic butterfly shape

## 🔬 The Science

This isn't just pretty - it's **real mathematics**:

- **Chaos Theory**: The Lorenz attractor demonstrates deterministic chaos
- **Computational Geometry**: Voronoi diagrams show nearest-neighbor relationships
- **Harmonic Motion**: Lissajous curves visualize frequency relationships
- **Fractals**: Self-similar patterns at every scale
- **Physics Simulation**: Realistic particle dynamics with forces

## 🎨 Performance

- Runs at **60 FPS** for smooth animation
- Optimized drawing routines
- Adaptive particle system (spawns/removes as needed)
- Efficient numpy operations for physics calculations

## 💡 Use Cases

- **Screensaver** - Hypnotic and mesmerizing
- **VJ/Live Visuals** - Perfect for music performances
- **Art Installation** - Run on large displays
- **Meditation/Focus** - Watch the patterns flow
- **Math Education** - Visualize complex concepts
- **Just Because It's Cool** - No explanation needed! 😎

## 🎊 Fun Facts

- The Lorenz attractor was discovered while studying weather patterns
- Voronoi diagrams appear in nature (giraffe spots, cell structures)
- Lissajous curves can be seen on oscilloscopes
- This effect generates **thousands of draw calls per frame**
- Every frame is unique - you'll never see the same pattern twice!

## 🌟 Enjoy the Chaos!

This is computational art at its finest. Sit back, press fullscreen, and let the mathematical beauty wash over you.

**Remember**: This isn't random - it's chaos. Every pixel is calculated with precision. The apparent randomness emerges from deterministic mathematical rules.

*"Chaos is order yet undeciphered."* - José Saramago

---

## 🎭 Integration with PNG-Tuber

The CHAOS effect is also available as a **background** in the main PNG-Tuber application!

### Using CHAOS as Background

In `pngtuber.py`, press **B+9** to activate the CHAOS background behind Samus:

```bash
python pngtuber.py
# Then press B+9 to enable CHAOS background
```

The effect will run at full intensity **behind** the character, creating an incredible visual backdrop for streaming or recording!

Perfect for:
- 🎮 **Boss battle moments** - Maximum intensity!
- 🎤 **Hype segments** - Energy overload!
- ✨ **Special announcements** - Stand out visually!
- 🌌 **Dramatic scenes** - Mathematical atmosphere!

---

Made with 💜 and a lot of math

