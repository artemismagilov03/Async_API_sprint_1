#!/usr/bin/env bash
set -x

ruff check --fix
ruff format
