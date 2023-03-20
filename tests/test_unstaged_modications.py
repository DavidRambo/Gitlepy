"""tests/test_unstaged_modifications.py

Tests the Repo class's unstaged_modifications property method.
"""
from pathlib import Path

from gitlepy.__main__ import main
from gitlepy.repository import Repo


def test_unstaged_modifications(runner, setup_repo):
    r = Repo(Path(setup_repo["work_path"]))
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "create a.txt"])
    file_a.write_text("Hello")
    result = r.unstaged_modifications()
    expected = ["a.txt (modified)"]
    assert expected == result


def test_staged_modifications(runner, setup_repo):
    """Stages for addition and ensures unstaged is empty."""
    r = Repo(Path(setup_repo["work_path"]))
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "create a.txt"])
    file_a.write_text("Hello")
    runner.invoke(main, ["add", "a.txt"])
    result = r.unstaged_modifications()
    expected = []
    assert expected == result
