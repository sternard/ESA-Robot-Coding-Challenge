import json
from src.commands import format_output


def test_format_output_with_no_robots():
    """
    Verifies output formatting for an empty robot list.
    The formatter should return an empty string so the CLI has nothing to print.
    """
    outputs = []
    formatted = format_output(outputs)
    assert formatted == "", "Expected empty string when no robot outputs are provided"


def test_format_output_with_single_robot():
    """
    Verifies output formatting for one robot.
    The formatter should return exactly one JSON object without adding extra
    lines or wrapping.
    """
    outputs = [
        {"type": "robot", "position": {"x": 1, "y": 2}, "bearing": "north"}
    ]
    formatted = format_output(outputs)
    expected_line = json.dumps(outputs[0])
    assert formatted == expected_line, "Expected formatted output to match the single robot JSON exactly"


def test_format_output_with_multiple_robots():
    """
    Verifies output formatting for multiple robots.
    The formatter should serialize each robot as JSON and join the messages with
    newline separators.
    """
    outputs = [
        {"type": "robot", "position": {"x": 1, "y": 2}, "bearing": "north"},
        {"type": "robot", "position": {"x": 3, "y": 4}, "bearing": "east"}
    ]
    formatted = format_output(outputs)
    expected_lines = "\n".join(json.dumps(robot) for robot in outputs)
    assert formatted == expected_lines, "Expected each robot JSON to be on a separate line"

