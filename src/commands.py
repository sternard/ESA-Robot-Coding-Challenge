import json
from typing import List, Dict, Any
from src.asteroid import Asteroid
from src.robot import Robot

def execute_commands(commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process a list of JSON command dictionaries and execute them.
    Expected commands include:
      - An "asteroid" command (must be first) defining the grid size.
      - One or more "new-robot" commands to create new robots.
      - "move" commands to control the current robot.
      
    Returns:
        A list of output dictionaries representing the final state of each robot.
    """
    if not commands or commands[0].get("type") != "asteroid":
        raise ValueError("First command must be an asteroid message")
    
    asteroid = Asteroid.from_dict(commands[0]["size"])
    robots: List[Robot] = []
    current_robot: Robot = None  # type: ignore

    for cmd in commands[1:]:
        cmd_type = cmd.get("type")
        if cmd_type == "new-robot":
            # Use subscripting to get required values.
            pos: Dict[str, int] = cmd["position"]
            if not asteroid.is_within_bounds(pos["x"], pos["y"]):
                raise ValueError("New robot cannot be initialised out of bounds")
            current_robot = Robot(cmd["position"], cmd["bearing"], asteroid)
            robots.append(current_robot)
        elif cmd_type == "move":
            if current_robot is None:
                raise ValueError("No robot available to execute move command")
            movement = cmd.get("movement")
            if movement == "turn-left":
                current_robot.turn_left()
            elif movement == "turn-right":
                current_robot.turn_right()
            elif movement == "move-forward":
                current_robot.move_forward()
            else:
                raise ValueError(f"Unknown movement command: {movement}")
        else:
            raise ValueError(f"Unknown command type: {cmd_type}")
    
    output: List[Dict[str, Any]] = []
    for robot in robots:
        state = robot.current_state()
        output.append({
            "type": "robot",
            "position": {"x": state.x, "y": state.y},
            "bearing": state.bearing
        })
    return output

def format_output(outputs: List[Dict[str, Any]]) -> str:
    """
    Formats a list of robot output dictionaries into a newline-separated string.
    """
    return "\n".join(json.dumps(robot_state) for robot_state in outputs)
