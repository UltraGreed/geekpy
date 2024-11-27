#!/bin/bash
(
  export PYTHONPATH=$(realpath ..)

  python train.py "$1" &&
  python normalize.py "$1" &&
  python histograms.py "$1" &&
  python checker.py "$1"
)
