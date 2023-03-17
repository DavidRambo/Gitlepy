"""tests/test_checkout.py"""
from pathlib import Path

from gitlepy.__main__ import main


def test_checkout_no_operands(runner, setup_repo):
    """Tries to checkout nothing."""
    result = runner.invoke(main, ["checkout"])
    assert result.output == "Incorrect operands.\n"


def test_checkout_file_invalid_target(runner, setup_repo):
    """Tries to checkout a file from a non-existent commit."""
    result = runner.invoke(main, ["checkout", "abc56e", "-f", "a.txt"])
    assert result.output == "abc56e is not a valid commit.\n"


def test_checkout_file_no_such_file_HEAD(runner, setup_repo):
    """Tries to checkout a file that does not exist in the HEAD."""
    result = runner.invoke(main, ["checkout", "-fa.txt"])
    assert result.output == "a.txt is not a valid file.\n"


def test_checkout_branch_does_not_exist(runner, setup_repo):
    """Tries to checkout a non-existent branch."""
    result = runner.invoke(main, ["checkout", "dev"])
    assert result.output == "dev is not a valid branch name.\n"


def test_checkout_already_on_branch(runner, setup_repo):
    """Tries to checkout currently checked out branch."""
    result = runner.invoke(main, ["checkout", "main"])
    assert result.output == "Already on 'main'\n"


def test_checkout_new_branch(runner, setup_repo):
    """Creates a new branch and checks it out."""
    runner.invoke(main, ["branch", "dev"])  # create branch called dev
    result = runner.invoke(main, ["checkout", "dev"])
    assert result.output == ""  # No stdout
    assert setup_repo["head"].read_text() == "dev"  # HEAD updated
    # dev branch is on same commit as main
    main_path = Path(setup_repo["branches"] / "main")
    main_head = main_path.read_text()
    dev_path = Path(setup_repo["branches"] / "dev")
    dev_head = dev_path.read_text()
    assert main_head == dev_head


def test_checkout_file_head(runner, setup_repo):
    """Checks out a file from the current HEAD commit."""
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    file_a.write_text("Hello")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Hello > a.txt"])
    file_a.write_text("Hello, gitlepy.")
    result = runner.invoke(main, ["checkout", "-f", "a.txt"])
    assert result.output == ""
    assert file_a.read_text() == "Hello"


def test_checkout_branch_files(runner, setup_repo):
    """Checks out a branch, changes files, and checks out previous branch."""
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    file_a.write_text("Hello")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Hello > a.txt"])

    file_b = Path(setup_repo["work_path"] / "b.txt")
    file_b.touch()
    file_b.write_text("Hi")
    runner.invoke(main, ["add", "b.txt"])
    runner.invoke(main, ["commit", "Hi > b.txt"])

    runner.invoke(main, ["branch", "dev"])  # create dev branch
    runner.invoke(main, ["checkout", "dev"])  # checkout dev

    file_a.write_text("Hello, dev.")
    file_b.write_text("Hi, dev.")
    runner.invoke(main, ["add", "a.txt", "b.txt"])
    # runner.invoke(main, ["add", "b.txt"])
    runner.invoke(main, ["commit", "add dev to a and b"])

    # Checkout main and validate file contents.
    runner.invoke(main, ["checkout", "main"])
    assert file_a.read_text() == "Hello"
    assert file_b.read_text() == "Hi"


def test_reset(runner, setup_repo):
    """Resets to earlier commit."""
    # First commit has a.txt
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    file_a.write_text("Hello")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Hello > a.txt"])

    # Retrieve that commit id for future reset command.
    main_ref = Path(setup_repo["branches"] / "main")
    commit_a = main_ref.read_text()

    # Second commit adds b.txt
    file_b = Path(setup_repo["work_path"] / "b.txt")
    file_b.touch()
    file_b.write_text("Hi")
    runner.invoke(main, ["add", "b.txt"])
    runner.invoke(main, ["commit", "Hi > b.txt"])

    # Third commit writes text to a.txt
    file_a.write_text("Hello, main.")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Hello, main. > a.txt"])

    # Reset to first commit and ensure b.txt is gone.
    runner.invoke(main, ["reset", commit_a])
    assert not file_b.exists()
    assert main_ref.read_text() == commit_a


def test_abbreviated_commit(runner, setup_repo):
    """Resets to earlier commit using abbreviated id."""
    # First commit has a.txt
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    file_a.write_text("Hello")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Hello > a.txt"])

    # Retrieve current commit's id
    main_ref = Path(setup_repo["branches"] / "main")
    commit_a = main_ref.read_text()
    # Take a slice of that commit id:
    abbreviated_a = commit_a[:6]
    print(f"\n>>>>>\n{commit_a=}\n")
    print(f"\n{abbreviated_a=}\n<<<<<\n")

    # Make new commit
    file_b = Path(setup_repo["work_path"] / "b.txt")
    file_b.touch()
    file_b.write_text("Hi")
    runner.invoke(main, ["add", "b.txt"])
    runner.invoke(main, ["commit", "Hi > b.txt"])

    result = runner.invoke(main, ["reset", abbreviated_a])
    assert result.exit_code == 0
    assert main_ref.read_text() == commit_a


def test_checkout_file_abbreviated_commit(runner, setup_repo):
    """Checks out a file from abbreviated commit id."""
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    file_a.write_text("Hello")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Hello > a.txt"])

    # Retrieve current commit' id
    main_ref = Path(setup_repo["branches"] / "main")
    commit_a = main_ref.read_text()
    # Take a slice of that commit id:
    abbreviated_a = commit_a[:6]

    # Make new commit
    file_a.write_text("Updated text")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Updated text > a.txt"])

    result = runner.invoke(main, ["checkout", abbreviated_a, "-f", "a.txt"])
    assert result.exit_code == 0
    assert result.output == ""

    assert "Hello" == file_a.read_text()
