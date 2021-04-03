__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"

import matplotlib.pyplot as plt
import numpy as np
import math
import random
import sys

sys.path.append("./")
sys.path.append("../")
import helper_functions as hf  # noqa: E402


def get_mean_std(input_list):
    m_val = np.mean(input_list)
    s_val = np.std(input_list)

    return m_val, s_val


def mean_std_all_flow_by_afp(common_configs, out_data_dict, __afp):
    n_switch = common_configs.n_default_sw
    mvl = []
    svl = []
    for nf in common_configs.number_of_flows_list:
        mean_val, std_val = get_mean_std(out_data_dict[n_switch][nf][__afp])
        mvl.append(mean_val)
        svl.append(std_val)
    return mvl, svl


def mean_std_all_switch_by_afp(common_configs, out_data_dict, __afp):
    n_flow = common_configs.n_default_flow
    mvl = []
    svl = []
    for n_switch in common_configs.num_switch_list:
        mean_val, std_val = get_mean_std(out_data_dict[n_switch][n_flow][__afp])
        mvl.append(mean_val)
        svl.append(std_val)
    return mvl, svl


def get_packet_lost(input_list):

    """
    Flow Rate 1 Mbps [used in Avionics experiments] => 1 * 1000000 bits/second
    Packet size 1024 Bytes => 1024 * 8 bits

    send rate: (1 * 1000000)/(1024*8) packets per second

    packet loss calculation:
    1000 ms -> (1 * 1000000)/(1024*8) packets = 122.0703125 packets
    1 ms -> 0.122 packets are lost
    x ms -> x * 0.122 where x is the time (ms) to compute MCP for affected flows
    """

    __pp_los_factor = 0.122
    output_list = [math.ceil(i * __pp_los_factor) for i in input_list]
    return output_list


def mean_std_for_packt_lost_all_flow_by_afp(common_configs, out_data_dict, __afp):
    n_switch = common_configs.n_default_sw
    mvl = []
    svl = []
    for nf in common_configs.number_of_flows_list:
        ilist = get_packet_lost(out_data_dict[n_switch][nf][__afp])
        mean_val, std_val = get_mean_std(ilist)
        mvl.append(mean_val)
        svl.append(std_val)
    return mvl, svl


def mean_std_for_packt_lost_all_switch_by_afp(common_configs, out_data_dict, __afp):
    n_flow = common_configs.n_default_flow
    mvl = []
    svl = []
    for n_switch in common_configs.num_switch_list:
        ilist = get_packet_lost(out_data_dict[n_switch][n_flow][__afp])
        mean_val, std_val = get_mean_std(ilist)
        mvl.append(mean_val)
        svl.append(std_val)
    return mvl, svl


def plot_vary_flow(trace_file, out_filename):
    result = hf.load_object_from_file(trace_file)

    out_data_dict = result.out_data_dict
    common_configs = result.common_configs

    x_val = common_configs.number_of_flows_list
    # n_switch = common_configs.n_default_sw

    plt.figure()

    __ff_time = 0.10  # time (ms) in fast-failover
    __ff_pck_lost = 15  # packets lost in fast-failover

    mlist, stdlist = mean_std_all_flow_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.75)
    mlist = [i/1000.0 for i in mlist]  # in second
    plt.plot(x_val, mlist, color='maroon', linestyle='-', marker='s', markersize=20, markeredgewidth=2.0,
             markerfacecolor='white', alpha=0.8, linewidth=5,
             label='FR-SDN (75%)')

    mlist, stdlist = mean_std_all_flow_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.50)
    mlist = [i / 1000.0 for i in mlist]  # in second
    plt.plot(x_val, mlist, color='maroon', linestyle='-.', marker='d', markersize=20, markeredgewidth=2.0,
             markerfacecolor='white', alpha=0.8, linewidth=5,
             label='FR-SDN (50%)')

    mlist, stdlist = mean_std_all_flow_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.25)
    mlist = [i / 1000.0 for i in mlist]  # in second
    plt.plot(x_val, mlist, color='maroon', linestyle=':', marker='x', markersize=20, markeredgewidth=2.0, 
             alpha=0.8, linewidth=5,
             label='FR-SDN (25%)')

    mlist, stdlist = mean_std_all_flow_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.1)
    mlist = [i / 1000.0 for i in mlist]  # in second
    plt.plot(x_val, mlist, color='maroon', linestyle='--', marker='o', markersize=20, markeredgewidth=2.0,
             markerfacecolor='white', alpha=0.8, linewidth=5,
             label='FR-SDN (10%)')

    plt.plot(x_val, [__ff_time] * int(len(x_val)), color='navy', linestyle='-', linewidth=5,
             marker='*', markersize=20, markeredgewidth=2.0,
             label='Fast-failover')

    plt.annotate(r'~100 $\mu$s', xy=(21, 1), xytext=(24, 1), arrowprops=dict(arrowstyle="->", lw=3.0))

    plt.xlabel('Number of Flows')
    plt.ylabel('Path Rerouting\nOverhead (s)')

    plt.legend(ncol=1, labelspacing=0.05, frameon=False)

    # plt.ylim([-2, 65])
    plt.ylim([-10, 100])

    plt.savefig(out_filename+"-time.pdf", pad_inches=0.1, bbox_inches='tight')
    plt.show()


    plt.figure()

    mlist, stdlist = mean_std_for_packt_lost_all_flow_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.75)
    plt.plot(x_val, mlist, color='maroon', linestyle='-', marker='s', markersize=20, markeredgewidth=2.0,
             markerfacecolor='white', alpha=0.8, linewidth=5,
             label='FR-SDN (75%)')

    mlist, stdlist = mean_std_for_packt_lost_all_flow_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.50)
    plt.plot(x_val, mlist, color='maroon', linestyle='-.', marker='d',  markersize=20, markeredgewidth=2.0,
             markerfacecolor='white', alpha=0.8, linewidth=5,
             label='FR-SDN (50%)')

    mlist, stdlist = mean_std_for_packt_lost_all_flow_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.25)
    plt.plot(x_val, mlist, color='maroon', linestyle=':', marker='x',  markersize=20, markeredgewidth=2.0, alpha=0.8, linewidth=5,
             label='FR-SDN (25%)')

    mlist, stdlist = mean_std_for_packt_lost_all_flow_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.1)
    plt.plot(x_val, mlist, color='maroon', linestyle='--', marker='o',  markersize=20, markeredgewidth=2.0,
             markerfacecolor='white', alpha=0.8, linewidth=5,
             label='FR-SDN (10%)')

    plt.plot(x_val, [__ff_pck_lost] * int(len(x_val)), color='navy', linestyle='-', linewidth=5,
             marker='*', markersize=20, markeredgewidth=2.0,
             label='Fast-failover')

    plt.annotate(r'~15 packets', xy=(17, 100), xytext=(20, 155), arrowprops=dict(arrowstyle="->", lw=3.0))

    plt.xlabel('Number of Flows')
    plt.ylabel('Number of Packets Lost')
    plt.legend(ncol=1, labelspacing=0.05, frameon=False)
    # plt.legend(ncol=1, loc='upper center', bbox_to_anchor=(0.5, 1.2), labelspacing=0.05, columnspacing=0.1)
    # plt.ylim([-500, 7000])
    plt.ylim([-500, 11000])

    # plt.ylim([-50, 1100])

    # ax = plt.gca()
    # ax.yaxis.get_major_formatter().set_powerlimits((2, 2))

    plt.savefig(out_filename+"-pktlost.pdf", pad_inches=0.1, bbox_inches='tight')
    plt.show()



def plot_vary_switch(trace_file, out_filename):
    result = hf.load_object_from_file(trace_file)

    out_data_dict = result.out_data_dict
    common_configs = result.common_configs

    x_val = common_configs.num_switch_list
    # n_switch = common_configs.n_default_sw

    plt.figure()

    __ff_time = 0.10  # time (ms) in fast-failover
    __ff_pck_lost = 15  # packets lost in fast-failover

    mlist, stdlist = mean_std_all_switch_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.75)
    mlist = [i/1000.0 for i in mlist]  # in second
    plt.plot(x_val, mlist, color='maroon', linestyle='-', marker='s', markersize=20, markeredgewidth=2.0,
             markerfacecolor='white', alpha=0.8, linewidth=5,
             label='FR-SDN (75%)')

    mlist, stdlist = mean_std_all_switch_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.50)
    mlist = [i / 1000.0 for i in mlist]  # in second
    plt.plot(x_val, mlist, color='maroon', linestyle='-.', marker='d', markersize=20, markeredgewidth=2.0,
             markerfacecolor='white', alpha=0.8, linewidth=5,
             label='FR-SDN (50%)')

    mlist, stdlist = mean_std_all_switch_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.25)
    mlist = [i / 1000.0 for i in mlist]  # in second
    plt.plot(x_val, mlist, color='maroon', linestyle=':', marker='x', markersize=20, markeredgewidth=2.0,
             alpha=0.8, linewidth=5,
             label='FR-SDN (25%)')

    mlist, stdlist = mean_std_all_switch_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.1)
    mlist = [i / 1000.0 for i in mlist]  # in second
    plt.plot(x_val, mlist, color='maroon', linestyle='--', marker='o', markersize=20, markeredgewidth=2.0,
             markerfacecolor='white', alpha=0.8, linewidth=5,
             label='FR-SDN (10%)')

    plt.plot(x_val, [__ff_time] * int(len(x_val)), color='navy', linestyle='-', linewidth=5,
             marker='*', markersize=20, markeredgewidth=2.0,
             label='Fast-failover')

    plt.annotate(r'~100 $\mu$s', xy=(13, 2), xytext=(16, 2), arrowprops=dict(arrowstyle="->", lw=3.0))

    plt.xlabel('Number of Switches')
    plt.ylabel('Path Rerouting\nOverhead (s)')

    plt.legend(ncol=1, labelspacing=0.05, frameon=False)
    # plt.ylim([-2000, 60000])
    plt.ylim([-10, 100])

    plt.savefig(out_filename+"-time.pdf", pad_inches=0.1, bbox_inches='tight')
    plt.show()


    plt.figure()

    mlist, stdlist = mean_std_for_packt_lost_all_switch_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.75)
    plt.plot(x_val, mlist, color='maroon', linestyle='-', marker='s', markersize=20, markeredgewidth=2.0,
             markerfacecolor='white', alpha=0.8, linewidth=5,
             label='FR-SDN (75%)')

    mlist, stdlist = mean_std_for_packt_lost_all_switch_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.50)
    plt.plot(x_val, mlist, color='maroon', linestyle='-.', marker='d',  markersize=20, markeredgewidth=2.0,
             markerfacecolor='white', alpha=0.8, linewidth=5,
             label='FR-SDN (50%)')

    mlist, stdlist = mean_std_for_packt_lost_all_switch_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.25)
    plt.plot(x_val, mlist, color='maroon', linestyle=':', marker='x',  markersize=20, markeredgewidth=2.0, alpha=0.8, linewidth=5,
             label='FR-SDN (25%)')

    mlist, stdlist = mean_std_for_packt_lost_all_switch_by_afp(common_configs=common_configs, out_data_dict=out_data_dict, __afp=0.1)
    plt.plot(x_val, mlist, color='maroon', linestyle='--', marker='o',  markersize=20, markeredgewidth=2.0,
             markerfacecolor='white', alpha=0.8, linewidth=5,
             label='FR-SDN (10%)')

    plt.plot(x_val, [__ff_pck_lost] * int(len(x_val)), color='navy', linestyle='-', linewidth=5,
             marker='*', markersize=20, markeredgewidth=2.0,
             label='Fast-failover')

    plt.annotate(r'~15 packets', xy=(11, 100), xytext=(14, 155), arrowprops=dict(arrowstyle="->", lw=3.0))

    plt.xlabel('Number of Switches')
    plt.ylabel('Number of Packets Lost')
    plt.legend(ncol=1, labelspacing=0.05, frameon=False)
    # plt.legend(ncol=1, loc='upper center', bbox_to_anchor=(0.5, 1.2), labelspacing=0.05, columnspacing=0.1)
    plt.ylim([-500, 11000])

    # plt.ylim([-50, 1100])

    # ax = plt.gca()
    # ax.yaxis.get_major_formatter().set_powerlimits((2, 2))

    plt.savefig(out_filename+"-pktlost.pdf", pad_inches=0.1, bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    # change font to Arial
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams['font.size'] = 60
    plt.rcParams['legend.fontsize'] = 55
    plt.rcParams['axes.titlesize'] = 50
    plt.rcParams['ytick.labelsize'] = 45
    plt.rcParams['xtick.labelsize'] = 45
    plt.rcParams['figure.figsize'] = [16.0, 12.0]



    plot_vary_flow(trace_file='traces_to_plot/varying_flow_exp.pickle.gzip', out_filename='frsdn_comp_vaying_flow')
    plot_vary_switch(trace_file='traces_to_plot/varying_switch_exp.pickle.gzip', out_filename='frsdn_comp_vaying_switch')

    print("Script finished!")
