# 2D Solar System Simulation

An interactive 2D solar system simulation built with Python and Pygame, made as a college assignment for the **2D Geometric Transformation** topic in Computer Graphics.

The program implements Rotation, Translation, and Scaling transformations from scratch — no physics libraries, no animation engines. Everything is done manually with math.

> **Kelompok 3 — Tugas Grafika Komputer: Transformasi Geometri 2D**

---

## Features

- 8 planets with manual scanline textures and day/night shading
- Saturn rings, Earth's moon, Jupiter's Great Red Spot
- 200 asteroid belt particles
- Halley's Comet with Keplerian orbit and particle tail
- Pulsing sun (sine-based scaling)
- Meteor launcher with 4 size options and realistic slingshot mechanics
- Planet destruction system based on planet hardness vs meteor mass
- Click a planet to see its details (gravity, diameter, orbital period, etc.)
- Camera pan, zoom, and follow mode
- Coordinate grid, orbit trails, gravity field lines visualization
- HUD panel showing live transformation matrix values (θ, cos, sin, x', y')
- Keyboard shortcut guide overlay (press F1 or click the button)
- Sound effects (synthesized, no external audio files needed)

---

## How It Works

The core of the simulation is built on three 2D geometric transformations:

### Rotation
Used for planet revolution around the sun and the moon around Earth.

$$x' = R \cdot \cos(\theta), \quad y' = R \cdot \sin(\theta)$$

Each frame, the angle is updated by:

$$\theta = \theta + (\text{speed} \times \Delta t)$$

### Translation
Used for camera panning and follow mode.

$$x' = x + dx, \quad y' = y + dy$$

The moon's position is a translation offset from Earth's current position.

### Scaling
Used for zoom and the pulsing sun effect.

$$x' = x \cdot s, \quad y' = y \cdot s$$

The sun's pulse uses:

$$s_{\text{pulse}} = 1.0 + 0.06 \cdot \sin(t \cdot 1.5)$$

### World to Screen
All world coordinates are converted to screen pixels with:

$$x_{\text{screen}} = \text{cam\_x} + (x_{\text{world}} \times s)$$

---

## Requirements

- Python 3.8 or higher (tested on Python 3.10)
- pygame 2.x
- Windows / macOS / Linux

---

## Installation & Running

### 1. Clone the repository

```bash
git clone https://github.com/fathiryasyaa/2d-solar-system-simulation.git
cd 2d-solar-system-simulation
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Install dependencies

**Windows (PowerShell):**
```powershell
.\venv\Scripts\pip install pygame
```

**Windows (CMD):**
```cmd
venv\Scripts\pip install pygame
```

**macOS / Linux:**
```bash
./venv/bin/pip install pygame
```

Or just use the requirements file:
```bash
pip install -r requirements.txt
```

### 4. Run the program

**Windows:**
```powershell
.\venv\Scripts\python tata_surya.py
```

**macOS / Linux:**
```bash
./venv/bin/python tata_surya.py
```

---

## Controls

| Input | Action |
|-------|--------|
| Scroll up / down | Zoom in / out |
| Left click + drag | Pan camera |
| Left click on planet | Select planet (shows info card) |
| Right click + drag back | Slingshot a meteor |
| `1` / `2` / `3` / `4` | Select meteor size (Small / Medium / Large / Giant) |
| `SPACE` | Pause / Resume |
| `→` (Right arrow) | Step 1 frame (while paused) |
| `S` | Toggle slow-motion (0.05x) |
| `F` | Follow selected planet |
| `[` / `]` | Decrease / Increase orbit speed |
| `O` | Toggle orbit lines |
| `L` | Toggle planet labels |
| `G` | Toggle coordinate grid |
| `T` | Toggle orbit trails |
| `V` | Toggle gravity field lines |
| `H` | Hide / show side panel |
| `R` | Reset camera, planets, and meteors |
| `F1` | Open / close keyboard shortcut guide |
| `ESC` | Quit |

---

## Meteor System

Meteors are launched by holding right click and dragging backward (slingshot), then releasing. A yellow dotted preview line shows the predicted trajectory.

There are 4 meteor sizes:

| Size | Mass | Effect |
|------|------|--------|
| Small | 3 | Sparks on impact, never destroys |
| Medium | 20 | Can destroy small rocky planets |
| Large | 60 | Can destroy ice/mid-size planets |
| Giant | 200 | Can destroy gas giants |

Whether a planet gets destroyed depends on the planet's hardness value compared to the meteor's mass. Press **R** to reset all meteors and restore destroyed planets.

---

## Project Structure

```
.
├── tata_surya.py     # main program
├── requirements.txt  # dependencies
└── README.md
```

---

## Notes

This project was made purely for learning purposes as part of a Computer Graphics course. All transformations are implemented manually without any physics or animation libraries.
