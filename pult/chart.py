#!python3
import setproctitle
import time
import sys
import json

from base import network, mat
from base.message import X, Y, DEPTH, YAW, PITCH, ROLL

import tkinter as tk
from tkinter import ttk

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def update_plot(*_):
    plt.cla()
    for entry in [plot_data[listbox_list[selected_i]] for selected_i in listbox.curselection()]:
        entry_data = entry[-1000:]
        ax_plot.plot(*reversed(list(zip(*entry_data))))

    canvas_plot.draw()


def clear_pause():
    for entry in [plot_data[listbox_list[selected_i]] for selected_i in listbox.curselection()]:
        entry.clear()


def change_pause():
    global is_paused
    is_paused = not is_paused


setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

N_PLT_COLORS = 8

start_time = time.time()

root = tk.Tk()
root.title('Chart')
root.geometry('1265x740')

listbox_shown: list[str] = list()
listbox_var = tk.StringVar(value=listbox_shown)  # type: ignore
listbox_list = list()

btn_frame = ttk.Frame(master=root)
btn_frame.grid(row=0, column=0, sticky='ns')

listbox = tk.Listbox(master=btn_frame, listvariable=listbox_var, selectmode='multiple')
listbox.pack(expand=True, fill='y')

clear_button = ttk.Button(master=btn_frame, command=clear_pause, width=10, text='Clear')
clear_button.pack()
pause_button = ttk.Button(master=btn_frame, command=change_pause, width=10, text='Pause')
pause_button.pack()

fig_plot = plt.figure()
fig_plot.set_size_inches(10, 7)
ax_plot = fig_plot.add_subplot()
ax_plot.yaxis.set_label_position('right')
ax_plot.yaxis.tick_right()

toolbar_frame = ttk.Frame(master=root)
toolbar_frame.grid(row=0, column=2)
canvas_plot = FigureCanvasTkAgg(fig_plot, master=toolbar_frame)
canvas_plot.get_tk_widget().pack()

toolbar = NavigationToolbar2Tk(canvas_plot, toolbar_frame)

plt.tight_layout()

plot_data: dict[str, list[tuple[object, float]]] = {}
net = network.Net(timer=0.2)
is_paused = False
while net.receive():
    if net.id == 'Timer':
        listbox_var.set(listbox_shown)  # type: ignore

        if not is_paused:
            update_plot()

        root.update()
        root.update_idletasks()
    else:
        try:
            msg_dict = json.loads(str(net.msg))
        except json.JSONDecodeError:
            print(net.id, net.msg)
            continue

        for key, value in msg_dict.items():
            if value is None:
                continue
            try:
                enumerate(value)
            except TypeError:
                value = [value]  # noqa

            for i, field_value in enumerate(value):
                if net.id in ('Sensor', 'Tack', 'Coord', 'InitRobot'):
                    field_type = {
                        X: 'X',
                        Y: 'Y',
                        DEPTH: 'DEPTH',
                        YAW: 'YAW',
                        PITCH: 'PITCH',
                        ROLL: 'ROLL',
                    }[i]
                else:
                    field_type = str(i)
                field_id = f'{net.id}.{key}.{field_type}'

                # Add class name
                if net.id not in plot_data:
                    plot_data[net.id] = list()
                    listbox_list.append(net.id)
                    listbox_shown.append(net.id.upper())

                # Add field name
                if field_id not in plot_data:
                    plot_data[field_id] = list()

                    field_name_shown = f'{" " * 13}{field_id[field_id.find(".") + 1:]}'

                    listbox_list.append(field_id)
                    listbox_shown.append(field_name_shown)

                if (
                    type(field_value) is int
                    or type(field_value) is float
                    or type(field_value) is bool
                    or (type(field_value) is np.ndarray and field_value.shape == ())
                ):
                    field_name_shown = (
                        f'{field_value:.2f}'.rjust(9, ' ') + ' ' + field_id[field_id.find('.') + 1 :]
                    )
                    listbox_shown[listbox_list.index(field_id)] = field_name_shown

                    # HACK: plot_data never clears, so memory losses are to be expected
                    plot_data[field_id].append((field_value, time.time() - start_time))
