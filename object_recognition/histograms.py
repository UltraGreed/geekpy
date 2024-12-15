import sys
import time

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

from object_recognition.config import MODEL_SHAPE, MODEL_MAX_VALUE
from object_recognition.model_class import get_model_path


obj_name = sys.argv[1]
mpl.rcParams['figure.dpi'] = 300


def get_histogram_bw(axis, data):
    """Return image representing bw histogram of either object or background in [0..1]."""
    axis_ind = 'HSV'.index(axis)

    image_r, image_g, image_b = (
        np.max(data, axis=axis_ind).astype(np.float64) / MODEL_MAX_VALUE for _ in range(3)
    )

    return np.stack((image_r, image_g, image_b), axis=-1)


def get_histogram_color(axis):
    """Return image representing separated histogram of object and background in [0..1]."""
    axis_ind = 'HSV'.index(axis)

    image_r = np.max(data_obj_norm, axis=axis_ind).astype(np.float64) / MODEL_MAX_VALUE
    image_b = np.max(data_bg_norm, axis=axis_ind).astype(np.float64) / MODEL_MAX_VALUE
    image_g = np.zeros(MODEL_SHAPE[:axis_ind] + MODEL_SHAPE[axis_ind + 1 :])

    return np.stack((image_r, image_g, image_b), axis=-1)


def plot_histogram_3d(ax, axis, image):
    """Plot provided histogram image perpendicular to axis of choice on mtl.Axes."""
    if axis == 'H':
        xs, ys = np.meshgrid(np.arange(MODEL_SHAPE[1]), np.arange(MODEL_SHAPE[2]))
        zs = np.full_like(xs, MODEL_SHAPE[0] - 1)
    elif axis == 'S':
        xs, zs = np.meshgrid(np.arange(MODEL_SHAPE[2]), np.arange(MODEL_SHAPE[0]))
        ys = np.zeros_like(xs)
    else:
        ys, zs = np.meshgrid(np.arange(MODEL_SHAPE[1]), np.arange(MODEL_SHAPE[0]))
        xs = np.full_like(ys, MODEL_SHAPE[2] - 1)

    ax.plot_surface(
        xs,
        ys,
        zs,
        rstride=1,
        cstride=1,
        facecolors=image
    )


fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.set(xlabel='Яркость', ylabel='Насыщение', zlabel='Тон')

data_obj_norm = np.load(get_model_path(obj_name, 'obj_norm')).reshape(MODEL_SHAPE)
data_bg_norm = np.load(get_model_path(obj_name, 'noobj_norm')).reshape(MODEL_SHAPE)

print(f'Histogram construction started for {obj_name}.')
time1 = time.time()

for axis in 'HSV':
    hist = get_histogram_bw(axis, data_obj_norm)
    plot_histogram_3d(ax, axis, hist)
plt.savefig('histogram_bw_obj.png')
print('Object BW histogram done.')

for axis in 'HSV':
    hist = get_histogram_bw(axis, data_bg_norm)
    plot_histogram_3d(ax, axis, hist)
plt.savefig('histogram_bw_bg.png')
print('Background BW histogram done.')

for axis in 'HSV':
    hist = get_histogram_color(axis)
    plot_histogram_3d(ax, axis, hist)
plt.savefig('histogram_color.png')
print('Colored histogram done.')

print(f'All histograms for {obj_name} done in {time.time() - time1}.')

