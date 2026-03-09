*This project has been created as part of the 42 curriculum by vborysov, vskopova.*

## Description

This project is a Maze Generator developed in Python, designed to programmatically create and visualize complex grid structures. The primary goal is to implement a robust generation engine capable of producing "perfect" mazes—mathematically defined structures where exactly one unique path exists between any two points, ensuring no loops and no isolated areas.

The application reads parameters from a configuration file, executes the generation logic, and exports the resulting maze using a compact hexadecimal wall representation. This format allows for efficient storage and data exchange. Additionally, the project includes a visualizer to render the maze, while the core generation logic is built as a modular component, making it easily reusable for future pathfinding or game development tasks.

---

## Configuration File

The maze generator reads its parameters from an external configuration file (`config.txt`).  
This file defines the maze dimensions, entry and exit points, output settings, and generation options.

The configuration file uses a simple **KEY=VALUE** format.

### Example Configuration

The configuration file follows a simple **key = value** format:

```
WIDTH=40
HEIGHT=20
ENTRY=0,0
EXIT=39,19
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=48956984659734
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `WIDTH` | Width of the maze grid (number of columns) |
| `HEIGHT` | Height of the maze grid (number of rows) |
| `ENTRY` | Coordinates of the maze entrance in the format `x,y` |
| `EXIT` | Coordinates of the maze exit in the format `x,y` |
| `OUTPUT_FILE` | Name of the file where the generated maze will be saved |
| `PERFECT` | If set to `True`, the generator creates a *perfect maze* (exactly one path between any two cells) |
| `SEED` | Random seed used for reproducible maze generation |

### Notes

- Coordinates use **zero-based indexing**, meaning the top-left cell of the maze is `(0,0)`.
- Providing a fixed `SEED` ensures that the same maze can be generated repeatedly.
- The `ENTRY` and `EXIT` points define where the maze starts and ends.

This configuration-driven approach allows the generator to be easily reused with different parameters without modifying the source code.

---
## Maze Generation Algorithms

The project supports multiple maze generation strategies implemented using a **Strategy Pattern**.  
All algorithms inherit from a common abstract base class `MazeStrategy`, which defines a unified interface for maze generation and provides shared utility methods.

This design allows the generator to easily support **multiple algorithms while keeping the core system modular and extensible**.

---

## Strategy Architecture

All generation algorithms inherit from the abstract class:

MazeStrategy


This base class provides:

- A common `generate()` interface
- Utility functions for opening walls between cells
- Boundary wall manipulation
- Direction bitmasks used in the internal maze representation

### Direction Encoding

Each cell stores its walls using a **bitmask representation**:

| Direction | Value |
|-----------|------|
| North | 1 |
| East | 2 |
| South | 4 |
| West | 8 |

Each cell initially contains the value `15` (`1111` in binary), meaning that **all four walls are present**.  
During maze generation, walls are removed by clearing the corresponding bits.

This compact representation allows efficient maze storage and fast manipulation.

---

## Perfect Maze Algorithm

The `PerfectMazeGen` class generates **perfect mazes** using **Kruskal's algorithm**.

A perfect maze has the following properties:

- Exactly **one unique path** between any two cells
- **No cycles**
- **No isolated areas**

### Algorithm Overview

The algorithm works as follows:

1. Each cell starts in its own disjoint set.
2. All possible walls between neighboring cells are collected.
3. The walls are randomly shuffled.
4. For each wall:
   - If the two cells belong to **different sets**, the wall is removed.
   - The two sets are merged using **Union-Find**.
5. If the cells are already connected, the wall is left intact to avoid creating a cycle.

This process continues until all cells are connected into a single spanning tree.

### Advantages

This approach guarantees that:

- the maze is fully connected
- no loops exist
- the result is mathematically a **minimum spanning tree** of the grid graph

---

## Non-Perfect Maze Algorithm

The `NonPerfectMazeGen` class generates mazes that **contain loops and multiple possible paths**.

It begins with the same **Kruskal-based spanning tree generation** used for perfect mazes.  
However, after the initial structure is created, additional walls may be removed to introduce cycles.

### Cycle Injection

The algorithm stores all walls that were not used during the Kruskal phase.

Then, with a fixed probability (20%), some of these walls are removed, creating **additional connections between cells**.

This produces:

- alternative routes
- loops
- more complex maze navigation

---

## Preventing Large Empty Areas

When adding extra openings, the algorithm performs an additional validation step.

Before removing a wall, it checks whether doing so would create a **3×3 empty region with no internal walls**.

If such a region would appear, the wall removal is reverted.

This constraint helps maintain:

- structural complexity
- visually interesting corridors
- avoidance of large open rooms

---

## Static Obstacle Pattern

Both algorithms also support embedding a **predefined obstacle pattern** inside the maze.

The pattern is defined as a small binary grid:

- `1` represents a **solid blocked cell**
- `0` represents a **normal maze cell**

The pattern is automatically centered inside the maze and excluded from the generation process.

This allows the maze to contain **structured obstacles or shapes**, making the generated layouts more interesting and less uniform.

---

## Deterministic Generation

Both algorithms support deterministic maze generation using a **random seed**.

When the same seed and configuration are used, the generator will always produce **the exact same maze**, which is useful for:

- testing
- reproducibility
- debugging
- sharing maze configurations
## Reusable Components

The project was designed with **modularity and reusability** in mind.

The core reusable components include:

### Maze Generation Engine

The generation logic is implemented as a standalone module responsible for:

- grid management
- cell connectivity
- wall removal logic
- algorithm execution

This component can be reused in:

- **game development**
- **procedural content generation**
- **pathfinding experiments**
- **AI navigation simulations**

### Maze Data Representation

The maze structure uses a **compact hexadecimal encoding of cell walls**, making it suitable for:

- efficient storage
- easy serialization
- fast parsing by other applications

---

## Project Management

This project was developed collaboratively as part of the **42 curriculum**.

### Team Members

| Name | Role |
|-----|------|
| vborysov | Core algorithm implementation, project architecture |
| vskopova | Visualization, testing |

---

### Planning and Development Process

At the beginning of the project, we focused on defining:

- the internal maze representation
- the generation algorithm
- the configuration system

The initial plan was to implement a minimal generator first, followed by visualization and modularization.

During development, the architecture evolved to improve:

- **separation between generation and visualization**
- **modularity of the generation engine**
- **configuration flexibility**

This iterative approach allowed us to progressively improve the codebase while maintaining a working version of the generator.

---

### What Worked Well

Several aspects of the project proved particularly effective:

- Clear separation between **core logic and visualization**
- A **configuration-based workflow** that simplifies experimentation
- Modular code that makes it easier to extend the project

---

### What Could Be Improved

Future improvements could include:

- support for **multiple maze generation algorithms**
- additional **visualization options**
- interactive maze exploration tools
- improved configuration validation

---

### Tools Used

During development, the following tools were used:

- **Python 3.10**
- **Make** for workflow automation
- **flake8** for code style checking
- **mypy** for static type analysis
- **Git** for version control

## Instructions

The project uses a **Makefile-based workflow** to simplify environment setup, dependency installation, execution, and development tasks. All commands are executed via `make`.

### Requirements

- Python 3.10
- `make`

### Setup

The project automatically creates a **Python virtual environment** and installs all required dependencies.

```bash
make install
```

### Run

Executes the maze generator using the default configuration file.

```bash
make run
```

Or

```bash
python3 a_maze_ing.py config.txt
```

## Resources

During the development of this project, several references and tools were used to guide the implementation and improve code quality:

### Documentation & Tutorials

- **Python 3 official documentation** — for language features, type hints, and standard library usage.  
  [https://docs.python.org/3/](https://docs.python.org/3/)

- **Python `abc` module documentation** — for understanding abstract base classes and strategy pattern implementation.  
  [https://docs.python.org/3/library/abc.html](https://docs.python.org/3/library/abc.html)

- **Kruskal’s Algorithm** references — classic algorithm tutorials and visualizations for understanding minimum spanning trees and perfect maze generation.  
  Examples:
  - [https://en.wikipedia.org/wiki/Kruskal%27s_algorithm](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
  - "Mazes for Programmers" by Jamis Buck (concepts and patterns for procedural maze generation)

- **Bitmasking and grid representation** tutorials — for efficient wall encoding in a 2D grid.

- Python static analysis guides (mypy, flake8) — for maintaining code quality and type safety.

---

### AI Assistance

AI tools were leveraged for:

- **Code organization and explanation** — helping to structure README sections, summarize algorithms, and write clear docstrings.
- **Python syntax and type hints** — generating type-annotated method stubs and utility functions.
- **Algorithm discussion and comparison** — assisting in writing explanations for DFS, Kruskal-based maze generation, and cycle injection in non-perfect mazes.

> Note: AI was used purely as a **writing and planning assistant**. All core logic, algorithm implementation, and testing were fully authored by the project team.

---

This combination of references and AI assistance allowed the team to **implement modular, readable, and reproducible maze generation strategies** while keeping documentation professional and accessible.