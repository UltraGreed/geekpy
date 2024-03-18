import copy
import pickle
import json
import socket
import time

from base import message

msg_table = message.get_msg_table()

DELAY_OSError = 5.0

if not hasattr(socket, "SO_REUSEPORT"):
    socket.SO_REUSEPORT = socket.SO_REUSEADDR


class MessageJSONEncoder(json.JSONEncoder):
    def default(self, o: list):
        try:
            assert isinstance(o[1], message.Message)
            return json.dumps([o[0], o[1].__dict__])
        except AssertionError:
            pass

        return super().default(o)


def serialize(obj: list, type="pickle") -> bytes:
    if type == "pickle":
        return pickle.dumps(obj)
    elif type == "json":
        return MessageJSONEncoder().default(obj).encode("utf-8")
    else:
        raise TypeError


# ahuet ono rabotaet
def as_message(obj: list):
    msg = msg_table[obj[0]]()
    for k, v in obj[1].items():
        setattr(msg, k, v)

    return [obj[0], msg]


def deserialize(data: bytes, type="pickle"):
    if type == "pickle":
        return pickle.loads(data)
    elif type == "json":
        return as_message(json.loads(data.decode("utf-8")))
    else:
        raise TypeError


# Network communication class
class Net:
    # Initialize network communication
    def __init__(
        self,
        timer=-1.0,
        timer_delay=0.5,
        get_port=31000,
        set_ports=None,
        set_ip="255.255.255.255",
        serialization_type="pickle",
    ):
        self.timer = timer

        if set_ports is None:
            set_ports = [31000]

        self.set_ip = set_ip
        self.set_ports = set_ports

        self.last_OSError = time.time()
        self.next = time.time() + self.timer + timer_delay

        self.sock_set = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        self.sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        self.sock_get = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        self.sock_get.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock_get.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock_get.bind(("", get_port))

        self.data = ["Unknown", None]

        self.serialization_type = serialization_type

    # Identification name of the received message (ClassName)
    @property
    def id(self):
        return copy.deepcopy(self.data[0])

    # Received from network message
    @property
    def msg(self):
        return copy.deepcopy(self.data[1])

    # Send message to network
    def send(self, set_msg):
        for port in self.set_ports:
            name = set_msg.id
            buf = serialize(obj=[name, set_msg], type=self.serialization_type)
            try:
                self.sock_set.sendto(buf, (self.set_ip, port))
            except OSError as err:
                if time.time() - self.last_OSError > DELAY_OSError:
                    self.last_OSError = time.time()
                    print("ERROR: OSError:", err)

    # Wait for receiving message or timer tick
    def receive(self) -> bool:
        if self.timer > 0:
            now = time.time()
            if now > self.next:
                self.next += self.timer
                self.data = ["Timer", None]
                return True
            self.sock_get.settimeout(self.next - now)
        try:
            buf, _ = self.sock_get.recvfrom(65535)
        except socket.timeout:
            if self.timer > 0:
                self.next += self.timer
                self.data = ["Timer", None]
            else:
                print("ERROR: UnknownTimeout")
                self.data = ["UnknownTimeout", None]
            return True
        except BlockingIOError as err:
            self.data = ["BlockingIOError", None]
            print("ERROR: BlockingIOError", err)
            return True
        else:
            self.data = deserialize(buf, self.serialization_type)
            return True


# Identification name of the received message (ClassName)
def wait_message(id=""):
    net = Net()  # Will wait for messages without timer.
    while net.receive():  # Wait all messages.
        if net.id == id:  # If id is necessary then
            return net.msg  # return message.
