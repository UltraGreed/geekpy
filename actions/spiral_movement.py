import math

from base import network, mat, message


def spiral_movement(center, r_min, r_max, step, d_min, d_max, turn_max_speed, min_speed, max_speed, depth=0):
    """
    :param center:
    :param r_min:
    :param r_max:
    :param step: distance from each turn of spiral
    :param d_min:
    :param d_max: max distance from auv to given radius when auv would go straight course
    :param turn_max_speed: turn on which spiral speed would be max
    :param min_speed:
    :param max_speed:
    :param depth:
    :return:
    """
    def spiral(phi_deg):  # Get x, y from current bearing
        phi = phi_deg * math.pi / 180
        k = step / (2 * math.pi)
        r = k * abs(phi)

        # r = min(r, r_max)
        r = max(r, r_min)

        x = r * math.cos(phi + bearing_start) + center[0]
        y = -r * math.sin(phi + bearing_start) + center[1]

        return x, y, r

    # Initial robot position
    auv_pos = network.wait_message('Coord').pos

    bearing = mat.to360(mat.direction(auv_pos, center))
    bearing_start = bearing / 180 * math.pi
    bearing_cum = 0  # Accumulator of bearing

    net = network.Net(timer=0.5)
    while net.receive():
        if net.id == 'Timer':
            prev_bearing = bearing
            bearing = mat.to360(mat.direction(auv_pos, center))

            # TODO: fix this shit
            # Accumulate bearing with possibility of auv passing through zero-angle
            if abs(bearing - prev_bearing) < abs(360 + bearing - prev_bearing):
                bearing_cum += bearing - prev_bearing
            else:
                bearing_cum += 360 + bearing - prev_bearing

            *target_pos, radius = spiral(bearing_cum)

            distance = mat.dist2d(auv_pos, center)

            if distance > r_max:
                return

            phi_coef = min(abs(bearing_cum) / (turn_max_speed * 360), 1)

            # TODO: continue increasing of D coef after capped velocity
            # TODO: (in other words separate D and V cap values)
            # Calculate such yaw, which would smoothly lead set auv on spiral
            if distance < radius:
                yaw_offset = 90 * (2 - distance / radius)
            else:
                yaw_offset = max(90 * (1 - (distance - radius) / (d_min + (d_max - d_min) * phi_coef)), 0)

            # AUV should go either clock-wise or counter clock-wise
            yaw = mat.direction(auv_pos, center) + yaw_offset * (-1 if bearing_cum > 0 else 1)

            print(bearing_cum, phi_coef, (d_min + (d_max - d_min) * phi_coef))

            net.send(message.Tack(
                time=1.5,
                speed_x=0.0, speed_y=min_speed + (max_speed - min_speed) * phi_coef,
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
