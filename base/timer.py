import time


class Timer:
    def __init__(self, delay_sec: float):
        self.delay_sec = delay_sec
        self.next = time.time() + delay_sec

    @property
    def is_unlock(self):
        unlock = self.next < time.time()
        if unlock:
            self.next = time.time() + self.delay_sec
        return unlock
