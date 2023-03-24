# Gitlepy

Python implementation of UC Berkeley's 61B's [Gitlet project](https://sp21.datastructur.es/materials/proj/proj2/proj2).

This is a toy program for practicing Python, especially manipulating the file
system, managing growing complexity, type annotations, and learning the pytest and click libraries.
It's a fun project with room to grow—after all, it's a simplified take on git.
I have adhered closely to the assigned spec of the Gitlet project, and I intend
to make some further modifications (see [TODO](#TODO) below).

## Related projects

[Dulwich](https://github.com/jelmer/dulwich/): a git implementation in pure Python

# Installation

Be sure to create a virtual environment.
I have been using `pyenv virtualenv` for this project, but in the snippet below, I use venv.

```
git clone https://github.com/DavidRambo/gitlepy.git

cd gitlepy

python3 -m venv venv

source venv/bin/activate

pip install --upgrade pip

pip install -r requirements.txt

pip install -e .
```

At this point, you can run gitlepy while the virtual environment is activated:
```
gitlepy init
```
This will create a .gitlepy repository in the current working directory.

If you want to use the suite of dev tools:
```
pip install -r dev-requirements.txt

# And run pytest to make sure everything covered by tests works.
pytest
```

# Usage
Assuming you have installed the package into your environment, you can call gitlepy
to initialize a new gitlepy repository as follows:
```
$ gitlepy init
```

## Commands
Gitlepy has some basic version control commands:
- add {file names} : stage a file to the index for addition
- commit {"commit message"} : commit changes in the index to the repository
- rm {file names} : remove files from the staging area, if staged, or stages
                   for removal and deletes from working directory.
- branch {branch name} : create a branch
- branch -d {branch name} : delete a branch
- checkout {branch name} : check out a branch
- checkout -f {file name} : checks out the file from the HEAD commit
- checkout {commit id} -f {file name} : checks out the file from the specified commit
- reset {commit id} : Resets the working directory to the specified commit (can be abbreviated).
- log
- status
- merge {branch name} : merge the currently checked out branch with the specified branch

## Examples

Adding and committing files:
```
$ touch a.txt b.txt
$ gitlepy add a.txt b.txt
$ gitlepy commit "Create a.txt and b.txt"
```
Branches:
```
$ gitlepy branch dev
$ gitlepy checkout dev
```
(Do some work and return to `main` branch.)
```
$ gitlepy checkout main
$ gitlepy merge dev  # merge main with dev
$ gitlepy branch -d dev  # delete dev branch
```

# Organization

After trying to take an entirely functional approach, I opted to use classes to represent:
- Repo: a gitlepy repository
- Index: the staging area
- Commit: a commit object
- Blob: a blob object for tracking files across commits

Click, the library I use for command-line arguments, works well with this structure,
as it allows for a guaranteed instantiation of a `Repo` object, which is then passed
to the called command. The `main` function in gitlepy.__main__ serves as the `click.group`.
Here is the first distinction with Gitlet: an option to specify the working directory.
This turned out to be crucial for utilizing pytest's monkeypatch functionality to setup
and teardown temporary filesystems for testing.
Click also happens to have a [sample](https://click.palletsprojects.com/en/8.1.x/complex/#building-a-git-clone)
git-like interface, which was a serendipitous starting rubric.

The [`Repo` class](src/gitlepy/repository.py) handles nearly all of the logic.

# TODO

## Enable support for nested working directory and hidden files
Currently, gitlepy only works with non-hidden files in a flat directory.
To support hidden files, the glob() pattern used to ignore certain files will need to be
replaced with a list of files to be ignored (the .gitlepy directory, by default).
Supporting a .gitlepyignore file shouldn't be much more work.
Supporting a nested working tree would require refactoring the code that searches the working directory.

## Refactor merge methods
Currently, `Repo.merge()` uses nested conditional blocks to determine the outcome of
a merge. While using helper methods keeps it fairly approachable,
I would like to convert it to use sets.
Once the sets of various possible file states are composed,
basic set comparison operations would make for an elegant merge.

