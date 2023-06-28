import socket, select, pickle, time, math, struct, copy

DELAY_OSError = 5.0

# Network communucation class
class Net:

    # Initialize network communication
    def __init__(self, timer=-1, timer_delay=0.5, get_port=31000, set_ports=[31000], set_ip="255.255.255.255"):
        self.timer     = timer
        self.set_ip    = set_ip
        self.set_ports = set_ports
        self.last_OSError = time.time()
        self.next      = time.time() + self.timer + timer_delay
        self.sock_set  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock_get  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock_get.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock_get.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock_get.bind(('', get_port))
        self.data = ["Unknown", None]
        
    # Identification name of the received message (ClassName)
    def id(self):
        return copy.deepcopy(self.data[0])
        
    # Received from network message
    def msg(self):
        return copy.deepcopy(self.data[1])
        
    # Send message to network
    def send(self, set_msg):
        for port in self.set_ports:
            name = set_msg.id()
            buf = pickle.dumps([name, set_msg])
        try:
            self.sock_set.sendto(buf, (self.set_ip, port))
        except OSError as err:
            if (time.time() - self.last_OSError > DELAY_OSError):
                self.last_OSError = time.time()
                print("ERROR: OSError:", err)

    # # [RECVFROM SOLUTION] Wait for receiving message or timer tick
    # def receive(self):
    #     if self.timer > 0:
    #         now = time.time()
    #         if now > self.next:
    #             self.next = self.next + self.timer          
    #         self.sock_get.settimeout(max(0.0, self.next - now))
    #     try:
    #         buf, addr = self.sock_get.recvfrom(65535)
    #     except socket.timeout:
    #         self.data[1] = None
    #         if self.timer > 0:
    #             self.data[0] = 'Timer'
    #         else:
    #             self.data[0] = 'UnknownTimeout'
    #             print("WARNING: UnknownTimeout!")
    #         return True
    #     except BlockingIOError as err:
    #         self.data[1] = None
    #         self.data[0] = BlockingIOError
    #         print("ERROR: BlockingIOError", err)
    #         return True
    #     else:
    #         self.data = pickle.loads(buf)
    #         return True

    # # Wait for receiving message or timer tick
    # def receive(self):
    #     if self.timer > 0:
    #         now = time.time()
    #         if now > self.next:
    #             self.next = self.next + self.timer
    #         timeout = self.next - now
    #         if timeout > 0.0:
    #             self.sock_get.settimeout(timeout)
    #         else:
    #             self.data[1] = None
    #             self.data[0] = 'Timer'
    #             return True
    #     try:
    #         buf, addr = self.sock_get.recvfrom(65535)
    #     except socket.timeout:
    #         self.data[1] = None
    #         if self.timer > 0:
    #             self.data[0] = 'Timer'
    #         else:
    #             self.data[0] = 'UnknownTimeout'
    #             print("WARNING: UnknownTimeout!")
    #         return True
    #     except BlockingIOError as err:
    #         self.data[1] = None
    #         self.data[0] = BlockingIOError
    #         print("ERROR: BlockingIOError", err)
    #         return True
    #     else:
    #         self.data = pickle.loads(buf)
    #         return True

    # # [SELECT SOLUTION] Wait for receiving message or timer tick
    # def receive(self):
    #     if self.timer > 0:
    #         now = time.time()
    #         if now > self.next:
    #             self.next = self.next + self.timer
    #         timeout = max(0.0, self.next - now)
    #         (socks, _, excp) = select.select([self.sock_get], [], [], timeout)
    #     else:
    #         (socks, _, excp) = select.select([self.sock_get], [], [])
    #     for e in excp:
    #         print(e)
    #         data = ["Exception", e]
    #     if not(socks):
    #         self.data[1] = None
    #         if self.timer > 0:
    #             self.data[0] = 'Timer'
    #         else:
    #             self.data[0] = 'UnknownTimeout'
    #             print("WARNING: UnknownTimeout!")
    #     else:
    #         buf, addr = socks[0].recvfrom(65535)
    #         self.data = pickle.loads(buf)
    #     return True

    # # Wait for receiving message or timer tick
    # def receive(self):
    #     now = time.time()
    #     if self.timer > 0:
    #         if self.next <= now:
    #             self.next += self.timer
    #             self.data = ['Timer', None]
    #             # self.data[0] = None
    #             # self.data[1] = 'Timer'
    #             return True
    #         (socks, _, excepts) = select.select([self.sock_get], [], [], self.next - now)
    #     else:
    #         (socks, _, excepts) = select.select([self.sock_get], [], [])
    #     for e in excepts:
    #         print(e)
    #         data = ["Exception", e]
    #     if not(socks):
    #         self.data = ['Timer', None]
    #     else:
    #         buf, addr = socks[0].recvfrom(65535)
    #         self.data = pickle.loads(buf)
    #     return True    

    # # Wait for receiving message or timer tick
    # def receive(self):
    #     now = time.time()
    #     if self.timer > 0:
    #         if self.next <= now:
    #             self.next += self.timer
    #             self.data = ['Timer', None]
    #             # self.data[0] = None
    #             # self.data[1] = 'Timer'
    #             return True
    #         (socks, _, excepts) = select.select([self.sock_get], [], [], self.next - now)
    #     else:
    #         (socks, _, excepts) = select.select([self.sock_get], [], [])
    #     for e in excepts:
    #         print(e)
    #         data = ["Exception", e]
    #     if not(socks):
    #         self.data = ['Timer', None]
    #     else:
    #         buf, addr = socks[0].recvfrom(65535)
    #         self.data = pickle.loads(buf)
    #     return True

    # # !!! TIMER BAG FIXED !!! [RECVFROM SOLUTION] Wait for receiving message or timer tick
    # def receive(self):
    #     if self.timer > 0:
    #         now = time.time()
    #         if now > self.next:
    #             self.next += self.timer
    #             self.data = ['Timer', None]
    #             return True
    #         self.sock_get.settimeout(self.next - now)
    #     try:
    #         buf, addr = self.sock_get.recvfrom(65535)
    #     except socket.timeout:
    #         self.data[1] = None
    #         if self.timer > 0:
    #             self.data[0] = 'Timer'
    #             self.next += self.timer
    #         else:
    #             self.data[0] = 'UnknownTimeout'
    #             print("WARNING: UnknownTimeout!")
    #         return True
    #     except BlockingIOError as err:
    #         self.data[1] = None
    #         self.data[0] = BlockingIOError
    #         print("ERROR: BlockingIOError", err)
    #         return True
    #     else:
    #         self.data = pickle.loads(buf)
    #         return True

    # Wait for receiving message or timer tick
    def receive(self):
        if self.timer > 0:
            now = time.time()
            if now > self.next:
                self.next += self.timer
                self.data = ['Timer', None]
                return True
            self.sock_get.settimeout(self.next - now)
        try:
            buf, addr = self.sock_get.recvfrom(65535)
        except socket.timeout:
            if self.timer > 0:
                self.next += self.timer
                self.data = ['Timer', None]
            else:
                print("ERROR: UnknownTimeout")
                self.data = ['UnknownTimeout', None]
            return True
        except BlockingIOError as err:
            self.data = ['BlockingIOError', None]
            print("ERROR: BlockingIOError", err)
            return True
        else:
            self.data = pickle.loads(buf)
            return True


# Identification name of the received message (ClassName)
def wait_message(id=''):
    net = Net()               # Will wait for messages without timer.
    while net.receive():      # Wait all messages.
        if net.id() == id:    # If id is necessary then
            return net.msg()  # return message.
