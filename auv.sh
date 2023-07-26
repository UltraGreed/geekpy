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
#  python ctd_aurt.py &

  python acoustic.py &
  python bearing.py 29500 30500 Frame &

  python gpio.py &

  #                              pos_tracking stream
  python3 zed.py Bottom 24827734 True          True &
  sleep 5
  python3 zed.py Front  16909428 False         True &

  python3 obj_recogn.py Bottom CellB ../object_recognition/model_divided.npy &
)
