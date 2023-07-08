# Start all the modules necessary for the simulation

cd robot
python3 navigation.py &
python3 odometry.py &
python3 regulator.py &
python3 scene.py &
# Acoustic objects detection:
python3 bearing.py  36000 37000 Cells &
python3 bearing.py  37000 38000 Frame &

cd ../simulation
python3 imu.py &
# Objects simulation: X  Y OBJ    DISP PERIOD PROB DIST
# python3 object.py    -5  5 BallR  0.10   0.25 0.99  90.0 &
# python3 object.py    -6  6 BallY  0.10   0.25 0.99  90.0 &
# python3 object.py    -7  5 BallG  0.10   0.25 0.99  90.0 &
# python3 object.py   -10 12 CellR  0.10   0.25 0.99  90.0 &
# python3 object.py   -10 11 CellY  0.10   0.25 0.99  90.0 &
# python3 object.py   -10 10 CellB  0.10   0.25 0.99  90.0 &
# python3 object.py  -3 11 Frame  0.50   1.00 1.00  90.0 &
# SoundDelay simulation:
python3 acoustic.py -9.5 10.5 2.0      0.01 36500 1.00  90.0 &
python3 acoustic.py  0.0 11.0 2.0      0.01 37500 1.00  90.0 &

cd ../pult
python3 map.py &
python3 keyboard.py
