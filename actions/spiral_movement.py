import math

from base import network, mat, message

from base.time import time_precise


def spiral_movement(center, step, turn_n, spiral_speed, depth=0):
    time_start = time_precise()
    print('spiral started')

    def spiral(t):  # Archimedean spiral with dl/dt = const
        k = step / (2 * math.pi)
        phi = math.sqrt(2 / k * (t - time_start) * 1e-9 * spiral_speed)
        r = k * phi

        x = r * math.cos(phi) + center[0]
        y = r * math.sin(phi) + center[1]

        return x, y, phi // math.pi

    # Initial and current robot position
    auv_pos = network.wait_message('Coord').pos

    net = network.Net(timer=1)
    while net.receive():
        if net.id == 'Timer':
            *target_pos, turn = spiral(time_precise())

            if turn > turn_n:
                return

            yaw = mat.direction(auv_pos, target_pos)  # Calculate relative yaw to object position.

            net.send(message.Tack(
                time=1.5,
                speed_x=0.0, speed_y=mat.dist2d(auv_pos, target_pos) * 0.2,
                stab_depth=depth, stab_yaw=yaw, stab_pitch=0.0, stab_roll=0.0
            ))

            net.send(message.DetectedObject(
                x=target_pos[0],
                y=target_pos[1],
                depth=1,
                obj='Spiral'
            ))

        if net.id == 'Coord':
            auv_pos = net.msg.pos

