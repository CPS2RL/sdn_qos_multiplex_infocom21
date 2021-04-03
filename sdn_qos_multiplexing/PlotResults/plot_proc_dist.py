# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"


from config import *
import helper_functions as hf
from collections import defaultdict
import numpy as np

import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

import pandas as pd


def get_trace_by_index(data, index):

    """ Returns corresponding trace ignoring nan """

    trace = data[:, index]
    trace = trace[~np.isnan(trace)]

    return trace


def getCDF_XY(data):
    x = np.sort(data)

    # calculate the proportional values of samples
    y = 1. * np.arange(len(data)) / (len(data) - 1)

    return x, y


def plot_distribution(outfilename, tracefilename):
    # change font to Arial
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams['font.size'] = 15
    plt.rcParams['legend.fontsize'] = 13
    plt.rcParams['axes.titlesize'] = 15
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 10

    df = pd.read_excel(open(tracefilename, 'rb'), sheetname=0)

    data = df.as_matrix()
    print(data)

    trace400 = get_trace_by_index(data=data, index=0)
    trace400 = trace400/1000

    trace512 = get_trace_by_index(data=data, index=1)
    trace512 = trace512/1000  # for microsecond

    trace1024 = get_trace_by_index(data=data, index=2)
    trace1024 = trace1024/1000

    x400, y400 = getCDF_XY(trace400)


    x512, y512 = getCDF_XY(trace512)


    x1024, y1024 = getCDF_XY(trace1024)




    fig = plt.figure()

    plt.subplot(2, 1, 1)

    plt.plot(x400, y400, linestyle='-', marker='o', markerfacecolor='None', markersize=4, color='k', alpha=0.7, label="400 Bytes")
    # plt.plot(x400, y400, linestyle='-', marker='o', markersize=7,
    #         markeredgewidth=1,markeredgecolor='g',
    #         markerfacecolor='None', alpha=0.7, label="400 Bytes")
    plt.plot(x512, y512, linestyle='--', marker='x', color='k', alpha=0.7, label="512 Bytes")
    plt.plot(x1024, y1024, linestyle=':', marker='*', color='k', alpha=0.7, label="1024 Bytes")


    plt.xlabel('Packet Processing Delay ($\mu$s)')
    # plt.ylabel('Cumulative Distribution Function (CDF)')
    plt.ylabel('CDF')
    plt.legend()

    plt.savefig(outfilename, pad_inches=0.1, bbox_inches='tight')

    plt.show()




if __name__ == '__main__':
    outfilename = 'proc_dist.pdf'
    tracefilename = 'proc_delay_trace.xlsx'
    plot_distribution(outfilename, tracefilename)

    print("Script Finished!!")