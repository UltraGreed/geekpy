import socket
import pickle
import time
import math
import struct

BUF   = 32000
DELAY = 1.0

# Network communucation
class Net:

	def __init__(my, timer=-1, msg=[], get_port=31000, set_ports=[31000], set_ip="255.255.255.255"):
		my.timer     = timer
		my.msg       = msg
		my.set_ip    = set_ip
		my.set_ports = set_ports
		my.start     = time.time()
		my.next      = my.start + my.timer + DELAY
		my.s_set     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		my.s_set.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		my.s_set.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		my.s_get     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		my.s_get.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		my.s_get.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		my.s_get.bind(('', get_port))
 		
	def set(my, data):
		for port in my.set_ports:
			bytes = pickle.dumps(data)
			my.s_set.sendto(bytes, (my.set_ip, port))

	def get(my):
		if my.timer <= 0:
			# data = my.s_get.recv(BUF)
			data, addr = my.s_get.recvfrom(BUF)
			return pickle.loads(data)
		now = time.time()
		if now > my.next:
			my.next = my.next + my.timer
		timeout = max(0.0, my.next - now)
		my.s_get.settimeout(timeout)
		try:
			data, addr = my.s_get.recvfrom(BUF)
		except socket.timeout:
			return 'Timer'
		else:
			return pickle.loads(data)
