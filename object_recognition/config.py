# COLORSCHEME PARAMETERS #
# Color scheme for model
COLOR_SCHEME = 'HSV'
# LOADING PARAMETERS #
MODEL_DIRECTORY = 'models/'
# OBJECT RECOGNITION PARAMETERS #
# Part of maximum image weight sum needed to recognize object
THRESHOLD_OBJECT = 0.001
# Part of maximum image weight sum to remove from image
THRESHOLD_CLEAN = 0.0005
# MODEL-WIDE PARAMETERS #
# Integer size of one model element
# Value higher than 32 does not work correctly
MODEL_PRECISION = 32
MODEL_MAX_VALUE = 2**MODEL_PRECISION - 1
MODEL_DTYPE = f'uint{MODEL_PRECISION}'
MODEL_NEXT_DTYPE = 'uint32' if MODEL_PRECISION < 32 else 'uint64'
MODEL_NEXT_SIGNED_DTYPE = MODEL_NEXT_DTYPE[1:]
# Model shall be divided by this value to fit into [0, 255] to get debug image
MODEL_IMAGE_CAST = 2 ** (MODEL_PRECISION - 8)
# Dimensions of RGB color space
RGB_AMOUNT = 32
RGB_COMPRESSION = 256 // RGB_AMOUNT
# Dimensions of HSV color space
H_AMOUNT = 60
S_AMOUNT = 16
V_AMOUNT = 16
H_COMPRESSION = 180 // H_AMOUNT
S_COMPRESSION = 256 // S_AMOUNT
V_COMPRESSION = 256 // V_AMOUNT

MODEL_SHAPE = (
    (RGB_AMOUNT, RGB_AMOUNT, RGB_AMOUNT)
    if COLOR_SCHEME == 'RGB'
    else (H_AMOUNT, S_AMOUNT, V_AMOUNT)
)
# TRAINING PARAMETERS #
# Dtype of accumulators
TRAIN_DTYPE = 'uint64'
# Area in which pixels incremented during training
PIXEL_AREA = 2
# NORMALIZATION PARAMETERS #
# Thresholds for model normalization
UPPER_BORDER_OBJECT = 0.5
UPPER_BORDER_NON_OBJECT = 0.2
# Model value which will equal to zero chance
# Ranges from -1 to 1
LOWER_MODEL_BORDER = 0.1
# INFERENCE PARAMETERS
PIXEL_SIZE_COEFFICIENT = 1.3
####################
