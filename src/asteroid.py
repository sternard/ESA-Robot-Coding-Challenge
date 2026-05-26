from dataclasses import dataclass
from typing import Dict

@dataclass
class Asteroid:
    size_x: int
    size_y: int

    @classmethod
    def from_dict(cls, size: Dict[str, int]) -> "Asteroid":
        # Create an Asteroid instance from a dictionary with keys "x" and "y"
        return cls(size_x=size["x"], size_y=size["y"])

    def is_within_bounds(self, x: int, y: int) -> bool:
        # Check if x and y are within the range [0, size_x] and [0, size_y] respectively.
        return 0 <= x <= self.size_x and 0 <= y <= self.size_y
