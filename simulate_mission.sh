# Start all the modules necessary for the simulation
(
  export PYTHONPATH=$(pwd)

  cd robot
  python3 navigation.py &
  python3 odometry.py &
  python3 regulator.py &
  python3 scene.py &
  # Acoustic objects detection:
  python3 bearing.py  29500 30500 Cells &
  python3 bearing.py  37000 38000 Frame &

  cd ../pult
  python3 map.py &

  cd ../tasks
  python3 test_mission.py &

  cd ../simulation
  python3 imu.py &

# Objects simulation:    X    Y   OBJ    DISP PERIOD PROB DIST
  # python3 object.py    -5.5  5.5 BallR  0.10   0.25 0.98  1.0 &
  # python3 object.py    -6.5  6.5 BallY  0.10   0.25 0.98  1.0 &
  # python3 object.py    -7.5  5.5 BallG  0.10   0.25 0.98  1.0 &
  # python3 object.py   -10.5 12.0 CellR  0.10   0.25 0.98  1.0 &
  # python3 object.py   -10.5 11.5 CellY  0.10   0.25 0.98  1.0 &
  # python3 object.py   -10.5 11.0 CellB  0.10   0.25 0.98  1.0 &
  # # python3 object.py    -3   11   Frame  0.50   1.00 1.00  90.0 &
  # # SoundDelay simulation:
  # python3 acoustic.py -10.5 10.5 1.2      0.01 30000 9.95  50.0 &
  # python3 acoustic.py  -7.0 12.2 2.0      0.01 37500 9.95  50.0 &
)
