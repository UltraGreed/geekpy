import math

from base.message import X, Y, DEPTH, YAW, PITCH, ROLL, AXIS


# Saturation function of some value
def sat(x, minimum, maximum):
    return max(minimum, min(maximum, x))


# Sin in degrees
def sind(x):
    return math.sin(x * math.pi / 180.0)


# Cos in degrees
def cosd(x):
    return math.cos(x * math.pi / 180.0)


# Rotate angle to +-180 deg range
def to180(x):
    angle = x
    while angle > 180.0: angle -= 360.0
    while angle < -180.0: angle += 360.0
    return angle


def to360(angle):
    while angle > 360.0:
        angle -= 360.0
    while angle < 0:
        angle += 360.0
    return angle


# Projection of xy-vector to x-axis after rotation
def proj_x(x, y, angle):
    return cosd(angle) * x + sind(angle) * y


# Projection of xy-vector to y-axis after rotation
def proj_y(x, y, angle):
    return cosd(angle) * y - sind(angle) * x


# Rotate dxy vector from map to robot coordinate system
def rotate2robot(map_dx, map_dy, robot_yaw):
    robot_dx = proj_x(map_dx, map_dy, -robot_yaw)
    robot_dy = proj_y(map_dx, map_dy, -robot_yaw)
    return robot_dx, robot_dy


# Rotate dxy vector from robot to map coordinate system
def rotate2map(robot_dx, robot_dy, robot_yaw):
    map_dx = proj_x(robot_dx, robot_dy, robot_yaw)
    map_dy = proj_y(robot_dx, robot_dy, robot_yaw)
    return map_dx, map_dy


# Convert dxy vector from robot to map coordinate system
def robot2map(robot, point):
    dx, dy = rotate2map(point[X], point[Y], robot[YAW])
    if len(robot) > 2 and len(point) > 2:
        return [robot[X] + dx, robot[Y] + dy, robot[DEPTH] + point[DEPTH]]
    return [robot[X] + dx, robot[Y] + dy]


# Distance between two points in XY dimensions
def dist2d(a, b):
    return math.sqrt((a[X] - b[X]) ** 2 + (a[Y] - b[Y]) ** 2)


# Distance between two points in XYZ dimensions
def dist3d(a, b):
    return math.sqrt((a[X] - b[X]) ** 2 + (a[Y] - b[Y]) ** 2 + (a[DEPTH] - b[DEPTH]) ** 2)


# Direction from point a to point b
def direction(a, b):
    return to180(math.degrees(math.atan2(b[X] - a[X], b[Y] - a[Y])))


def calc_lin_approx(data):
    """
    Returns coefficients for linear function with the lowest possible MSE
    :param data: tuple of two arrays: xs and ys
    :return: tuple of coefficients
    """
    sum_x = sum(data[0])
    sum_x2 = sum([x ** 2 for x in data[0]])
    sum_y = sum(data[1])
    sum_xy = sum([data[0][i] * data[1][i] for i in range(len(data[0]))])
    n = len(data[0])

    # Calculate coefficients
    a = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)

    b = (sum_y - a * sum_x) / n

    return a, b


def line_closest_point(coefs: tuple, point: tuple):
    """
    Returns point from line closest to the given point
    :param coefs: line coefs in either (Ax + By + C = 0) or (y = kx + b) format
    :param point: coordinates of point
    :return:
    """
    if len(coefs) == 2:
        k, b = coefs
        a, b, c = k, -1, b
    elif len(coefs) == 3:
        a, b, c = coefs
    else:
        raise ValueError("Wrong number of coefficients")

    x0, y0 = point

    x = (b * (b * x0 - a * y0) - a * c) / (a ** 2 + b ** 2)
    y = (a * (-b * x0 + a * y0) - b * c) / (a ** 2 + b ** 2)

    return x, y


