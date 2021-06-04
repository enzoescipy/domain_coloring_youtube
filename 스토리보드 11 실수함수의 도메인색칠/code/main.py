import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import sys
import pygame as pygame
function_limit = (-10.0,10.0)
quality = 1000
colorline_size = 600
x = sp.symbols("x")
my_sigmoid = (1 / (1 + (np.e)**(-30*(x-0.5))))
funcpair = []
funcInput = np.array([])
funcOutput = []

print("all basic math function should be wrote like np.")
func_str_input = input("please write your function with x.  :")
#func_str_input = "x**-2 * sin(1/x*10)"

func_syp = sp.sympify(func_str_input)

# make DATA list.
def datagenerate(div):
    global funcInput
    global funcOutput
    global funcpair
    funcpair = []
    funcInput = np.linspace(-1, 1, div)
    funcOutput = []
    for i in range(div):
        xvalue = funcInput[i]
        yvalue = float(func_syp.subs(x, xvalue))
        if function_limit[0] < yvalue < function_limit[1]:
            funcpair.append((xvalue, yvalue))
        else:
            if yvalue <= function_limit[0]:
                funcpair.append((xvalue, -np.inf))
            elif function_limit[1] <= yvalue:
                funcpair.append((xvalue, np.inf))

    funcInput = list(map(lambda tup: tup[0], funcpair))
    funcOutput = list(map(lambda tup: tup[1], funcpair))

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





# re-generate data and Draw domain coloring
datagenerate(colorline_size)

d_glob = 0
funcOutput_exceptInf = []
for val in funcOutput:
    if str(val) == str(np.inf) or str(val) == str(-np.inf):
        continue
    funcOutput_exceptInf.append(val)
minimum = min(funcOutput_exceptInf)
maximum = max(funcOutput_exceptInf)
if minimum * maximum < 0:
    if abs(maximum) > abs(minimum):
        d_glob = abs(maximum)
    else:
        d_glob = abs(minimum)
else:
    if minimum < 0:
        d_glob = abs(minimum)
    else:
        d_glob = abs(maximum)
print(minimum, maximum, d_glob)
def float_to_color(floatvalue): #d is half-interval length. ex) [-1,1] interval's d is 1.
    if str(floatvalue) == str(np.inf):
        return 255,0,0
    elif str(floatvalue) == str(-np.inf):
        return 0,0,255

    fraction = (floatvalue + d_glob) / d_glob / 2
    print(fraction)
    fraction = float(my_sigmoid.subs(x,fraction))
    print(fraction)
    stretched_length = fraction * 510
    if stretched_length < 255:
        return 0,0,round(255 - stretched_length)
    else:
        return round(stretched_length - 255), 0, 0
print(funcOutput)
funcOutput_colorized = list(map(float_to_color,list(funcOutput)))
print(funcOutput_colorized)

pygame.init()
screen = pygame.display.set_mode((1024, 640))
run = True
animated = False
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    screen.fill((255,255,255))

    #draw gradation!!
    if animated == False:
        for i in range(len(funcOutput_colorized)):
            pygame.draw.line(screen,
                             funcOutput_colorized[i],
                             [150 + i, 300],
                             [150 + i, 330])
            pygame.display.flip()
            pygame.time.wait(5)
        animated = True




pygame.quit()
sys.exit()