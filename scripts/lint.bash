#!/usr/bin/env bash
set -x

ruff check
ruff format --check
