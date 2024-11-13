from tkinter import *
from math import sin, cos, radians
size = 600
root = Tk()
canvas = Canvas(root, width=size, height=size)
canvas.pack()
canvas.create_oval(100,100,500,500)
dot = canvas.create_oval(1,1,1,1,outline="red", fill='red')

speed = int(input("Введите скорость движения точки:"))
direction = int(input("Введите направление движения точик: 0-по часовой; 1-против:"))

def move_dot(ang):
    ang %= 360
    x = 200*cos(radians(ang))
    y = 200*sin(radians(ang))
    ang += 1 * (-1)**direction
    canvas.coords(dot,300+x-2,300+y-2,300+x+2,300+y+2)
    root.after(speed,move_dot,ang)
    
root.after(speed,move_dot,0)
root.mainloop()
