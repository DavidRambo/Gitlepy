import shutil
import pytest

from gitlepy import repository as repo


@pytest.fixture(autouse=True)
def change_dir(request, monkeypatch, tmp_path):
    """Changes the CWD to the test directory."""
    # monkeypatch.chdir(request.fspath.dirname)
    monkeypatch.chdir(tmp_path)


@pytest.fixture(autouse=True)
def setup_teardown():
    """Cleans up the Gitlepy repository for subsequent tests."""
    gitlepydir = repo.GITLEPY_DIR
    if gitlepydir.exists():
        shutil.rmtree(gitlepydir)
    yield
    if gitlepydir.exists():
        shutil.rmtree(gitlepydir)
