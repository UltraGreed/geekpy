#!/bin/bash
# Turn on robot software
(
  export PYTHONPATH=$(pwd)

  sh ./offpy.sh

  launch_old=$(cat /media/ssd/launch_number.txt)
  launch_new=$((launch_old + 1))

  echo "$launch_new" > /media/ssd/launch_number.txt

  cd robot
  python3 scene.py &

  python physoptic.py &
  python main.py &
  python odometry.py &
  python kotleta.py &

  # python ctd_i2c_lin.py &
  python ctd_uart.py &

  python acoustic.py &
  python bearing.py 29500 30500 Pinger &

  python gpio.py &

  #                              pos_tracking stream
  python3 zed.py --camera-orientation Bottom --serial 24827734 --img-capture --save-mode Right &
  #	sleep 5
  #	python3 zed.py --camera-orientation Front --serial 16909428 --disable-orientation --img-capture &

  #                      camera_name    model_name   object_name
  #   python3 obj_recogn.py Bottom        CellR         CellR &
  #   python3 obj_recogn.py Bottom        CellY         CellY &

  #                   camera_name model_name
  python line_recogn.py Bottom.right LineRedFEFU 0.75 0.01 &
  python obj_recogn.py Bottom.right SquareBlackFEFU SquareBlack 0.35 0.075 &
  python obj_recogn.py Bottom.right SquareOrangeFEFU SquareOrange 0.35 0.1 &
  python obj_recogn.py Bottom.right SquareGreenFEFU SquareGreen 0.75 0.025 &

  #	python aruco.py Bottom.right Aruco &
)
