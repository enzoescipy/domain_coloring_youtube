from multiprocessing import Process, Queue
import time
import sympy as sp
import numpy as np

function_limit = 10  # this limit is abs() value of complex number.
quality = 10  # colorline_size ** 2 is total data length.

z = sp.symbols("z")
a = sp.symbols("a", real=True, imaginary=False)  # use for real domain
b = sp.symbols("b", real=True, imaginary=False)  # use for imaginary domain
x = sp.symbols("x")
my_sigmoid = (1 / (1 + np.e ** (-30 * x)) - 0.5) * 2

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

def numeric_work(id, start, end, task_queue,func_real, func_imag):
    print(id, "started")
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
        print(i,"numeric_",id)
        x = i % quality
        y = i // quality
        numeric_process(funcInput_glob(x, y))
    task_queue.put((id,funcOutput_tmp,funcOutput_dist_exceptInf_tmp))
    print(id,"ended")
    return


def coloring_work(id, start, end, maxDist,task_queue, funcOutput):
    print(id,"started")
    funcOutput_colorized_tmp= []
    def coloring_process(tup, maxDist):
        yvalue_colorized = tup_to_color(tup, maxDist)
        funcOutput_colorized_tmp.append(yvalue_colorized)


    for i in range(start, end):
        print(i, "coloring_", id)
        coloring_process(funcOutput[i], maxDist)
    task_queue.put(funcOutput_colorized_tmp)
    print(id,"ended")
    return

if __name__ == '__main__':
    timer = time.perf_counter()


    display_size = (1024, 640)
    display_rect_start = (262, 70)  # think midpoint for 512, 320 and length for 500.
    display_rect_size = 2



    print("all basic math function should be wrote like cos(x) * x + x**2 ")
    # func_str_input = input("please write your function with z.  :")
    # func_str_input = "x**-2 * sin(1/x*10)"
    func_str_input = "z**2"

    func_syp = sp.sympify(func_str_input)
    func_syp = func_syp.subs(z, (a + b * sp.I))
    func_syp = sp.expand(func_syp)
    func_real, func_imag = func_syp.as_real_imag()
    # (a**2 - b**2, 2*a*b) for (real, imag)



    funcOutput_main = []
    funcOutput_colorized_main = []
    funcOutput_dist_exceptInf_main = []

    ##threading
    task_queue = Queue()
    temp_tasklist = []
    th1 = Process(target=numeric_work, args=(1, START, END // 2,task_queue,func_real, func_imag))
    th2 = Process(target=numeric_work, args=(2, END // 2, END,task_queue,func_real, func_imag))
    th1.start()
    th2.start()
    th1.join()
    th2.join()
    task_queue.put("STOP")

    while True:
        takeout = task_queue.get()
        if takeout == "STOP":
            print("?")
            break
        else:
            print("!")
            temp_tasklist.append(takeout)

    temp_tasklist = sorted(temp_tasklist, key=lambda tup:tup[0])
    funcOutput_main = temp_tasklist[0][1] + temp_tasklist[1][1]
    funcOutput_dist_exceptInf_main = temp_tasklist[0][2] + temp_tasklist[1][2]
    temp_tasklist.clear()
    del(th1)
    del(th2)

    maxDist = max(funcOutput_dist_exceptInf_main)

    th1 = Process(target=coloring_work, args=(1, START, END // 2, maxDist,task_queue, funcOutput_main))
    th2 = Process(target=coloring_work, args=(2, END // 2, END, maxDist, task_queue, funcOutput_main))

    th1.start()
    th2.start()
    th1.join()
    th2.join()
    task_queue.put("STOP")

    while True:
        takeout = task_queue.get()
        if takeout == "STOP":
            print("?")
            break
        else:
            print("!")
            temp_tasklist.append(takeout)

    temp_tasklist = sorted(temp_tasklist, key=lambda tup: tup[0])
    funcOutput_colorized_main =temp_tasklist[0] + temp_tasklist[1]
    ##threading


    """
    for i in range(quality):
        for j in range(quality):
            print(funcOutput[i * quality + j], end="")
        print()
    print()
    for i in range(quality):
        for j in range(quality):
            print(funcOutput_colorized[i * quality + j], end="")
        print()
    """
    print(time.perf_counter() - timer)
##multiprocessing


