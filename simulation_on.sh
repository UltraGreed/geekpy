# Start all the modules necessary for the simulation

python3 robot/navigation.py &
python3 robot/odometry.py &
python3 robot/regulator.py &
python3 robot/scene.py &

python3 simulation/imu.py &

# Objects simulation: x  y obj disp period
python3 simulation/object.py    -5  5 BallR  1 0.25 &
python3 simulation/object.py    -6  6 BallY  1 0.25 &
python3 simulation/object.py    -7  5 BallG  1 0.25 &
python3 simulation/object.py   -10 12 CellR  1 0.25 &
python3 simulation/object.py   -10 11 CellY  1 0.25 &
python3 simulation/object.py   -10 10 CellB  1 0.25 &
python3 simulation/object.py    -3 11 Frame  5 1.00 &

python3 pult/map.py &
python3 pult/keyboard.py
