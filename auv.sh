#!/bin/bash
# Turn on robot software
(
	export PYTHONPATH=$(pwd)

	cd robot
	# python3 scene.py &

	python physoptic.py &
	python main.py &
	python odometry.py &
	python kotleta.py &

	python ctd_i2c_exp.py &
	# python ctd_uart.py &

	# python acoustic.py &
	# python bearing.py 29500 30500 Cells &
	# python bearing.py 37000 38000 Frame &

	python gpio.py &

	#                              pos_tracking stream
	python3 zed.py --camera-orientation Bottom --serial 24827734 --img-capture &
	sleep 5
	python3 zed.py --camera-orientation Front --serial 16909428 --disable-orientation --img-capture &

	#                   camera_name  model_type  model_name   object_name
	#   python3 obj_recogn.py Bottom        sub      CellR           CellR &
	# python3 obj_recogn.py Bottom        sub      CellY           CellY &

	#                   camera_name  model_type  model_name
	python3 obj_recogn_target.py Front sub Target &
)
