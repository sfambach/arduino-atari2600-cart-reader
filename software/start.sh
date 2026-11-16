#!/bin/sh
# Starts the PC program from its folder; creates the venv and installs the requirements on the first run.
# Arguments are passed on, e.g. ./start.sh --demo
cd "$(dirname "$0")" || exit 1
if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv || { echo "python3-venv missing: sudo apt install python3-venv libxcb-cursor0"; exit 1; }
    .venv/bin/pip install -r requirements.txt || exit 1
fi
exec .venv/bin/python -m acr "$@"
