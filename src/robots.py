import sys
import json
from typing import Union, Iterable, List, Dict, Any, TextIO
from .commands import execute_commands, format_output  # Using relative import for package mode

def process_instructions(instructions: Union[str, Iterable[str]]) -> List[Dict[str, Any]]:
    """
    Processes instructions from a string or file-like object (or any iterable of strings) line by line.
    Skips blank lines and validates that the first command is an asteroid command.
    """
    # If instructions is a string, split it into lines.
    if isinstance(instructions, str):
        if not instructions.strip():
            return []
        lines: Iterable[str] = instructions.splitlines()
    else:
        # Otherwise, assume it's an iterable (e.g., file-like object) yielding lines.
        lines = instructions

    commands: List[Dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            # Skip blank lines.
            continue
        try:
            command: Dict[str, Any] = json.loads(line)
        except json.JSONDecodeError as e:
            raise e
        commands.append(command)
    
    if not commands or commands[0].get("type") != "asteroid":
        raise ValueError("First command must be an asteroid message")
    
    # Validate that if there is more than one command, the second command is not a move instruction.
    if len(commands) > 1 and commands[1].get("type") == "move":
        raise ValueError("New robot must be initialised before a move instruction")
    
    return commands

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m src.robots <instructions_file>")
        sys.exit(1)
    
    # Open the instructions file.
    with open(sys.argv[1]) as file:
        commands_list = process_instructions(file)
    
    # Dispatch commands to create and move robots.
    robot_outputs = execute_commands(commands_list)
    
    # Format the final output so that each robot's state is on a separate JSON line.
    final_output: str = format_output(robot_outputs)
    
    print(final_output)

if __name__ == "__main__":
    main()
