from multiprocessing import Process, Queue
import sympy as sp
import numpy as np

function_limit = 100  # this limit is abs() value of complex number.
quality = 100  # colorline_size ** 2 is total data length.
display_size = (1024, 640)
display_rect_start = (262, 70)  # think midpoint for 512, 320 and length for 500.
display_rect_size = 5
#quality * display_rect_size == size of graph(pixel)
thr_count = 9 #thread(process) count
qu_by_thr = 9 #queue divide per thread

z = sp.symbols("z")
a = sp.symbols("a", real=True, imaginary=False)  # use for real domain
b = sp.symbols("b", real=True, imaginary=False)  # use for imaginary domain
x = sp.symbols("x")
my_sigmoid = (1 / (1 + np.e ** (-30 * x)) - 0.5) * 2

def tuplist_parsing(string):
    temp = string.split("), (")
    final = []
    for line in temp:
        line = line.strip("[]()")
        tup = line.split(", ")
        tup = list(map(float,tup))
        final.append(tuple(tup))
    return final

def string_divider(string, div):
    length = len(string)
    interval = length // div
    final = []
    for i in range(div):
        if i != div-1:
            final.append(string[interval * i: interval * (i + 1)])
        else:
            final.append(string[interval * i: length])
    return tuple(final)

def dist(tup):
    return np.sqrt(float((tup[0])**2 + (tup[1])**2))
def angle(tup):

    tanAngle = None
    if tup[0] == 0.0:
        if tup[1] > 0:
            tanAngle = np.pi / 2
        elif tup[1] < 0:
            tanAngle = - np.pi / 2
        else:
            return np.nan

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
def tup_to_color(tup,maxDist): #d is half-interval length. ex) [-1,1] interval's d is 1.
    #red     255 0   0   => 0   degree
    #yellow  255 255 0   => 60  degree
    #green   0   255 0   => 120 degree
    #cyan    0   255 255 => 180 degree
    #blue    0   0   255 => 240 degree
    #magenta 255 0   255 => 300 degree
    #each color's angluar dist is 60 degree.
    dist_fraction = 0.0
    if tup[0] <= maxDist:
        dist_fraction = tup[0] / maxDist
    else:
        dist_fraction = 1.0
    dist_fraction = my_sigmoid.subs(x,dist_fraction)
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

# make DATA list.
## Input_generator making.
def funcInput_indexer(qua):
    alinspace = np.linspace(-1, 1, qua)
    blinspace = np.linspace(-1, 1, qua)
    def indexer(x,y):
        return alinspace[x],blinspace[y]
    return indexer
funcInput_glob = funcInput_indexer(quality)




##multiprocessing

START = 0
END = quality ** 2

def numeric_work(id, start, end, task_queues,func_real, func_imag):
    funcOutput_tmp = []
    funcOutput_dist_exceptInf_tmp = []

    def numeric_process(tup):
        xvalue_tup = tup
        yvalue_tup = (func_real.subs([(a, xvalue_tup[0]), (b, xvalue_tup[1])]),
                      func_imag.subs([(a, xvalue_tup[0]), (b, xvalue_tup[1])]))
        yvalue_tup = polarize(yvalue_tup)
        if yvalue_tup[0] >= function_limit:
            yvalue_tup = (np.inf, yvalue_tup[1])
        else:
            funcOutput_dist_exceptInf_tmp.append(yvalue_tup[0])

        funcOutput_tmp.append(yvalue_tup)


    for i in range(start, end):
        x = i % quality
        y = i // quality
        numeric_process(funcInput_glob(x, y))

    qu_count = len(task_queues)
    str_funcOutput = string_divider(str(funcOutput_tmp),qu_count)
    str_exceptInf = string_divider(str(funcOutput_dist_exceptInf_tmp),qu_count)
    for i in range(qu_count):
        task_queues[i].put((id, str_funcOutput[i], str_exceptInf[i]))
    print(id+1,"/", thr_count,"  numeric task")
    return


def coloring_work(id, start, end, maxDist,task_queues, funcOutput):
    funcOutput_colorized_tmp= []
    def coloring_process(tup, maxDist):
        yvalue_colorized = tup_to_color(tup, maxDist)
        funcOutput_colorized_tmp.append(yvalue_colorized)


    for i in range(start, end):
        coloring_process(funcOutput[i], maxDist)

    qu_count = len(task_queues)
    str_funcOutput_colorized = string_divider(str(funcOutput_colorized_tmp),qu_count)
    for i in range(qu_count):
        task_queues[i].put((id, str_funcOutput_colorized[i]))
    print(id+1,"/", thr_count,"  coloring task")
    return

if __name__ == '__main__':
    import sys
    import pygame as pygame
    import time

    timer = time.perf_counter()

    print("all basic math function should be wrote like cos(x) * x + x**2 ")
    func_str_input = input("please write your function with z.  :")
    #func_str_input = "x**-2 * sin(1/x*10)"
    #func_str_input = "z**2"

    func_syp = sp.sympify(func_str_input)
    func_syp = func_syp.subs(z, (a + b * sp.I))
    func_syp = sp.expand(func_syp)
    func_real, func_imag = func_syp.as_real_imag()
    # (a**2 - b**2, 2*a*b) for (real, imag)

    funcOutput_main = []
    funcOutput_colorized_main = []
    funcOutput_dist_exceptInf_main = []

    ##threading
    tmp_qu = []
    th = []
    qu = []

    interval = quality ** 2 // thr_count

    for i in range(thr_count):
        qu.append([])
        for j in range(qu_by_thr):
            qu[i].append(Queue())

    for i in range(thr_count):
        if i != thr_count - 1:
            th.append(Process(target=numeric_work,
                            args=(i, interval * i, interval * (i + 1), qu[i], func_real, func_imag)))
        else:
            th.append(Process(target=numeric_work,
                            args=(i, interval * i, END, qu[i], func_real, func_imag)))

    for i in range(thr_count):
        th[i].start()
    for i in range(thr_count):
        th[i].join()
    for i in range(thr_count):
        for j in range(qu_by_thr):
            qu[i][j].put("STOP")


    for i in range(thr_count):
        temp_str = [0,"",""]
        for j in range(len(qu[i])):
            while True:
                takeout = qu[i][j].get()
                if takeout == "STOP":
                    break
                else:
                    temp_str[0] = takeout[0]
                    temp_str[1] += takeout[1]
                    temp_str[2] += takeout[2]
        tmp_qu.append( (  temp_str[0],tuplist_parsing(temp_str[1]),tuplist_parsing(temp_str[2])  ) )


    tmp_qu = sorted(tmp_qu, key=lambda tup:tup[0])
    funcOutput_main = []
    funcOutput_dist_exceptInf_main = []
    for i in range(thr_count):
        funcOutput_main = funcOutput_main + tmp_qu[i][1]
        funcOutput_dist_exceptInf_main = funcOutput_dist_exceptInf_main + list(tmp_qu[i][2][0])
    tmp_qu.clear()
    del(th)
    th = []
    del(qu)
    qu = []




    maxDist = max(funcOutput_dist_exceptInf_main)

    for i in range(thr_count):
        qu.append([])
        for j in range(qu_by_thr):
            qu[i].append(Queue())

    for i in range(thr_count):
        if i != thr_count - 1:
            th.append(Process(target=coloring_work,
                              args=(i, interval * i, interval * (i + 1), maxDist, qu[i], funcOutput_main)))
        else:
            th.append(Process(target=coloring_work,
                              args=(i, interval * i, END, maxDist, qu[i], funcOutput_main)))

    for i in range(thr_count):
        th[i].start()
    for i in range(thr_count):
        th[i].join()
    for i in range(thr_count):
        for j in range(qu_by_thr):
            qu[i][j].put("STOP")


    for i in range(thr_count):
        temp_str = [0,""]
        for j in range(len(qu[i])):
            while True:
                takeout = qu[i][j].get()
                if takeout == "STOP":
                    break
                else:
                    temp_str[0] = takeout[0]
                    temp_str[1] += takeout[1]
        tmp_qu.append( (  temp_str[0],tuplist_parsing(temp_str[1])  ) )

    tmp_qu = sorted(tmp_qu, key=lambda tup: tup[0])
    funcOutput_colorized_main = []
    for i in range(thr_count):
        funcOutput_colorized_main = funcOutput_colorized_main + tmp_qu[i][1]


    """
    for i in range(quality):
        for j in range(quality):
            print(funcOutput_main[i * quality + j], end="")
        print()
    print()
    for i in range(quality):
        for j in range(quality):
            print(funcOutput_colorized_main[i * quality + j], end="")
        print()
    """
    print(time.perf_counter() - timer)

    pygame.init()

    screen = pygame.display.set_mode(display_size)
    run = True
    animated = False

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        screen.fill((255, 255, 255))

        # draw gradation!!
        if animated == False:
            for i in range(quality ** 2):
                tup = funcOutput_colorized_main[i]
                posx = display_rect_start[0] + (i % quality) * display_rect_size
                posy = display_rect_start[1] + (int(i / quality)) * display_rect_size

                pygame.draw.rect(screen,
                                 tup,
                                 [posx, posy, display_rect_size, display_rect_size],
                                 )
                if i % (quality // 3) == 0:
                    pygame.time.delay(10)
                    pygame.display.flip()

            pygame.display.flip()
            animated = True

    pygame.quit()
    sys.exit()

