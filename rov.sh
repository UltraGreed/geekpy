#!/bin/bash
# Turn on robot software
(
  export PYTHONPATH=$(pwd)

  cd robot

  thon physoptic.py &
  python navigation.py &
  python odometry.py &
  python regulator.py &
  python spreader.py &
  python kotleta.py &

  python ctd_i2c.py &

  #                              photo stream
  python3 zed.py Bottom 24827734 True  True &
  python3 zed.py Front  16909428 True  True &
)
