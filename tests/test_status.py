"""Tests the status command as well as the Repo class's methods for
determining untracked and modified files.
"""
from pathlib import Path


from gitlepy.__main__ import main
from gitlepy.repository import Repo


def test_working_files(setup_repo):
    """Tests Repo.working_files method."""
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    working_result = repo.working_files()
    assert ["a.txt"] == working_result


def test_untracked_files(setup_repo):
    """Tests Repo.untracked_files method."""
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    untracked_result = repo.untracked_files()
    expected = ["a.txt"]
    assert type(untracked_result) == list
    assert untracked_result is not None
    assert expected == untracked_result


def test_unstaged_modifications_modified(runner, setup_repo):
    """Tests Repo.unstaged_modifications method by modifying a
    tracked file without staging for addition.
    """
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    file_a.write_text("hello")
    result = repo.unstaged_modifications()
    expected = ["a.txt (modified)"]
    assert expected == result


def test_unstaged_modifications_deleted(runner, setup_repo):
    """Tests Repo.unstaged_modifications method by deleting
    a tracked file without staging for removal.
    """
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    file_a.unlink()
    result = repo.unstaged_modifications()
    expected = ["a.txt (deleted)"]
    assert expected == result


def test_unstaged_modifications_untracked_staged_modified(runner, setup_repo):
    """Tests Repo.unstaged_modifications method by modifying
    an untracked file after it was staged for addition.
    """
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    file_a.write_text("hello")
    result = repo.unstaged_modifications()
    expected = ["a.txt (modified)"]
    assert expected == result


def test_unstaged_modifications_tracked_staged_modified(runner, setup_repo):
    """Tests Repo.unstaged_modifications method by modifying
    a file tracked by the current commit and already staged for addition.
    """
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    file_a.write_text("hello")
    runner.invoke(main, ["add", "a.txt"])
    file_a.write_text("hello, world")
    result = repo.unstaged_modifications()
    expected = ["a.txt (modified)"]
    assert expected == result


def test_unstaged_modifications_none(runner, setup_repo):
    """Tests Repo.unstaged_modifications method when no modifications
    are unstaged.
    """
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    file_a.write_text("hello")
    runner.invoke(main, ["add", "a.txt"])
    result = repo.unstaged_modifications()
    expected = []
    assert expected == result


def test_unstaged_modifications_untracked_added_deleted(runner, setup_repo):
    """Tests Repo.unstaged_modifications method for a staged, untracked file
    that has since been deleted.
    """
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    file_a.unlink()
    result = repo.unstaged_modifications()
    expected = ["a.txt (deleted)"]
    assert expected == result


def test_unstaged_modifications_removal_readded(runner, setup_repo):
    """Tests Repo.unstaged_modifications method by staging a file
    for removal and then adding it back to the working directory. It is now
    considered to be untracked.
    """
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    runner.invoke(main, ["rm", "a.txt"])
    file_a.touch()
    assert file_a.exists()

    result_1 = repo.unstaged_modifications()
    expected_1 = []
    assert expected_1 == result_1

    expected_2 = ["a.txt"]
    result_2 = repo.untracked_files()
    assert expected_2 == result_2


def test_status_branches(runner, setup_repo):
    """Checks status with multiple branches."""
    runner.invoke(main, ["branch", "dev"])
    result = runner.invoke(main, ["status"])
    expected = _status_helper(["dev", "*main"])
    assert expected == result.output


def test_status_staged(runner, setup_repo):
    """Checks status with staged files."""
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    result = runner.invoke(main, ["status"])
    expected = _status_helper(branches=["*main"], staged=["a.txt"])
    assert expected == result.output


def test_status_removed(runner, setup_repo):
    """Checks status with file staged for removal."""
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    runner.invoke(main, ["rm", "a.txt"])
    result = runner.invoke(main, ["status"])
    expected = _status_helper(branches=["*main"], removed=["a.txt"])
    assert expected == result.output


def test_status_mods_not_staged(runner, setup_repo):
    """Checks status with unstaged modifications."""
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    file_a.write_text("Hello")
    result = runner.invoke(main, ["status"])
    expected = _status_helper(branches=["*main"], modified=["a.txt (modified)"])
    assert expected == result.output


def test_status_untracked(runner, setup_repo):
    """Checks status with untracked files."""
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    result = runner.invoke(main, ["status"])
    expected = _status_helper(branches=["*main"], untracked=["a.txt"])
    assert expected == result.output


def test_status_full(runner, setup_repo):
    """Tests status with all four categories."""
    runner.invoke(main, ["branch", "dev"])
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    file_d = Path(setup_repo["work_path"] / "d.txt")
    file_d.touch()
    runner.invoke(main, ["add", "a.txt", "d.txt"])
    runner.invoke(main, ["commit", "Add a and d"])
    runner.invoke(main, ["rm", "d.txt"])  # removed
    file_b = Path(setup_repo["work_path"] / "b.txt")
    file_b.touch()  # untracked
    file_c = Path(setup_repo["work_path"] / "c.txt")
    file_c.touch()
    runner.invoke(main, ["add", "c.txt"])  # staged
    file_a.write_text("hi, a")  # mod but not staged
    expected = _status_helper(
        branches=["dev", "*main"],
        staged=["c.txt"],
        removed=["d.txt"],
        modified=["a.txt (modified)"],
        untracked=["b.txt"],
    )
    result = runner.invoke(main, ["status"])
    assert expected == result.output


def test_status_checkout_diff(runner, setup_repo):
    """Check status with two branches, each tracking different files."""
    # main branch
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["branch", "dev"])
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    assert file_a.exists()

    # dev branch
    runner.invoke(main, ["checkout", "dev"])
    assert not file_a.exists()
    file_b = Path(setup_repo["work_path"] / "b.txt")
    file_b.write_text("some text in dev branch\n")
    runner.invoke(main, ["add", "b.txt"])
    runner.invoke(main, ["commit", "Add b.txt"])

    # main branch
    runner.invoke(main, ["checkout", "main"])
    assert not file_b.exists()
    assert file_a.exists()
    result = runner.invoke(main, ["status"])
    expected = _status_helper(
        branches=["dev", "*main"],
    )
    assert expected == result.output  # b.txt should be gone


def test_status_after_merge(runner, setup_repo):
    """Check for clean status after merging two branches.
    This test features a merge conflict as well as an added file.
    """
    # main branch
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.write_text("text for a.txt")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])

    # dev branch
    runner.invoke(main, ["branch", "dev"])
    runner.invoke(main, ["checkout", "dev"])
    file_a.write_text("dev branch a.txt")
    file_b = Path(setup_repo["work_path"] / "b.txt")
    file_b.write_text("some text in dev branch\n")
    runner.invoke(main, ["add", "a.txt", "b.txt"])
    runner.invoke(main, ["commit", "Write to a.txt and b.txt"])

    # main branch
    runner.invoke(main, ["checkout", "main"])
    file_a.write_text("main branch a.txt")  # prevents fast-forwarding
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Write to a.txt"])
    r = Repo(Path.cwd())
    assert r.current_branch() == "main"
    merge_result = runner.invoke(main, ["merge", "dev"])
    expected = "Encountered a merge conflict.\n"
    assert expected == merge_result.output
    status_result = runner.invoke(main, ["status"])
    expected_status = _status_helper(branches=["dev", "*main"])
    assert expected_status == status_result.output


def _status_helper(
    branches: list[str] = [],
    staged: list[str] = [],
    removed: list[str] = [],
    modified: list[str] = [],
    untracked: list[str] = [],
) -> str:
    """Helper function to create status strings."""
    output = "=== Branches ===\n"
    for branch in branches:
        output += f"{branch}\n"
    output += "\n=== Staged Files ===\n"
    for file in staged:
        output += f"{file}\n"
    output += "\n=== Removed Files ===\n"
    for file in removed:
        output += f"{file}\n"
    output += "\n=== Modifications Not Staged For Commit ===\n"
    for file in modified:
        output += f"{file}\n"
    output += "\n=== Untracked Files ===\n"
    for file in untracked:
        output += f"{file}\n"

    output += "\n"  # for click.echo()'s added new line

    return output
