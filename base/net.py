import socket
import pickle
import time

BUF = 32000
DELAY = 1.0


# Network communication
class Net:
    def __init__(self, timer=-1, msg=None, get_port=31000, set_ports=None, set_ip="255.255.255.255"):
        if set_ports is None:
            set_ports = [31000]
        if msg is None:
            msg = []
        self.timer = timer
        self.msg = msg
        self.set_ip = set_ip
        self.set_ports = set_ports

        self.start = time.time()
        self.next = self.start + self.timer + DELAY

        self.s_set = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.s_set.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.s_set.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        self.s_get = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.s_get.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.s_get.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.s_get.bind(('', get_port))

    def set(self, data):
        for port in self.set_ports:
            bytes_to_set = pickle.dumps(data)
            self.s_set.sendto(bytes_to_set, (self.set_ip, port))

    def get(self):
        if self.timer <= 0:
            # data = my.s_get.recv(BUF)
            data, addr = self.s_get.recvfrom(BUF)
            return pickle.loads(data)
        now = time.time()
        if now > self.next:
            self.next = self.next + self.timer
        timeout = max(0.0, self.next - now)
        self.s_get.settimeout(timeout)
        try:
            data, addr = self.s_get.recvfrom(BUF)
        except socket.timeout:
            return 'Timer'
        else:
            return pickle.loads(data)

