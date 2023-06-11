# Start all the modules necessary for the simulation

cd robot
python3 navigation.py &
python3 odometry.py &
python3 regulator.py &
python3 scene.py &

cd ../simulation
python3 imu.py &

cd ../pult
python3 map.py &
python3 keyboard.py
