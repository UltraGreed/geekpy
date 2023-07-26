expect -c "
	spawn sh -c {./stop_on_board.sh auv}

	expect {
		-re \"auv@192.168.88.101's password:\" {
			send \"123\r\"
		}
	}

	interact {
		-o eof exit
	}
"
expect -c "
	spawn sh -c {./stop_on_board.sh rov}

	expect {
		-re \"auv@192.168.88.101's password:\" {
			send \"123\r\"
		}
	}

	interact {
		-o eof exit
	}
"

mode=$1

expect -c "
	spawn sh -c {./stop_on_board.sh $mode}

	expect {
		-re \"auv@192.168.88.101's password:\" {
			send \"123\r\"
		}
	}

	interact {
		-o eof exit
	}
"
expect -c "
	spawn sh -c {./install_all.sh}

	expect {
		-re \"auv@192.168.88.101's password:\" {
			send \"123\r\"
		}
	}

	interact {
		-o eof exit
	}
"
expect -c "
	spawn sh -c {./start_on_board.sh $mode}

	expect {
		-re \"auv@192.168.88.101's password:\" {
			send \"123\r\"
		}
	}

	interact {
		-o eof exit
	}
"

datetime=$(date +'%Y-%m-%d')
expect -c "
	spawn sh -c {ssh auv@192.168.88.101 /home/auv/geekpy/set_datetime.sh $datetime}

	expect {
		-re \"auv@192.168.88.101's password:\" {
			send \"123\r\"
		}
	}

	interact {
		-o eof exit
	}
"

datetime=$(date +'%H:%M:%S')
expect -c "
	spawn sh -c {ssh auv@192.168.88.101 /home/auv/geekpy/set_datetime.sh $datetime}

	expect {
		-re \"auv@192.168.88.101's password:\" {
			send \"123\r\"
		}
	}

	interact {
		-o eof exit
	}
"
