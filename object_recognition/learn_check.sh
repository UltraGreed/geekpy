#!/bin/bash
(
  export PYTHONPATH=$(realpath ..)

  python learn.py
  python checker.py
)