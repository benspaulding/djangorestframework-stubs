#!/usr/bin/env -S python -m nox --noxfile
"""
Automated development tasks via `nox <https://nox.thea.codes>`_.

Example usage::

    nox  # defaults to listing available sessions
    nox -s precommit  # run only named session(s)
    nox -t dev  # run only sessions having tag(s)
    nox -p 3.10 3.7 -s pytest  # Run pytest against Python 3.10 and 3.7
    nox -h  # show nox help
    ./noxfile.py  # the file is executable
"""
from typing import Final

import nox

nox.needs_version = ">=2022.11.21"
nox.options.reuse_existing_virtualenvs = True
nox.options.envdir = ".nox_cache"
nox.options.sessions = ["ls"]

PYTHONS: Final = [
    "3.10",
    "3.9",
    "3.8",
    "3.7",
]
DJANGOS: Final = [
    # "4.1.4",
    # "4.0.8",
    "3.2.16",
]
DRFS: Final = [
    "3.14.0",
    # "3.13.1",
    # "3.12.4",
    # "3.11.2",
]

PYTHON: Final = PYTHONS[0]
TEST: Final = "test"
DEV: Final = "dev"


@nox.session
def ls(session: nox.Session) -> None:
    """list available sessions"""
    session.run("nox", "-l")


@nox.session(python=PYTHON, tags=[DEV])
def precommit(session: nox.Session) -> None:
    """run pre-commit hooks on all files"""
    _setup(session)
    session.install("pre-commit")
    session.run("python", "-m", "pre_commit", "run", "--all-files", *session.posargs)


@nox.session(python=PYTHONS, tags=[DEV, TEST])
@nox.parametrize("django", DJANGOS)
@nox.parametrize("drf", DRFS)
def pytest(session: nox.Session, django: str, drf: str) -> None:
    """run pytest test suite"""
    _setup(session)
    session.install(f"django=={django}")
    session.install(f"djangorestframework=={drf}")
    session.install("pytest")
    session.run("python", "-m", "pytest", *session.posargs)


@nox.session(python=PYTHONS, tags=[DEV, TEST])
@nox.parametrize("django", DJANGOS)
@nox.parametrize("drf", DRFS)
def typecheck(session: nox.Session, django: str, drf: str) -> None:
    """run typecheck tests"""
    _setup(session)
    session.install(f"django=={django}")
    session.install(f"djangorestframework=={drf}")
    session.run("python", "scripts/typecheck_tests.py", "--drf_version", drf)


@nox.session(python=PYTHON)
def build(session: nox.Session) -> None:
    """build a distribution"""
    _setup(session)
    session.run("python", "setup.py", "check", "sdist", "bdist_wheel")


@nox.session(python=PYTHON)
def release(session: nox.Session) -> None:
    """release a distribution"""
    _setup(session)
    session.install("--upgrade", "twine")
    session.run("./scripts/release.sh")


def _setup(session: nox.Session) -> None:
    """common session setup work"""
    session.install("--upgrade", "setuptools", "wheel")
    session.install("-r", "requirements.txt")
