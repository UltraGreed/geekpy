### movement
MAIN_TIMER = 1 / 12

    #######        X ##### Y # DEPTH ### YAW # PITCH ## ROLL
REGULATOR_P   = [  0.50,  1.00,  0.50,   2.00,   1.50,   1.00]  # Proportional coefficients of regulator.
REGULATOR_D   = [  0.00,  1.00,  0.50,   2.00,   1.50,   1.00]  # Differential coefficients of regulator.
REGULATOR_MAX = [  0.15,  0.15,  0.30,  45.00,  45.00,  45.00]  # Maximal possible velocity in stabilization mode.
REGULATOR_MIN = [ -0.15, -0.15, -0.30, -45.00, -45.00, -45.00]  # Minimal possible velocity in stabilization mode.

MIN_STAB_DIST = 0.001  # Min distance to make stabilization.


### cameras

BOTTOM_CAMERA_VFOV = 51.8
BOTTOM_CAMERA_HFOV = 72.4

FRONT_CAMERA_VFOV = 40.0
FRONT_CAMERA_HFOV = 61.4

