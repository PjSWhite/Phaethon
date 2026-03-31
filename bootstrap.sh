#!/bin/bash

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

cd $SCRIPT_DIR || exit 1
mkdir -p logs

exec python frontend/ivan_is_gay.py >> logs/frontend.log 2>&1
