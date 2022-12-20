#!/usr/bin/env -S just --justfile

# Config
# =====================================================================

set dotenv-load := true
set shell := [ "bash", "-euo", "pipefail", "-c" ]

# these names are short because they will be used a lot
FROM := invocation_directory()
HERE := justfile_directory()
SELF := justfile()
SHELL := file_stem(`test -n "$0" && echo "$0" || status fish-path`)

# more explicit names are exported
export JUSTFILE := SELF
export JUSTFILE_DIR := HERE
export JUST_INVOCATION_DIR := FROM
export JUST_INVOCATION_SHELL := SHELL

# Handy bits
t := "true"
f := "false"

# Path of .env file (not configurable)
dotenv := HERE / ".env"
dotexample := HERE / ".env.example"

# The Python executable used to create the project virtualenv
srcpy := env_var_or_default("DRF_STUBS_PYTHON", "python3")

# The path at which to create the project virtualenv
venv_dir := env_var_or_default("DRF_STUBS_VENV", HERE / ".venv")
venv_bin := venv_dir / "bin"
venv_act := venv_bin / "activate" + if SHELL =~ '^(fi|c)sh$' { "." + SHELL } else { "" }

# The Python executable of the project virtualenv
pyexe := venv_bin / "python"

# The version of DRF for which to test and build
export DRF_VERSION := env_var_or_default("DRF_VERSION", "3.14.0")

export PATH := venv_bin + ":" + env_var("PATH")


# Aliases
# =====================================================================

alias h := help
alias t := test
alias rm := clean
alias clear := clean


# Recipes
# =====================================================================

## General
## --------------------------------------------------------------------

# run this recipe if no arguments are given (by virtue of it being the *first* recipe)
@_default: ls

# list available recipes
@ls:
  "{{ SELF }}" --list --unsorted

# print help info & list available recipes
@help: && ls
  "{{ SELF }}" --help


## Development
## --------------------------------------------------------------------

# refresh setup, run checks & builds
full: clean setup lint test build

# remove development artifacts
clean: _clean-precommit _clean-setuptools _clean-project

# uninstall pre-commit hooks and clean up artifacts
_clean-precommit:
  -pre-commit uninstall
  -pre-commit clean
  -pre-commit gc

# run setuptools clean command, delete other artifacts
_clean-setuptools:
  -"{{ if path_exists(pyexe) == t { pyexe } else { srcpy } }}" setup.py clean --all
  -rm -rf ./*.egg-info
  -rm -rf ./build
  -rm -rf ./dist

# remove all artifacts not removed by other cleaners
_clean-project:
  -rm -rf "{{ venv_dir }}"
  -rm -rf ./.*cache
  @# Remove the dotenv file if it is no different from the example one.
  -! diff -q "{{ dotenv }}" "{{ dotexample }}" >/dev/null 2>&1 || rm "{{ dotenv }}"
  @# TODO: Consider deleting these safely by using a prompt & --noinput switch.
  @echo "Manually delete the following, if needed:"
  @printf -- "    %s\n" $(python scripts/paths.py)


# setup up project development environment
setup:
  @"{{ SELF }}" {{ if path_exists(pyexe) == f { "_setup" } else { "_install" } }}
  @echo "If needed, generate draft stubs by running 'just draft-stubs"

# create virtualenv, install requirements
_setup: && _install
  test -e "{{ dotenv }}" || cp "{{ dotexample }}" "{{ dotenv }}"
  test ! -e "{{ venv_dir }}" || rm -rf "{{ venv_dir }}"
  "{{ srcpy }}" -m venv "{{ venv_dir }}"

_install:
  "{{ pyexe }}" -m pip install -U pip setuptools wheel
  "{{ pyexe }}" -m pip install -r requirements.txt nox
  "{{ pyexe }}" -m pre_commit install --install-hooks

# generate new draft stub files
draft-stubs:
  "{{ pyexe }}" scripts/stubgen-drf.py --drf_version "$DRF_VERSION"


## Lint & Test
## --------------------------------------------------------------------

# run all linters & checkers
lint: lint-precommit

# run pre-commit hooks
lint-precommit *ARGS:
  @# "{{ pyexe }}" -m pre_commit run --all-files {{ ARGS }}
  "{{ pyexe }}" -m nox -e precommit {{ ARGS }}

# run all tests
test: test-py test-drf

# run unit tests w/ pytest
test-py *ARGS:
  @# see `.github/workflows/tests.yml:jobs.test.steps`
  @# "{{ pyexe }}" -m pytest {{ ARGS }}
  "{{ pyexe }}" -m nox -e pytest {{ ARGS }}

# typecheck DRF tests w/ mypy using project stubs
test-drf:
  @# see `.github/workflows/tests.yml:jobs.typecheck.steps`
  @# "{{ pyexe }}" scripts/typecheck_tests.py --drf_version "$DRF_VERSION"
  "{{ pyexe }}" -m nox -e typecheck


## Build
## --------------------------------------------------------------------

# build rest_framework-stubs package
build:
  @# "{{ pyexe }}" -m pip install --upgrade setuptools wheel
  @# "{{ pyexe }}" setup.py check sdist bdist_wheel
  "{{ pyexe }}" -m nox -e build


## Release
## --------------------------------------------------------------------

# build & release rest_framework-stubs package
release: full
  @# "{{ pyexe }}" -m pip install --upgrade setuptools wheel twine
  @# . "{{ venv_act }}" && ./scripts/release.sh
  "{{ pyexe }}" -m nox -e release


## Meta
## --------------------------------------------------------------------

# update the included .env.example file
update-dotenv:
  # Not yet implemented

update-noxfile:
  # Not yet implemented
