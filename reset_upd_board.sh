expect -c "
	spawn sh -c {./stop_on_board.sh}

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
	spawn sh -c {./start_on_board.sh}

	expect {
		-re \"auv@192.168.88.101's password:\" {
			send \"123\r\"
		}
	}

	interact {
		-o eof exit
	}
"
