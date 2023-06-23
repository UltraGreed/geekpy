# Start all the modules necessary for the simulation

cd robot
python3 navigation.py &
python3 odometry.py &
python3 regulator.py &
python3 scene.py &

cd ../simulation
python3 imu.py &

# Objects simulation: x  y obj disp period
python3 object.py    -5  5 BallR  1 0.25 &
python3 object.py    -6  6 BallY  1 0.25 &
python3 object.py    -7  5 BallG  1 0.25 &
python3 object.py   -10 12 CellR  1 0.25 &
python3 object.py   -10 11 CellY  1 0.25 &
python3 object.py   -10 10 CellB  1 0.25 &
python3 object.py    -3 11 Frame  5 1.00 &

cd ../pult
python3 map.py &
python3 keyboard.py
