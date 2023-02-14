import shutil
import pytest

from gitlepy import repository as repo

# TODO: Setup new temporary directory for each test, and provide option to keep


@pytest.fixture(autouse=True)
def change_dir(request, monkeypatch):
    """Changes the CWD to the test directory."""
    monkeypatch.chdir(request.fspath.dirname)


@pytest.fixture(autouse=True)
def setup_teardown():
    """Cleans up the Gitlepy repository for subsequent tests."""
    gitlepydir = repo.GITLEPY_DIR
    if gitlepydir.exists():
        shutil.rmtree(gitlepydir)
    yield
    if gitlepydir.exists():
        shutil.rmtree(gitlepydir)
