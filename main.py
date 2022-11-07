import sys
import time
from frechetdist import frdist
import matplotlib.pyplot as plt
import numpy as np
import sample_data
import compare
import threadpool
import preference

if __name__ == "__main__":
    sys.setrecursionlimit(1000000)

    offset = 400

    if preference.UI_ENABLED == True:
        plt.ion()

    for area in range(11, 14):
        target_curve_points = []
        for i in range(0, sample_data.STEP_SIZE):
            point = []
            point.append(i)
            point.append(sample_data.data2[i + offset][area])
            target_curve_points.append(point)

        compare.CompareJob(sample_data.WIN_SIZE, area,
                           target_curve_points, 20.0, sample_data.STEP_SIZE)

    while True:
        threadpool.from_main_thread_nonblocking()
        time.sleep(0.001)
