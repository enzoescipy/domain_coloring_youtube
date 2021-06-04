from multiprocessing import Process, Queue


def work(id, start, end, result):
    total = 0
    for i in range(start, end):
        total += i
    result.makeTrue()
    return

class justList:
    def __init__(self):
        self.bool = False
    def makeTrue(self):
        self.bool = True
if __name__ == "__main__":
    START, END = 0, 1000
    result = justList()
    th1 = Process(target=work, args=(1, START, END // 2, result))
    th2 = Process(target=work, args=(2, END // 2, END, result))

    th1.start()
    th2.start()
    th1.join()
    th2.join()


    print(result.bool)
