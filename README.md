# Endless 3D Maze Game

An infinite, procedurally-generated 3D maze game built with Python and Pygame. Explore endless corridors in a first-person perspective with no memory limitations - the maze generates infinitely as you move!

## ✨ Features

- **🗺️ Infinite World**: Truly endless maze generation with no memory storage
- **🎮 3D Rendering**: Real-time raycasting engine for immersive 3D experience
- **⚡ High Performance**: Optimized with Numba JIT compilation for smooth 60 FPS gameplay
- **🎨 Visual Effects**: Distance-based fog, realistic lighting, and atmospheric shading
- **🧭 Mini-map**: Real-time navigation aid with player position and direction
- **🎯 Smooth Controls**: WASD movement with strafing and precise collision detection

## 🚀 Quick Start

### Prerequisites

```bash
pip install pygame numba numpy
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/azario0/endless3Dgame.git
cd endless3Dgame
```

2. Run the game:
```bash
python maze_game.py
```

## 🎮 Controls

| Key | Action |
|-----|--------|
| `W` / `↑` | Move forward |
| `S` / `↓` | Move backward |
| `A` / `←` | Turn left |
| `D` / `→` | Turn right |
| `Q` | Strafe left |
| `E` | Strafe right |
| `ESC` | Exit game |

## 🔧 How It Works

### Procedural Generation
The maze uses a deterministic hash function to generate infinite maze patterns without storing any data in memory. Each coordinate is calculated on-demand, ensuring:
- **Zero memory growth** regardless of exploration distance
- **Consistent layout** - the same areas always look the same
- **Infinite exploration** in any direction

### 3D Rendering
Real-time raycasting creates the 3D effect by:
- Casting rays from the player's position
- Calculating wall distances and heights
- Applying perspective projection and lighting effects
- Rendering walls, floors, and ceilings with atmospheric depth

### Performance Optimization
- **Numba JIT compilation** for critical algorithms
- **Efficient ray marching** with optimized step sizes
- **Distance-based culling** to skip far objects
- **Smart memory management** with minimal allocations

## ⚙️ Configuration

Customize the game by modifying constants at the top of the code:

```python
# Screen resolution
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Player movement speed
PLAYER_SPEED = 0.05
PLAYER_ROT_SPEED = 0.03

# Maze generation seed (change for different layouts)
MAZE_SEED = 42

# Visual quality vs performance
NUM_RAYS = SCREEN_WIDTH // 3
MAX_DEPTH = 25.0
```

## 📊 Performance

- **Target FPS**: 60
- **Typical performance**: 60+ FPS on modern hardware
- **Memory usage**: Constant (no growth with exploration)
- **CPU usage**: Optimized with JIT compilation

### Fallback Mode
If Numba is not available, the game includes a fallback mode with reduced performance but full functionality.

## 🛠️ Technical Details

### Architecture
- **Language**: Python 3.7+
- **Graphics**: Pygame with custom raycasting
- **Optimization**: Numba JIT compilation
- **Math**: NumPy for efficient calculations

### Maze Algorithm
The maze generation uses a hash-based approach:
1. Convert world coordinates to grid coordinates
2. Apply deterministic hash function
3. Generate maze pattern based on hash values
4. Ensure connectivity between rooms

### Rendering Pipeline
1. **Ray casting**: Cast rays for each screen column
2. **Wall detection**: Find intersections with maze walls
3. **Distance calculation**: Apply perspective correction
4. **Shading**: Calculate lighting based on distance and wall orientation
5. **Drawing**: Render walls, floor, and ceiling

## 🎯 Future Enhancements

- [ ] Texture mapping for walls
- [ ] Multiple maze themes/biomes  
- [ ] Collectible items and objectives
- [ ] Multiplayer support
- [ ] Sound effects and ambient audio
- [ ] Different maze generation algorithms
- [ ] Save/load player progress

## 🐛 Troubleshooting

### Performance Issues
- Install Numba for optimal performance: `pip install numba`
- Reduce `NUM_RAYS` for better performance on slower hardware
- Lower screen resolution if needed

### Installation Problems
- Ensure Python 3.7+ is installed
- Update pip: `pip install --upgrade pip`
- Install dependencies in virtual environment if needed

### Controls Not Responding
- Make sure the game window has focus
- Check if any keys are stuck
- Restart the game if input becomes unresponsive

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Inspired by classic first-person maze games
- Raycasting technique from early 3D games like Wolfenstein 3D
- Thanks to the Pygame and Numba communities for excellent documentation

## 📞 Contact

**azario0** - [@azario0](https://github.com/azario0)

Project Link: [https://github.com/azario0/endless3Dgame](https://github.com/azario0/endless3Dgame)

---

⭐ **Star this repository if you found it helpful!** ⭐