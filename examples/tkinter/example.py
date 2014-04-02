from tkinter import *

root = Tk()
root.title("Python Example App")
t = Text(root)
t.insert(END, "Type stuff here.")
t.pack()

w = Label(root, text="Hello, world!")
w.pack()

root.mainloop()
