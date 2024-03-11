#!/bin/bash
# Turn on robot software
(
	export PYTHONPATH=$(pwd)

	cd robot

	#  python physoptic.py &
	python odometry.py &
	python main.py &
	python kotleta.py &

	python ctd_i2c.py &
	python ctd_uart.py &

	python gpio.py &

	#                              pos_tracking stream
	python3 zed.py --camera-orientation Bottom --serial 24827734 --img-capture &
	sleep 5
	python3 zed.py --camera-orientation Front --serial 16909428 --disable-orientation --img-capture &
)
