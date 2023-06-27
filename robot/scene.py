#!python3
# @todo: need filtration and avg!!!
import sys, setproctitle
sys.path.append('../base')
import mat, network, message
# from message import AXIS

TIMER = 0.25  # Filtered objects publication timer.

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net = network.Net(timer=TIMER)                 # Will send/receive some messages and wait timer ticks.
# pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]           # Input robot position.
out = message.FilteredObjects()                # Sended array with all filtered objects.
new = message.FilteredObjects()                # Sended array with all filtered objects.
old = message.FilteredObjects()                # Sended array with all filtered objects.
ini = message.FilteredObjects()                # Sended array with all filtered objects.

while net.receive():  # Wait for messages or timer

    if net.id == 'Timer':  # If timer has come then
        net.send(out)        # send output objects array.

    elif net.id == 'DetectedObject':  # If object has come
        data = net.msg()                # then read object position
        out.objs[data.obj] = data.pos   # and save to filtered output data.

    # if net.id() == 'Timer':  # If timer has come then
    #     for obj in out.param:
    #         if time.time() - obj.time > obj.old:
    #             obj.pos = DEEPCOPY ini[obj].pos
    #     net.send(out)

    # elif net.id == 'DetectedObject':  # If object has come
    #     msg = net.msg()                 # then read object position
    #     out.objs[msg.obj] = msg.pos     # and save to filtered output data.


    # if net.id() == 'Timer':  # If timer has come then

    #     for obj in range(out):
    #         if time.time() - new.param[obj].dt:
    #             out.param[obj] = !DEEPCOPY! ini.param[obj]
    #         else:

    #             dt = time.time() - new.param[obj].dt
    #             dr = mat.dr(new.param[obj].pos, new.param[obj].pos)
    #         for i in range(TRIM):
    #             if is_num(new.objs[o][a]) && is_num(old.objs[o][a]):
    #                 diff = math.abs(new.objs[o][a] - old.objs[o][a])
    #             && delay[o][a] < DT[o][a].delay && diff < DIFF[o][a]:
    #                 old.objs [now_obj][i] = new.objs[now_obj][i]
    #                 new.objs [now_obj][i] = now_pos[i]
    #                 timestamp[now_obj][i] = now_time

    #     net.send(out)        # send output objects array.

    # elif net.id() == 'DetectedObject':
    #     msg = net.msg()
    #     old = DEEPCOPY new
    #     new = {"time": time.time(), "obj": msg.obj, "pos": msg.pos}
    #     for i in range(DEPTH+1):
    #         new.pos[i] = msg.pos[i] if mat.is_num(msg.pos[i]) else ini.objs[msg.obj].pos[i]

    elif net.id() == 'ResetObjects':     # If ResetObjects message has come
        out = message.FilteredObjects()  # then save object to output array.
