import pytest
import io
import sys
import json
from src.robots import process_instructions


def test_process_instructions_from_file():
    """
    Verifies parsing from a file-like iterable.
    The input includes whitespace-only lines so the test can confirm they are
    ignored while valid JSON command lines are preserved.
    """
    instructions_content = (
        "   \n"
        '{"type": "asteroid", "size": {"x": 5, "y": 5}}\n'
        "\n"
        '{"type": "new-robot", "position": {"x": 1, "y": 2}, "bearing": "north"}\n'
        "    \n"
        '{"type": "move", "movement": "turn-left"}\n'
    )
    file_obj = io.StringIO(instructions_content)
    
    commands = process_instructions(file_obj)
    
    assert isinstance(commands, list)
    assert len(commands) == 3
    assert commands[0].get("type") == "asteroid"
    assert commands[2].get("type") == "move"


def test_process_instructions_returns_empty_list_for_empty_input():
    """
    Verifies empty string handling.
    A completely empty instruction payload should return an empty command list
    without attempting to dispatch anything.
    """
    instructions = ""
    
    result = process_instructions(instructions)
    
    assert result == [], "Expected an empty list for empty instructions"


def test_process_instructions_parses_valid_input():
    """
    Verifies parsing of valid JSON-line instruction text.
    The parser should return a list of command dictionaries and preserve the
    asteroid command as the first message.
    """
    instructions = "\n".join([
        '{"type": "asteroid", "size": {"x": 5, "y": 5}}',
        '{"type": "new-robot", "position": {"x": 1, "y": 2}, "bearing": "north"}',
        '{"type": "move", "movement": "turn-left"}'
    ])
    commands = process_instructions(instructions)
    assert isinstance(commands, list)
    assert len(commands) == 3
    assert commands[0].get("type") == "asteroid", "The first command must be an asteroid message."


def test_process_instructions_fails_for_malformed_json():
    """
    Verifies malformed JSON handling.
    The parser should surface json.JSONDecodeError when any instruction line is
    not valid JSON.
    """
    instructions = "\n".join([
        '{"type": "asteroid", "size": {"x": 5, "y": 5}}',
        '{"type": "new-robot", "position": {"x": 1, "y": 2}, "bearing": "north"'
    ])
    with pytest.raises(json.JSONDecodeError):
        process_instructions(instructions)


def test_process_instructions_fails_if_first_command_not_asteroid():
    """
    Verifies first-command validation.
    The parser should reject valid JSON instructions when the first command does
    not define the asteroid.
    """
    instructions = "\n".join([
        '{"type": "new-robot", "position": {"x": 1, "y": 2}, "bearing": "north"}',
        '{"type": "asteroid", "size": {"x": 5, "y": 5}}'
    ])
    with pytest.raises(ValueError, match="First command must be an asteroid"):
        process_instructions(instructions)


def test_process_instructions_fails_if_new_robot_not_initialised():
    """
    Verifies that movement cannot be the first robot command.
    After the asteroid message, a move command should fail because there is no
    active robot to control.
    """
    instructions = "\n".join([
        '{"type": "asteroid", "size": {"x": 5, "y": 5}}',
        '{"type": "move", "movement": "turn-left"}'
    ])
    with pytest.raises(ValueError, match="New robot must be initialised before a move instruction"):
        process_instructions(instructions)


def test_process_instructions_ignores_blank_lines():
    """
    Verifies that blank and whitespace-only lines are skipped.
    Only valid JSON command lines should appear in the returned command list.
    """
    instructions = "\n".join([
        "   ",
        '{"type": "asteroid", "size": {"x": 5, "y": 5}}',
        "",
        '{"type": "new-robot", "position": {"x": 1, "y": 2}, "bearing": "north"}',
        "    "
    ])
    commands = process_instructions(instructions)
    assert isinstance(commands, list)
    assert len(commands) == 2, "Expected only valid JSON lines to be processed, blank lines should be ignored"
    assert commands[0].get("type") == "asteroid"


def test_main_output_integration(tmp_path, monkeypatch, capsys):
    """
    Verifies the package CLI path through parsing, dispatch, and formatting.
    The test writes a temporary instructions file, patches sys.argv, runs main,
    and asserts the final stdout JSON message.
    """
    instructions_content = (
        '{"type": "asteroid", "size": {"x": 5, "y": 5}}\n'
        '{"type": "new-robot", "position": {"x": 1, "y": 2}, "bearing": "north"}\n'
        '{"type": "move", "movement": "turn-left"}\n'
        '{"type": "move", "movement": "move-forward"}\n'
    )
    instructions_file = tmp_path / "instructions.txt"
    instructions_file.write_text(instructions_content)
    
    monkeypatch.setattr(sys, 'argv', ['robots.py', str(instructions_file)])
    
    from src.robots import main
    main()
    
    output = capsys.readouterr().out.strip()
    
    expected_output = '{"type": "robot", "position": {"x": 0, "y": 2}, "bearing": "west"}'
    
    assert output == expected_output, f"Expected: {expected_output}, but got: {output}"

