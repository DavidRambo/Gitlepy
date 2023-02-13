# tests/test_init.py
"""Tests the init command."""
from pathlib import Path

from click.testing import CliRunner
import pytest

from gitlepy.__main__ import main
import gitlepy.repository as repo


@pytest.fixture
def runner():
    return CliRunner()


def test_main_init_new_repo(runner):
    """Creates a new repository successfully.
    Uses click.testing's CliRunner.isolated_filesystem() to create a temporary
    directory in which gitlepy sets up its repository.
    https://click.palletsprojects.com/en/8.1.x/testing/#file-system-isolation
    """
    # with runner.isolated_filesystem(tmp_path):
    #     print(f"\n>>>>\n{tmp_path=}\n<<<<<\n")
    # print(f"\n<<<<\n{Path.cwd()=}\n>>>>>\n")
    result = runner.invoke(main, ["init"])
    assert repo.GITLEPY_DIR.exists()
    assert repo.BLOBS_DIR.exists()
    assert repo.COMMITS_DIR.exists()
    assert repo.INDEX.exists()

    main_branch = Path(repo.BRANCHES / "main")
    assert main_branch.exists()

    assert repo.HEAD.exists()
    assert repo.HEAD.read_text() == "main"

    assert result.exit_code == 0
    assert result.output == "Initializing gitlepy repository.\n"


def test_main_init_already_exists(runner):
    """Tries to create a new repository where one already exists."""
    # with runner.isolated_filesystem():
    # print(tmp_path)
    repo.GITLEPY_DIR.mkdir()
    result = runner.invoke(main, ["init"])
    assert result.exit_code == 0
    assert result.output == "Gitlepy repository already exists.\n"
