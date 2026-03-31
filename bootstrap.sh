#!/bin/bash

mkdir -p logs

exec python frontend/ivan_is_gay.py >> logs/frontend.log 2>&1
