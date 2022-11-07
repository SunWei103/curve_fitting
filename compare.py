import time
import threading
from frechetdist import frdist
from functools import wraps
import matplotlib.pyplot as plt
import sample_data
import threadpool
import preference


class JobCounter():
    def __init__(self):
        self.__lock = threading.Lock()
        self.__ref = 0

    def increase(self):
        self.__lock.acquire()
        ref = self.__ref = self.__ref + 1
        self.__lock.release()
        return ref

    def decrease(self):
        self.__lock.acquire()
        ref = self.__ref = self.__ref - 1
        self.__lock.release()
        return ref


job_counter = JobCounter()


def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print("Total time running %s: %s seconds" %
              (function.__name__, str(t1-t0)))
        return result
    return function_timer


def do_frdist(P, Q):
    return frdist(P, Q)


def show_result(args):
    area = args[0]
    B = args[1]
    D = args[2]

    x = []
    y = []
    for i in range(0, len(D)):
        x.append(D[i][0])
        y.append(D[i][1])

    a = []
    b = []
    for i in range(0, len(B)):
        a.append(B[i][0])
        b.append(B[i][1])

    plt.figure(area, (9.6, 2.7))
    plt.clf()
    plt.plot(x, y)
    plt.plot(a, b)
    plt.pause(0.000001)
    plt.ioff()


def show_end(args):
    area = args[0]
    ref = job_counter.decrease()

    if ref == 0:
        plt.figure(area, (9.6, 2.7))
        plt.show()


class CompareJob(threading.Thread):

    def __init__(self, winsize, area, target_curve_points, metric, step_size):
        super().__init__()

        self.__winsize = winsize
        self.__area = area
        self.__target_curve_points = target_curve_points
        self.__metric = metric
        self.__step_size = step_size

        self.start()

    @fn_timer
    def cal_distance(self, winsize, area, target_curve_points, metric, step_size):
        offset = 0
        source_curve_points = []
        m = 100

        if preference.UI_ENABLED == True:
            for i in range(0, winsize):
                point = []
                point.append(i)
                point.append(sample_data.data1[i][area])
                source_curve_points.append(point)

        for offset in range(0, winsize - len(target_curve_points), step_size):
            slide_source_curve_points = []
            for i in range(0, len(target_curve_points)):
                point = []
                point.append(i)
                point.append(sample_data.data1[offset + i][area])
                slide_source_curve_points.append(point)

            if preference.UI_ENABLED == True:
                slide_target_curve_points = []
                for i in range(0, len(target_curve_points)):
                    slide_target_curve_points.append(
                        [target_curve_points[i][0] + offset, target_curve_points[i][1]])

                threading.Thread(target=threadpool.dummy_run, args=(
                    show_result, (area, slide_target_curve_points, source_curve_points))).start()

            m = do_frdist(slide_source_curve_points, target_curve_points)
            if m <= metric:
                print(
                    "--------------------------------------------------------------------------------")
                print("offset = {:d}, metric = {:f}".format(offset, m))
                print("A are[{:d}]".format(area))
                print(slide_source_curve_points)
                print("B are[{:d}]".format(area))
                print(target_curve_points)
                print(
                    "--------------------------------------------------------------------------------")
                break

        threading.Thread(target=threadpool.dummy_run,
                         args=(show_end, (area,))).start()

    def run(self):
        job_counter.increase()
        self.cal_distance(self.__winsize, self.__area,
                          self.__target_curve_points, self.__metric, self.__step_size)
