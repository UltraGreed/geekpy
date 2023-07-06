import math, sys

# Check if value is numerical
def is_num(x):
    return type(x) == int or type(x) == float

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
    while angle >  180.0: angle -= 360.0
    while angle < -180.0: angle += 360.0
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
    dx, dy = rotate2map(point[0], point[1], robot[2])
    return [robot[0] + dx, robot[1] + dy, robot[2] + point[2]]

# Distance between two points in XY dimensions
def dist2d(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

# Distance between two points in XYZ dimensions
def dist3d(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2)

# Direction from point a to point b
def direction(a, b):
    return to180(math.degrees(math.atan2(b[0] - a[0], b[1] - a[1])))

