# Start all the modules necessary for the simulation
(
  export PYTHONPATH=$(pwd)

  cd robot
  python3 main.py &
  python3 odometry.py &
  python3 scene.py &

  cd ../simulation
  python3 imu.py &

  cd ../tasks
  python3 spiral_test.py
)
