from base import network
from base.message import X, Y, DEPTH, YAW, PITCH, ROLL

import tkinter
from tkinter import ttk

import time

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import json


def update_plot(*_):
    plt.cla()
    for entry in [plot_data[listbox_list[selected_i]] for selected_i in listbox.curselection()]:
        color = entry.color
        entry_data = entry.data[-1000:]
        ax_plot.plot(*reversed(list(zip(*entry_data))), color=color)

    canvas_plot.draw()


class ListboxEntry:
    data: list[tuple[float, float]]

    def __init__(self, color):
        self.color = color
        self.data = []

    def add(self, entry):
        self.data.append(entry)


def handle_new_entry(class_name, field_name, field_value):
    if not plot_data.get(class_name):
        plot_data[class_name] = ListboxEntry(color=cmap(0))
        listbox_list.append(class_name)

    if not plot_data.get(field_name):
        plot_data[field_name] = ListboxEntry(color=cmap(len(listbox_list) % N_PLT_COLORS))
        listbox_list.append(field_name)  # todo: this causes infinite memory losses

    plot_data[field_name].add((field_value, time.time() - start_time))


def change_pause():
    global is_paused
    is_paused = not is_paused


N_PLT_COLORS = 5

start_time = time.time()

root = tkinter.Tk()
root.title('Debugger')  # заголовок
root.geometry('1265x740')

listbox_list: list[ListboxEntry] = list()
# noinspection PyTypeChecker
listbox_var = tkinter.StringVar(value=listbox_list)

btn_frame = ttk.Frame(master=root)
btn_frame.grid(row=0, column=0, sticky='ns')

listbox = tkinter.Listbox(master=btn_frame, listvariable=listbox_var, selectmode='multiple')
listbox.pack(expand=True, fill='y')

plot_button = ttk.Button(master=btn_frame, command=change_pause, width=10, text="Pause")
plot_button.pack()

cmap = plt.cm.get_cmap('hsv', N_PLT_COLORS)

fig_cmap = plt.figure()
fig_cmap.set_size_inches(1, 7)
ax_cmap = fig_cmap.add_subplot()

n_rect = 43
ax_cmap.set_xlim([-0.5, 0.5])
ax_cmap.set_ylim([0, n_rect])
for i in range(n_rect):
    rect = plt.Rectangle((-0.5, n_rect - i - 1), 1, 1, facecolor=cmap(i % N_PLT_COLORS))
    ax_cmap.add_artist(rect)

ax_cmap.set_position((0, 0, 0.1, 1))

canvas_cmap = FigureCanvasTkAgg(fig_cmap, master=root)
canvas_cmap.get_tk_widget().grid(row=0, column=1, sticky='n', pady=1)

fig_plot = plt.figure()
fig_plot.set_size_inches(10, 7)
ax_plot = fig_plot.add_subplot()

toolbar_frame = ttk.Frame(master=root)
toolbar_frame.grid(row=0, column=2)
canvas_plot = FigureCanvasTkAgg(fig_plot, master=toolbar_frame)
canvas_plot.get_tk_widget().pack()

toolbar = NavigationToolbar2Tk(canvas_plot, toolbar_frame)

plt.tight_layout()

plot_data = {}
net = network.Net(timer=0.2)
is_paused = False
while net.receive():
    if net.id == 'Timer':
        # noinspection PyTypeChecker
        listbox_var.set(listbox_list)

        if not is_paused:
            update_plot()

        root.update()
        root.update_idletasks()
    else:
        for key, value in json.loads(str(net.msg)).items():
            if value is None:
                continue
            try:
                for i, field_value in enumerate(value):
                    if field_value is None:
                        continue

                    field_type = {X: 'x', Y: 'y', DEPTH: 'depth', YAW: 'yaw', PITCH: 'pitch', ROLL: 'roll'}[i]
                    field_name = f'    {key}.{field_type}'

                    handle_new_entry(net.id, field_name, field_value)
            except TypeError:
                field_value = value

                field_name = f'    {key}'

                handle_new_entry(net.id, field_name, field_value)
