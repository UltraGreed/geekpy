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
