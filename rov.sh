#!/bin/bash
# Turn on robot software
(
  export PYTHONPATH=$(pwd)

  cd robot

  python physoptic.py &
  python navigation.py &
  python odometry.py &
  python regulator.py &
  python spreader.py &
  python kotleta.py &

#  python ctd_i2c.py &
  python ctd_aurt.py &

  #                              pos_tracking stream
  python3 zed.py Bottom 24827734 True          True &
  sleep 3
  python3 zed.py Front  16909428 False         True &
)
