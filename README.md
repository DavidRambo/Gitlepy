# Gitlepy
Python implementation of UC Berkeley's 61B's [Gitlet project](https://sp21.datastructur.es/materials/proj/proj2/proj2).

# Installation

Be sure to create a virtual environment.
I have been using `pyenv virtualenv` for this project, but in the snippet below, I use venv.

```
git clone https://github.com/DavidRambo/gitlepy.git

cd gitlepy

python3 -m venv venv

source venv/bin/activate

pip install --upgrade pip

pip install -r requirements

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
# TODO

## Refactor merge methods
Currently, `Repo.merge()` uses nested if blocks to determine the outcome of
a merge. Since this is visually messy, I would like to convert it to use sets.

## Convert Blob.file_contents to bytes
Currently, I follow the Gitlet spec, which uses straight string representations
of file contents. However, I would like to convert this to use bytes in order
to make use of Python's memoryview object and chunking. I do this with the sha1
hash of the Blob.
