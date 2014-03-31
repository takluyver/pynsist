from tkinter import *
import foopkg

root = Tk()
root.title("Python Example App")
t = Text(root)
t.insert(END, "Type stuff here.")
t.insert(END, foopkg.strvar)
t.pack()

w = Label(root, text="Hello, world!")
w.pack()

root.mainloop()
