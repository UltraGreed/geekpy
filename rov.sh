# Turn on robot software
(
  export PYTHONPATH=$(pwd)

  cd robot

  # python physoptic.py &
  python navigation.py &
  python odometry.py &
  python regulator.py &
  python spreader.py &
  python kotleta.py &

  python depth_meter.py &

  python3 zed.py bottom 24827734 True &
  # python3 zed.py front 16909428 False &
)
