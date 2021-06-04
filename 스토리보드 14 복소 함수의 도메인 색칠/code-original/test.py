import numpy as np
import sympy as sp
x = sp.symbols("x")
my_sigmoid = (1 / (1 + (np.e)**(-5*(x-0.5))))

for i in range(0,361,10):
    angle = i
    color = [0, 0, 0]
    if 0 <= angle <= 60:
        color[1] = 255 * (angle / 60)
        color[0] = 255
    elif 60 < angle <= 120:
        angle -= 60
        angle = 60 - angle
        color[0] = 255 * (angle / 60)
        color[1] = 255
    elif 120 < angle <= 180:
        angle -= 120
        color[2] = 255 * (angle / 60)
        color[1] = 255
    elif 180 < angle <= 240:
        angle -= 180
        angle = 60 - angle
        color[1] = 255 * (angle / 60)
        color[2] = 255
    elif 240 < angle <= 300:
        angle -= 240
        color[0] = 255 * (angle / 60)
        color[2] = 255
    elif 300 < angle <= 360:
        angle -= 300
        angle = 60 - angle
        color[2] = 255 * (angle / 60)
        color[0] = 255

    #print(color)

    #red     255 0   0   => 0   degree
    #yellow  255 255 0   => 60  degree
    #green   0   255 0   => 120 degree
    #cyan    0   255 255 => 180 degree
    #blue    0   0   255 => 240 degree
    #magenta 255 0   255 => 300 degree

a = 30.0
print(a.arctan(1.93220338983051 / 0.0666475150818731))