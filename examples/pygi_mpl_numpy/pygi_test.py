#!/usr/bin/python3

"""
This test program utilizes the Python bindings for GTK3 (PyGI or PyGObject).

The program conists of a window with a button that closes the window when
clicked. The window also shows a matplotlib plot. The plot is based on this
example: http://matplotlib.org/examples/pie_and_polar_charts/polar_bar_demo.html
"""

from gi.repository import Gtk
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.cm as cm
import numpy as np


class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="PyGI / PyGObject Example")
        self.connect("delete-event", Gtk.main_quit)
        self.set_default_size(400, 400)

        self.box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)

        self.fig = Figure(figsize=(10,10), dpi=80)
        self.ax = self.fig.add_subplot(111, polar=True)

        N = 20
        theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
        radii = 10 * np.random.rand(N)
        width = np.pi / 4 * np.random.rand(N)
        bars = self.ax.bar(theta, radii, width=width, bottom=0.0)
        for r, bar in zip(radii, bars):
            bar.set_facecolor(cm.jet(r / 10.))
            bar.set_alpha(0.5)

        self.canvas = FigureCanvas(self.fig)
        self.box.pack_start(self.canvas, True, True, 0)

        self.button = Gtk.Button(label="Exit")
        self.button.connect("clicked", self.on_exit_clicked)
        self.box.pack_start(self.button, False, False, 0)

    def on_exit_clicked(self, widget):
        Gtk.main_quit()

def main():
    win = MyWindow()
    win.show_all()
    Gtk.main()
