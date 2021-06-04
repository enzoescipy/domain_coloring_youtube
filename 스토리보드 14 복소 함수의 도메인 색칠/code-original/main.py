import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import sys
import pygame as pygame

d_glob = 0.0
function_limit = 10 # this limit is abs() value of complex number.
quality = 30
colorline_size = 30 # colorline_size ** 2 is total data length.
display_size = (1024, 640)
display_rect_start = (262,70) # think midpoint for 512, 320 and length for 500.
display_rect_size = 2

z = sp.symbols("z")
a = sp.symbols("a",real=True, imaginary=False) # use for real domain
b = sp.symbols("b",real=True, imaginary=False) # use for imaginary domain
my_sigmoid = (1 / (1 + (np.e) ** (-30 * (z - 0.5))))
def dist(tup):
    return (tup[0])**2 + (tup[1])**2
def angle(tup):

    tanAngle = None
    if tup[0] == 0.0:
        tanAngle = np.pi / 2
    else:
        tanAngle = np.arctan(float(tup[1] / tup[0]))
    if tanAngle > 0:
        if tup[0] >= 0:
            return tanAngle
        else:
            return  tanAngle + np.pi
    elif tanAngle < 0:
        if tup[1] < 0:
            return tanAngle + 2 * np.pi
        else:
            return  tanAngle + np.pi
    else:
        return 0.0
def polarize(tup):
    return dist(tup),angle(tup) #(r,theta)
def tup_to_color(tup): #d is half-interval length. ex) [-1,1] interval's d is 1.
    print(d_glob)
    #red     255 0   0   => 0   degree
    #yellow  255 255 0   => 60  degree
    #green   0   255 0   => 120 degree
    #cyan    0   255 255 => 180 degree
    #blue    0   0   255 => 240 degree
    #magenta 255 0   255 => 300 degree
    #each color's angluar dist is 60 degree.
    dist_fraction = 0.0
    if tup[0] <= d_glob:
        dist_fraction = tup[0] / d_glob
    else:
        dist_fraction = 1.0

    angle = tup[1] / np.pi * 180

    color = [0,0,0]
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

    return tuple(map(lambda x:round(dist_fraction * x),color))

funcpair = []
funcInput = np.array([])
funcOutput = []

print("all basic math function should be wrote like cos(x) * x + x**2 ")
#func_str_input = input("please write your function with z.  :")
#func_str_input = "x**-2 * sin(1/x*10)"
func_str_input = "z**2"

func_syp = sp.sympify(func_str_input)
func_syp = func_syp.subs(z, (a+b*sp.I))
func_syp = sp.expand(func_syp)
func_real, func_imag = func_syp.as_real_imag()
#(a**2 - b**2, 2*a*b) for (real, imag)



# make DATA list.
def datagenerate(div):
    global funcInput
    global funcOutput
    global funcpair
    funcInput = []
    for avalue in np.linspace(-1, 1, div):
        for bvalue in np.linspace(-1, 1, div):
            funcInput.append((avalue, bvalue))
    funcpair = []
    funcOutput = []
    for i in range(len(funcInput)):
        xvalue_tup = funcInput[i]
        yvalue_tup = ( func_real.subs([ (a,xvalue_tup[0]), (b,xvalue_tup[1]) ]) ,
                       func_imag.subs([ (a,xvalue_tup[0]), (b,xvalue_tup[1]) ]))
        yvalue_tup = polarize(yvalue_tup)
        if yvalue_tup[0] < function_limit:
            funcpair.append((xvalue_tup, yvalue_tup))
        else:
            funcpair.append((xvalue_tup, (np.inf , yvalue_tup[1])))
    funcInput = list(map(lambda tup: tup[0], funcpair))
    funcOutput = list(map(lambda tup: tup[1], funcpair))






"""
datagenerate(quality)
# Draw simple graph.
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(funcInput, funcOutput)
ax.spines['left'].set_position('zero')
ax.spines['right'].set_color('none')
ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
plt.show()
#plt.savefig('output.png')

"""



# re-generate data and Draw domain coloring
datagenerate(colorline_size)
print("data generating completed.")

#print(funcOutput)
funcOutput_colorized = list(map(tup_to_color,list(funcOutput)))
print("domain colorizing completed.")
#print(funcOutput_colorized)


funcOutput_dist_exceptInf = []
for tup in funcOutput:
    if str(tup[0]) == str(np.inf):
        continue
    funcOutput_dist_exceptInf.append(tup[0])
d_glob = abs(max(funcOutput_dist_exceptInf))
print(d_glob)

pygame.init()

screen = pygame.display.set_mode(display_size)
run = True
animated = False

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    screen.fill((255,255,255))

    #draw gradation!!
    if animated == False:
        for i in range(colorline_size**2):
            tup = funcOutput_colorized[i]
            posx = display_rect_start[0] + (i % colorline_size) * display_rect_size
            posy = display_rect_start[1] + (int(i / colorline_size)) * display_rect_size

            pygame.draw.rect(screen,
                             tup,
                             [posx, posy, display_rect_size, display_rect_size],
                             )
            pygame.time.delay(1)
            pygame.display.flip()

        animated = True






pygame.quit()

sys.exit()