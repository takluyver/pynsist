#!/usr/bin/env python

# This example was adapted from http://matplotlib.org/examples/user_interfaces/embedding_in_gtk.html, and http://pygtk.org/pygtk2tutorial/examples/helloworld.py

import pygtk
pygtk.require('2.0')
import gtk
from matplotlib.figure import Figure
from numpy import arange, sin, pi
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas

class HelloMatplotlib:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_size_request(400, 400)
        self.window.set_border_width(10)

        f = Figure(figsize=(5,4), dpi=100)
        a = f.add_subplot(111)
        t = arange(0.0,3.0,0.01)
        s = sin(2*pi*t)
        a.plot(t,s)

        self.canvas = FigureCanvas(f)
        self.canvas.show()
        self.window.add(self.canvas)
        self.window.show()

    def delete_event(self, widget, event, data=None):
        gtk.main_quit()

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def main(self):
        gtk.main()

def main():
    hello = HelloMatplotlib()
    hello.main()
