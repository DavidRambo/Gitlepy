from pathlib import Path

# import shutil
# import tempfile

import pytest


@pytest.fixture(autouse=True)
def change_dir(request, monkeypatch, tmp_path):
    """Changes the CWD to the test directory."""
    monkeypatch.chdir(request.fspath.dirname)
    monkeypatch.chdir(tmp_path)
    # repo.WORK_DIR = Path(tmp_path)
    # repo.GITLEPY_DIR = Path(tmp_path / ".gitlepy")
    # repo.BLOBS_DIR = Path(repo.GITLEPY_DIR / "blobs")
    # repo.COMMITS_DIR = Path(repo.GITLEPY_DIR / "commits")
    # repo.BRANCHES = Path(repo.GITLEPY_DIR / "refs")
    # repo.INDEX = Path(repo.GITLEPY_DIR / "index")
    # repo.HEAD = Path(repo.GITLEPY_DIR / "HEAD")


# @pytest.fixture(autouse=True)
# def setup_teardown():
#     """Cleans up the Gitlepy repository for subsequent tests."""
#     gitlepydir = repo.GITLEPY_DIR
#     print(f"\n>>>within setup_teardown, cwd={Path.cwd()}")
#     print(f"\n{repo.WORK_DIR=}")
#     print(f"\n{repo.GITLEPY_DIR=}")
#     print(f"\n{repo.BLOBS_DIR=}")
#     if gitlepydir.exists():
#         shutil.rmtree(gitlepydir)
#     yield
#     if gitlepydir.exists():
#         shutil.rmtree(gitlepydir)
