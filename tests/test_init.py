# tests/test_init.py
"""Tests the init command."""
from pathlib import Path
import shutil

from click.testing import CliRunner
import pytest

from gitlepy.main import main
import gitlepy.repository as repo


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def setup_teardown():
    """Cleans up the Gitlepy repository for subsequent tests."""
    workdir = repo.WORK_DIR
    if workdir.exists():
        shutil.rmtree(workdir)
    yield
    if workdir.exists():
        shutil.rmtree(workdir)


def test_main_init_new_repo(runner, tmp_dir="tmp_dir"):
    """Creates a new repository successfully.
    Uses click.testing's CliRunner.isolated_filesystem() to create a temporary
    directory in which gitlepy sets up its repository.
    https://click.palletsprojects.com/en/8.1.x/testing/#file-system-isolation
    """
    with runner.isolated_filesystem(temp_dir=tmp_dir):
        result = runner.invoke(main, ["init"])
        assert repo.WORK_DIR.exists()
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
    with runner.isolated_filesystem():
        repo.WORK_DIR.mkdir()
        repo.GITLEPY_DIR.mkdir()
        result = runner.invoke(main, ["init"])
        assert result.exit_code == 0
        assert result.output == "Gitlepy repository already exists.\n"
