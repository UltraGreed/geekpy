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
)
