from typing import Dict, Tuple, NamedTuple
from enum import Enum
from src.asteroid import Asteroid

class Direction(Enum):
    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"

class RobotState(NamedTuple):
    x: int
    y: int
    bearing: str

class Robot:
    # Define the order of cardinal directions as an enum tuple.
    DIRECTIONS: Tuple[Direction, ...] = (Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST)
    # MOVEMENTS is now keyed by Direction.
    MOVEMENTS: Dict[Direction, Tuple[int, int]] = {
        Direction.NORTH: (0, 1),
        Direction.EAST: (1, 0),
        Direction.SOUTH: (0, -1),
        Direction.WEST: (-1, 0)
    }

    def __init__(self, position: Dict[str, int], bearing: str, asteroid: Asteroid) -> None:
        # Use subscripting to ensure we get int values.
        self.x: int = position["x"]
        self.y: int = position["y"]
        # Convert the bearing string to a Direction enum.
        self.bearing: Direction = Direction(bearing.lower())
        self.asteroid: Asteroid = asteroid

    def turn_left(self) -> None:
        idx: int = self.DIRECTIONS.index(self.bearing)
        self.bearing = self.DIRECTIONS[(idx - 1) % len(self.DIRECTIONS)]

    def turn_right(self) -> None:
        idx: int = self.DIRECTIONS.index(self.bearing)
        self.bearing = self.DIRECTIONS[(idx + 1) % len(self.DIRECTIONS)]

    def move_forward(self) -> None:
        # Now using self.bearing (a Direction) as key in MOVEMENTS.
        dx, dy = self.MOVEMENTS[self.bearing]
        new_x: int = (self.x + dx) % (self.asteroid.size_x + 1)
        new_y: int = (self.y + dy) % (self.asteroid.size_y + 1)
        self.x = new_x
        self.y = new_y

    def current_state(self) -> RobotState:
        # Return a RobotState NamedTuple.
        return RobotState(x=self.x, y=self.y, bearing=self.bearing.value)
