import pytest
from src.commands import execute_commands


def test_execute_only_asteroid_command_returns_empty():
    """
    Verifies that an asteroid-only command list produces no robot output.
    The dispatcher should initialise the grid but return an empty result because
    no robot was created.
    """
    commands = [
        {"type": "asteroid", "size": {"x": 5, "y": 5}}
    ]
    result = execute_commands(commands)
    assert result == [], "Expected no robot output if no new-robot commands were given"


def test_initialise_new_robot_out_of_bounds():
    """
    Verifies validation of new robot starting coordinates.
    The dispatcher should reject a robot whose initial position is outside the
    asteroid grid.
    """
    commands = [
        {"type": "asteroid", "size": {"x": 5, "y": 5}},
        {"type": "new-robot", "position": {"x": 6, "y": 4}, "bearing": "north"}
    ]
    with pytest.raises(ValueError, match="New robot cannot be initialised out of bounds"):
        execute_commands(commands)


def test_execute_moves_without_new_robot():
    """
    Verifies that move commands require an active robot.
    The dispatcher should fail when a movement arrives before any new-robot
    command has established the current robot.
    """
    commands = [
        {"type": "asteroid", "size": {"x": 5, "y": 5}},
        {"type": "move", "movement": "turn-left"}
    ]
    with pytest.raises(ValueError, match="No robot available to execute move command"):
        execute_commands(commands)


def test_execute_unknown_command_type():
    """
    Verifies command type validation.
    The dispatcher should reject any message whose type is not one of the
    challenge-defined command types.
    """
    commands = [
        {"type": "asteroid", "size": {"x": 5, "y": 5}},
        {"type": "new-robot", "position": {"x": 1, "y": 2}, "bearing": "north"},
        {"type": "move", "movement": "turn-left"},
        {"type": "alien-anomaly", "position": {"x": 0, "y": 1}, "bearing": "north"}
    ]
    with pytest.raises(ValueError, match="Unknown command type: alien-anomaly"):
        execute_commands(commands)


def test_execute_new_robot_command_without_moves():
    """
    Verifies that a newly created robot is included in final output.
    The robot should be reported at its initial position when no movement
    commands follow it.
    """
    commands = [
        {"type": "asteroid", "size": {"x": 5, "y": 5}},
        {"type": "new-robot", "position": {"x": 1, "y": 2}, "bearing": "north"}
    ]
    result = execute_commands(commands)
    expected = [
        {"type": "robot", "position": {"x": 1, "y": 2}, "bearing": "north"}
    ]
    assert result == expected, "Expected one robot with initial state"


def test_execute_move_commands_for_single_robot():
    """
    Verifies movement dispatch for one robot.
    The command list turns a north-facing robot left, moves it forward, and then
    checks the final west-facing position.
    """
    commands = [
        {"type": "asteroid", "size": {"x": 5, "y": 5}},
        {"type": "new-robot", "position": {"x": 1, "y": 2}, "bearing": "north"},
        {"type": "move", "movement": "turn-left"},
        {"type": "move", "movement": "move-forward"}
    ]
    result = execute_commands(commands)
    expected = [
        {"type": "robot", "position": {"x": 0, "y": 2}, "bearing": "west"}
    ]
    assert result == expected, "Expected robot state after turning left and moving forward"


def test_execute_multiple_robots():
    """
    Verifies that command dispatch tracks multiple robots independently.
    Each new-robot command starts controlling a new current robot while previous
    robots retain their final state for output.
    """
    commands = [
        {"type": "asteroid", "size": {"x": 5, "y": 5}},
        {"type": "new-robot", "position": {"x": 1, "y": 2}, "bearing": "north"},
        {"type": "move", "movement": "turn-left"},
        {"type": "move", "movement": "move-forward"},
        {"type": "new-robot", "position": {"x": 3, "y": 3}, "bearing": "east"},
        {"type": "move", "movement": "move-forward"},
    ]
    result = execute_commands(commands)
    expected = [
        {"type": "robot", "position": {"x": 0, "y": 2}, "bearing": "west"},
        {"type": "robot", "position": {"x": 4, "y": 3}, "bearing": "east"}
    ]
    assert result == expected, "Expected output for multiple robot commands"

