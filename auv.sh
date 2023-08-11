#!/bin/bash
# Turn on robot software
(
  export PYTHONPATH=$(pwd)

  cd robot
  python3 scene.py &

#  python physoptic.py &
  python navigation.py &
  python odometry.py &
  python regulator.py &
  python spreader.py &
  python kotleta.py &

  python ctd_i2c.py &
  python ctd_uart.py &

  python acoustic.py &
  python bearing.py 29500 30500 Cells &
  python bearing.py 37000 33800 Frame &

  python gpio.py &

  #                              pos_tracking stream
  python3 zed.py Bottom 24827734 True         False &
  sleep 5
  python3 zed.py Front  16909428 False        False &

  #                   camera_name  model_type  model_name   object_name
  python3 obj_recogn.py Bottom        sub      CellR           CellR &
  python3 obj_recogn.py Bottom        sub      CellY           CellY &
  python3 obj_recogn.py Front         sub      BallY           BallY &
)
