# ESA Robot Coding Challenge

Solution for the ESA asteroid robot coding challenge. The original challenge 
prompt is included in [CHALLENGE.md](CHALLENGE.md).

The program reads one JSON command per line from a text file and writes one JSON
message per robot to standard output.

Development was test driven with additional functional tests implemented 
retrospectively.

## Quick start

```bash
python robots.py examples/instructions.txt
```

Expected output for the included worked example:

```json
{"type": "robot", "position": {"x": 1, "y": 3}, "bearing": "north"}
{"type": "robot", "position": {"x": 5, "y": 1}, "bearing": "east"}
```

Run the tests with:

```bash
python -m pytest
```

Run the type checker directly with:

```bash
python -m mypy
```

## Project structure

```text
.
├── robots.py              # CLI entry point
├── src/
│   ├── asteroid.py        # Asteroid grid model
│   ├── commands.py        # JSON-line parsing and command dispatch
│   ├── robot.py           # Robot movement and bearing logic
│   └── types.py           # Shared typed structures
├── tests/                 # Unit, integration, CLI, and typing tests
└── examples/
    └── instructions.txt   # Worked example input
```

## Design notes

The core domain logic is separated from file handling and standard output. That
keeps `Robot` and `Asteroid` easy to unit test, while `robots.py` only handles
argument parsing and process-level concerns.

The instruction file is read lazily, line by line, so the program does not need
to load the full input file into memory. It keeps only the asteroid definition,
the current robot, and the list of robots required for final output.

## Boundary behaviour

Grid coordinates are inclusive: an asteroid with size `{"x": 5, "y": 5}` accepts
positions from `(0, 0)` through `(5, 5)`.

Robot movement wraps around the asteroid boundary. For example, moving north
from `(5, 5)` lands at `(5, 0)`, and moving west from `(0, 0)` lands at `(5, 0)`.
New robots still have to be initialised within the asteroid bounds.

