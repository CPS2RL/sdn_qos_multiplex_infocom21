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


def plot_3d_bar(in_filename, out_filename, nw_diameter, fig_num):
    # change font to Arial
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams['font.size'] = 15
    plt.rcParams['legend.fontsize'] = 13
    plt.rcParams['axes.titlesize'] = 15
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 10

    result = hf.load_object_from_file(in_filename)

    NUMBER_OF_SWITCHES = result.NUMBER_OF_SWITCHES
    NUM_HOST_PER_SWITCH = result.NUM_HOST_PER_SWITCH
    N_PRIO_LEVEL = result.N_PRIO_LEVEL
    N_FLOW_EACH_PRIO_LIST = result.N_FLOW_EACH_PRIO_LIST
    BASE_E2E_BETA_LIST = result.BASE_E2E_BETA_LIST
    SCHED_EXP_EACH_TRIAL_COUNT = result.SCHED_EXP_EACH_TRIAL_COUNT
    sched_count_dict = result.sched_count_dict

    BASE_E2E_BETA_LIST.reverse()  # for test

    data = []
    for n in N_FLOW_EACH_PRIO_LIST:
        val = []
        for d in BASE_E2E_BETA_LIST:
            val.append((sched_count_dict[n][d] / SCHED_EXP_EACH_TRIAL_COUNT)*100)

        data.append(val)

    data = np.array(data)

    print(data)

    column_names = [int(BASE_E2E_BETA_LIST[i]*1000*nw_diameter) for i in range(len(BASE_E2E_BETA_LIST))]  #convert to microsecond
    row_names = [N_FLOW_EACH_PRIO_LIST[i] * N_PRIO_LEVEL for i in range(len(N_FLOW_EACH_PRIO_LIST))]

    print("NFLOW EACH PRIo", N_FLOW_EACH_PRIO_LIST)
    print("N_PRIO_LEV", N_PRIO_LEVEL)
    print("Row name:", row_names)

    fig = plt.figure(fig_num)
    ax = Axes3D(fig)

    # following code is taken from
    # https://goo.gl/u7gAqR

    lx = len(data[0])  # Work out matrix dimensions
    ly = len(data[:, 0])
    xpos = np.arange(0, lx, 1)  # Set up a mesh of positions
    ypos = np.arange(0, ly, 1)
    xpos, ypos = np.meshgrid(xpos + 0.25, ypos + 0.25)

    xpos = xpos.flatten()  # Convert positions to 1D array
    ypos = ypos.flatten()
    zpos = np.zeros(lx * ly)

    dx = 0.5 * np.ones_like(zpos)
    dy = dx.copy()
    dz = data.flatten()

    cs = plt.cm.gray(data.flatten() / float(data.max()))

    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=cs, edgecolor='k', alpha=0.7)

    ax.w_xaxis.set_ticklabels(column_names)
    ax.w_yaxis.set_ticklabels(row_names)
    ax.set_xlabel('End To End Deadline')
    ax.set_ylabel('Total Number of Flows')
    ax.set_zlabel('Acceptance Ratio (%)')

    ax.set_zlim(0, 100)

    # ax.view_init(azim=50, elev=15)
    ax.view_init(azim=61, elev=27)

    ticksx = np.arange(0.5, len(column_names), 1)
    plt.xticks(ticksx, column_names)

    ticksy = np.arange(0.6, len(row_names), 1)
    plt.yticks(ticksy, row_names)

    # plt.tight_layout()

    plt.savefig(out_filename, pad_inches=-0.1, bbox_inches='tight')
    plt.show()




def plot_3d_surface(in_filename, out_filename, nw_diameter, fig_num):

    # change font to Arial
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams['font.size'] = 15
    plt.rcParams['legend.fontsize'] = 13
    plt.rcParams['axes.titlesize'] = 15
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 10

    result = hf.load_object_from_file(in_filename)


    NUMBER_OF_SWITCHES = result.NUMBER_OF_SWITCHES
    NUM_HOST_PER_SWITCH = result.NUM_HOST_PER_SWITCH
    N_PRIO_LEVEL = result.N_PRIO_LEVEL
    N_FLOW_EACH_PRIO_LIST = result.N_FLOW_EACH_PRIO_LIST
    BASE_E2E_BETA_LIST = result.BASE_E2E_BETA_LIST
    SCHED_EXP_EACH_TRIAL_COUNT = result.SCHED_EXP_EACH_TRIAL_COUNT
    sched_count_dict = result.sched_count_dict

    BASE_E2E_BETA_LIST.pop()
    BASE_E2E_BETA_LIST.reverse()  # for better view

    N_FLOW = [N_FLOW_EACH_PRIO_LIST[i] * N_PRIO_LEVEL for i in range(len(N_FLOW_EACH_PRIO_LIST))]

    column_names = [int(BASE_E2E_BETA_LIST[i]*1000*nw_diameter) for i in range(len(BASE_E2E_BETA_LIST))]  #convert to microsecond
    # column_names = [r'{}$\times\delta$'.format(int(BASE_E2E_BETA_LIST[i] * 1000)) for i in
    #                 range(len(BASE_E2E_BETA_LIST))]  # convert to microsecond
    # row_names = [N_FLOW_EACH_PRIO_LIST[i] * N_PRIO_LEVEL for i in range(len(N_FLOW_EACH_PRIO_LIST))]
    row_names = N_FLOW

    column_names.reverse()



    fig = plt.figure(fig_num)
    ax = Axes3D(fig)



    X, Y = np.meshgrid(N_FLOW, BASE_E2E_BETA_LIST)

    # Z = np.zeros((len(N_FLOW_EACH_PRIO_LIST), (len(BASE_E2E_BETA_LIST)))  # initialize

    Z = np.zeros((len(BASE_E2E_BETA_LIST), len(N_FLOW_EACH_PRIO_LIST)))  # initialize


    for row in range(len(BASE_E2E_BETA_LIST)):
        for col in range(len(N_FLOW_EACH_PRIO_LIST)):
            vv = sched_count_dict[N_FLOW_EACH_PRIO_LIST[col]][BASE_E2E_BETA_LIST[row]]
            Z[row][col] = (vv/SCHED_EXP_EACH_TRIAL_COUNT) * 100  # in percent

    print("X:", X)
    print("Y:", Y)
    print("Z:", Z)
    ax.plot_surface(X, Y, Z, linewidth=1.0, cmap=plt.cm.gray, rstride=1, cstride=1, alpha=0.7,  edgecolors='k')
    # ax.plot_surface(X, Y, Z)

    ax.set_ylabel('End To End Deadline ($\mu$s)')
    ax.set_xlabel('Total Number of Flows')
    ax.set_zlabel('Acceptance Ratio (%)')

    ax.set_zlim(0, 100)
    # ax.set_xlim(1, max(N_FLOW)+ 2)

    ax.view_init(azim=-17, elev=25)
    ax.set_xticklabels(row_names)
    #ax.set_yticklabels(column_names)
    #ax.set_yticklabels(labels=column_names)


    #print("colname:", column_names)
    #print("base e2e beta:", BASE_E2E_BETA_LIST)
    #ylabels = ax.get_yticklabels(locs=BASE_E2E_BETA_LIST, labels=column_names)

    #labels = [yl.get_text() for yl in ylabels]
    #print("labels", labels)

    # this two comment out if we don't want to show diameter
    # plt.yticks(rotation=20)
    # ax.yaxis.labelpad = 10

    #print(ax.get_yticklabels())
    ax.set_yticklabels(ax.get_yticks())  # must do this
    labels = ax.get_yticklabels()

    colnamelist  = [int(float(label.get_text())*1000*nw_diameter) for label in labels]
    ax.set_yticklabels(labels=colnamelist)


    print(colnamelist)

    ax.tick_params(direction='out', pad=1)



    # plt.tight_layout()

    plt.savefig(out_filename, pad_inches=0.12, bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    in_filename = "exp_sched.pickle.gzip"

    # plot_sched(filename)
    # plot_3d_bar(in_filename=in_filename, out_filename='sched_5.pdf', nw_diameter=4, fig_num=1)
    plot_3d_surface(in_filename=in_filename, out_filename='sched_5.pdf', nw_diameter=4, fig_num=1)

    print("Script Finished!!")
