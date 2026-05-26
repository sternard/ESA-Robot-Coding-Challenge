import subprocess
import sys


def test_type_hints():
    """
    Verifies that the project passes mypy.
    The test shells out to the configured Python interpreter and fails with the
    mypy output if any type-checking issues are reported.
    """
    result = subprocess.run(
        [sys.executable, '-m', 'mypy', '.'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    assert result.returncode == 0, f"Type hints issues found:\n{result.stdout}\n{result.stderr}"
