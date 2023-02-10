# tests/main_tests.py
"""Tests the main.py module."""
from click.testing import CliRunner
import pytest

from gitlepy.main import main


@pytest.fixture
def runner():
    return CliRunner()


def test_main_no_arguments(runner):
    """Check for main.py run without any arguments."""
    # result = runner.invoke(main, ["init"])
    result = runner.invoke(main, [""])
    assert result.exit_code == 0
    assert result.output == "Incorrect operands.\n"


# def test_main_no_arguments(capsys):
#     """Runs main.py without any argument."""
#     gitlepy.main([""])

#     out, err = capsys.readouterr()
#     assert out == "Incorrect operands."
#     assert err == ""
