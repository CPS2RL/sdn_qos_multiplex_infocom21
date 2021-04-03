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
import scipy.stats as st


def get_delay(result, delay_dict, tag_flow_prio):
    delay_list = []
    for n_flow_each_prio in result.N_FLOW_EACH_PRIO_LIST:
        delay_list.append(delay_dict[n_flow_each_prio][tag_flow_prio])

    return delay_list


def plot_single_node():

    # change font to Arial
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams['font.size'] = 15
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['axes.titlesize'] = 15
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 10

    # filename = "../" + PARAMS.EXP_SINGLE_NODE_FILENAME
    filename = "exp_single_node.pickle.gzip"
    result = hf.load_object_from_file(filename)

    all_delay_dict = result.all_delay_dict

    # i = 5
    # j = 4
    # k = 2
    #
    # print(all_delay_dict[i][j][k])

    # n_flow_each_prio = 2
    # tag_flow_prio = 4
    # dl = []
    #
    # for count in range(result.N_SINGLE_NODE_EXP_SAMPLE_RUN):
    #     dl.append(all_delay_dict[n_flow_each_prio][tag_flow_prio][count])
    #
    # print("Trace:", dl)

    mean_delay = defaultdict(lambda: defaultdict(dict))
    std_delay = defaultdict(lambda: defaultdict(dict))

    for n_flow_each_prio in result.N_FLOW_EACH_PRIO_LIST:
        for tag_flow_prio in result.TAG_FLOW_PRIO_LIST:
            dl = []
            for count in range(result.N_SINGLE_NODE_EXP_SAMPLE_RUN):
                dl.append(all_delay_dict[n_flow_each_prio][tag_flow_prio][count])
                # dl.append(all_delay_dict[n_flow_each_prio][tag_flow_prio][count]*1000.00)  # change to microsecond

            print("Trace:", dl)
            # mean_delay[n_flow_each_prio][tag_flow_prio] = np.mean(dl)  # millisecond
            # std_delay[n_flow_each_prio][tag_flow_prio] = np.std(dl)

            mean_delay[n_flow_each_prio][tag_flow_prio] = np.mean(dl)
            std_delay[n_flow_each_prio][tag_flow_prio] = np.std(dl)
            #


            # mean_delay[n_flow_each_prio][tag_flow_prio] = max(dl)  # millisecond
            # std_delay[n_flow_each_prio][tag_flow_prio] = np.std(dl)
            mean_delay[n_flow_each_prio][tag_flow_prio] = np.percentile(dl, 99)  # millisecond
            # std_delay[n_flow_each_prio][tag_flow_prio] = st.t.interval(0.95, len(dl) - 1, loc=np.mean(dl), scale=st.sem(dl))
            std_delay[n_flow_each_prio][tag_flow_prio] = st.sem(dl)
            # std_delay[n_flow_each_prio][tag_flow_prio] = np.var(dl)


    print(mean_delay)

    print("mean:", mean_delay[5][4])
    print("std:", std_delay[5][4])

    plt.subplot(2, 1, 1)


    y_pos = np.arange(len(result.N_FLOW_EACH_PRIO_LIST))
    y_delta = 0.25
    bar_width = 0.25

    tag_flow_prio = result.TAG_FLOW_PRIO_LIST[0]
    mean_delay_list = get_delay(result, mean_delay, tag_flow_prio)
    std_delay_list = get_delay(result, std_delay, tag_flow_prio)
    print(mean_delay_list)
    print(std_delay_list)
    plt.bar(y_pos, mean_delay_list, bar_width, yerr=std_delay_list,
            color=['gray'], edgecolor='k',
            alpha=0.9, label="High Priority")


    tag_flow_prio = result.TAG_FLOW_PRIO_LIST[1]
    mean_delay_list = get_delay(result, mean_delay, tag_flow_prio)
    std_delay_list = get_delay(result, std_delay, tag_flow_prio)
    print(mean_delay_list)
    print(std_delay_list)
    plt.bar(y_pos+y_delta, mean_delay_list,  bar_width, yerr=std_delay_list,
            color=['gray'],
            alpha=0.6,
            edgecolor='k',
            label="Medium Priority",
            error_kw=dict(ecolor='black', alpha=0.5, lw=2, capsize=5, capthick=2))

    tag_flow_prio = result.TAG_FLOW_PRIO_LIST[2]
    mean_delay_list = get_delay(result, mean_delay, tag_flow_prio)
    std_delay_list = get_delay(result, std_delay, tag_flow_prio)
    print(mean_delay_list)
    print(std_delay_list)



    plt.bar(y_pos + 2*y_delta, mean_delay_list, bar_width, yerr=std_delay_list,
            color=['gray'],
            alpha=0.3,
            edgecolor='k',
            label="Low Priority",
            error_kw=dict(ecolor='black', alpha=0.5, lw=2, capsize=5, capthick=2))


    plt.xticks(y_pos+bar_width, result.N_FLOW_EACH_PRIO_LIST)
    # label = [ r'3 $\times$ {} = {}'.format(result.N_FLOW_EACH_PRIO_LIST[i], 3*result.N_FLOW_EACH_PRIO_LIST[i]) for i in range(len(result.N_FLOW_EACH_PRIO_LIST))]
    label = [3*result.N_FLOW_EACH_PRIO_LIST[i] for i in range(len(result.N_FLOW_EACH_PRIO_LIST))]
    ax = plt.gca() # grab the current axis
    ax.set_xticklabels(label)

    plt.xlabel('Total Number of Flows')
    plt.ylabel('Observed Delay (ms)')
    plt.legend()




    # plt.tight_layout()

    plt.savefig("delay_validation.pdf", pad_inches=0.1, bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    plot_single_node()

    print("Script Finished!!")