from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any, TextIO, cast

from src.commands import execute_commands, format_output


Command = dict[str, Any]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run ESA asteroid robot instructions from a JSON-lines file.",
    )
    parser.add_argument(
        "instructions",
        type=Path,
        help="Path to a text file containing one JSON command per line.",
    )
    return parser


def read_commands(instructions_file: TextIO) -> Iterator[Command]:
    for line_number, line in enumerate(instructions_file, start=1):
        stripped_line = line.strip()
        if not stripped_line:
            continue

        try:
            command: object = json.loads(stripped_line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_number}") from exc

        if not isinstance(command, dict):
            raise ValueError(f"Command on line {line_number} must be a JSON object")

        yield cast(Command, command)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    instructions_path: Path = args.instructions

    try:
        with instructions_path.open(encoding="utf-8") as instructions_file:
            output = format_output(execute_commands(list(read_commands(instructions_file))))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if output:
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
