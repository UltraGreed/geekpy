#!/bin/bash
(
  export PYTHONPATH=$(realpath ..)

  python train.py "$@" &&
  ./renormalize.sh "$@"
)
