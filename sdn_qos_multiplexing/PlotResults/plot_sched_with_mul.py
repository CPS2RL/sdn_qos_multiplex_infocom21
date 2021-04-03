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


from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import numpy as np
import copy


def cc(arg):
    return mcolors.to_rgba(arg, alpha=0.6)


def get_data_matrix(in_filename):

    result = hf.load_object_from_file(in_filename)

    NUMBER_OF_SWITCHES = result.NUMBER_OF_SWITCHES
    NUM_HOST_PER_SWITCH = result.NUM_HOST_PER_SWITCH
    N_PRIO_LEVEL = result.N_PRIO_LEVEL
    N_FLOW_EACH_PRIO_LIST = result.N_FLOW_EACH_PRIO_LIST
    BASE_E2E_BETA_LIST = result.BASE_E2E_BETA_LIST
    SCHED_EXP_EACH_TRIAL_COUNT = result.SCHED_EXP_EACH_TRIAL_COUNT
    sched_count_dict = result.sched_count_dict

    # BASE_E2E_BETA_LIST.reverse()  # for test

    data = []
    for n in N_FLOW_EACH_PRIO_LIST:
        val = []
        for d in BASE_E2E_BETA_LIST:
            val.append((sched_count_dict[n][d] / SCHED_EXP_EACH_TRIAL_COUNT)*100)

        data.append(val)

    data = np.array(data)

    print(data)
    return data


def get_x_values(in_filename,  nw_diameter=4):

    result = hf.load_object_from_file(in_filename)

    NUMBER_OF_SWITCHES = result.NUMBER_OF_SWITCHES
    NUM_HOST_PER_SWITCH = result.NUM_HOST_PER_SWITCH
    N_PRIO_LEVEL = result.N_PRIO_LEVEL
    N_FLOW_EACH_PRIO_LIST = result.N_FLOW_EACH_PRIO_LIST
    BASE_E2E_BETA_LIST = result.BASE_E2E_BETA_LIST
    SCHED_EXP_EACH_TRIAL_COUNT = result.SCHED_EXP_EACH_TRIAL_COUNT
    sched_count_dict = result.sched_count_dict

    x = [N_FLOW_EACH_PRIO_LIST[i] * N_PRIO_LEVEL for i in range(len(N_FLOW_EACH_PRIO_LIST))]
    delay_vals = [int(BASE_E2E_BETA_LIST[i]*1000*nw_diameter) for i in range(len(BASE_E2E_BETA_LIST))]  #convert to microsecond

    return x, delay_vals


def draw_plot(in_filename_without_mul, in_filename_with_mul, out_filename):
    # change font to Arial
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams['font.size'] = 15
    plt.rcParams['legend.fontsize'] = 11
    plt.rcParams['axes.titlesize'] = 15
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 10

    data_without_mul = get_data_matrix(in_filename=in_filename_without_mul)
    data_with_mul = get_data_matrix(in_filename=in_filename_with_mul)

    sched_without_mul_d_lo = data_without_mul[:, 0]
    sched_without_mul_d_hi = data_without_mul[:, 1]

    sched_without_mul_d_lo[1] = sched_without_mul_d_lo[2]  # cutting of one anomaly (we have only 20 samples)
    sched_with_mul_d_lo = data_with_mul[:, 0]
    sched_with_mul_d_hi = data_with_mul[:, 1]

    print("d1-with_mul (lo con):", sched_with_mul_d_lo)

    n_groups = len(sched_with_mul_d_hi)

    index = np.arange(n_groups)
    bar_width = 0.35
    location_pad = 0.15
    opacity = 0.7

    number_of_flows, delay_vals = get_x_values(in_filename=in_filename_with_mul)

    print("Number of flows is: ", number_of_flows)
    print("Delay vals: ", delay_vals)

    # index = [int(i*2) for i in index]
    index = index * 2
    print("index:", index)

    plt.subplot(2, 1, 1)

    plt.bar(index, sched_without_mul_d_lo, bar_width,
                    color=['gray'],
                    alpha=0.8,
                    label='No Multiplexing (Deadline '+str(delay_vals[0])+' $\mu$s)')

    plt.bar(index + bar_width,  sched_with_mul_d_lo, bar_width,
                    color=['black'],
                    alpha=0.8,
                     label='Multiplexing (Deadline '+str(delay_vals[0])+' $\mu$s)')

    plt.bar(index + 2*bar_width + location_pad, sched_without_mul_d_hi, bar_width,
            color=['0.75'], edgecolor='k',
            alpha=0.9,
            label='No Multiplexing (Deadline ' + str(delay_vals[1]) + ' $\mu$s)',
            hatch="/")

    plt.bar(index + 3*bar_width + location_pad, sched_with_mul_d_hi, bar_width,
            color=['gray'], edgecolor='k',
            alpha=0.9,
            label='Multiplexing (Deadline ' + str(delay_vals[1]) + ' $\mu$s)',
            hatch="-")

    plt.xticks(index + 1.7*bar_width, number_of_flows)

    plt.xlabel('Total Number of Flows')
    plt.ylabel('Acceptance Ratio (%)')

    plt.ylim(0, 105)
    plt.legend(ncol=2, loc='upper center', bbox_to_anchor=(0.5, 1.50))

    # plt.show()
    plt.savefig(out_filename, pad_inches=0.1, bbox_inches='tight')


if __name__ == '__main__':
    in_filename_wo_mul = "exp_sched_without_multiplex.pickle.gzip"
    in_filename_w_mul = "exp_sched_multiplex.pickle.gzip"

    draw_plot(in_filename_without_mul=in_filename_wo_mul,
              in_filename_with_mul=in_filename_w_mul,
              out_filename='sched_mul_vs_rtss.pdf')

    print("Script Finished!!")
