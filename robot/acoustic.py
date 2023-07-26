#!python33
import json
import asyncio
import websockets
import numpy as np
import time, sys, setproctitle
from base import network, message, mat

# Constants.
PERIOD   = 1.0                       # Publication period.
OV_DSP_FREQ = 1.0/192.0e3  

LEFT_CHANNEL   = 1
FRONT_CHANNEL  = 3
RIGHT_CHANNEL  = 0
BACK_CHANNEL   = 2

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net = network.Net(timer=PERIOD)                # Network communication.

async def init_connection(url = 'ws://192.168.88.4:9002'):
    return await websockets.connect(url)


async def recv_message(acc_con):
    data = json.loads(await acc_con.recv())
    return data
    
loop = asyncio.get_event_loop()
acc_con = loop.run_until_complete(init_connection())

while net.receive():
    json_data = loop.run_until_complete(recv_message(acc_con))
    if json_data['type'] == 12:
        delays = json_data['data']['delay']
        freqs  = json_data['data']['frequency']

        freq = np.mean(freqs).item()
        min_delay  = np.min(delays).item()
        net.send(message.SoundDelay(freq  = freq,           # Send message with config frequecy and
                                left  = (delays[LEFT_CHANNEL] - 2000)*OV_DSP_FREQ*1500,   # left,
                                right = (delays[RIGHT_CHANNEL] - 2000)*OV_DSP_FREQ*1500,   # right,
                                back  = (delays[BACK_CHANNEL] - 2000)*OV_DSP_FREQ*1500,   # back and
                                front = (delays[FRONT_CHANNEL] - 2000)*OV_DSP_FREQ*1500,
                                freq_left = freqs[LEFT_CHANNEL],
                                freq_right = freqs[RIGHT_CHANNEL],
                                freq_back  = freqs[BACK_CHANNEL], 
                                freq_front = freqs[FRONT_CHANNEL]
                                ))  # front distance diffrences.


 
