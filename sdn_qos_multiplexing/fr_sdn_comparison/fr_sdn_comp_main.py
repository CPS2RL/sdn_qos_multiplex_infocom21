__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"

import math
import random
import copy
import time
from collections import defaultdict
import sys
sys.path.append("./")
sys.path.append("../")

import fr_sdn_comparison.mcp_helper as mcph  # noqa: E402
import helper_functions as hf  # noqa: E402


# class to save varying flow experiment
class FRSDNFlowOutClass(object):
    def __init__(self, common_configs, out_data_dict):
        self.common_configs = common_configs
        self.out_data_dict = out_data_dict


# a class to save common configurations
class CommonConfigs(object):

    def __init__(self, n_default_sw, n_default_flow, num_switch_list, num_hosts_per_switch, link_delay, link_bw, number_of_flows_list,
                 delay_budget_lb_ub, bw_req_lb_ub, n_trial_per_exp,
                 affected_flow_per_list):
        self.n_default_sw = n_default_sw
        self.n_default_flow = n_default_flow
        self.num_switch_list = num_switch_list
        self.num_hosts_per_switch = num_hosts_per_switch
        self.link_delay = link_delay  # us
        self.link_bw = link_bw  # MBPS

        self.number_of_flows_list = number_of_flows_list
        self.delay_budget_lb_ub = delay_budget_lb_ub
        self.bw_req_lb_ub = bw_req_lb_ub
        self.n_trials_per_exp = n_trial_per_exp
        self.affected_flow_per_list = affected_flow_per_list


def compute_fr_sdn_runtime(nw_graph, flow_specs, affected_flow_per):
    if affected_flow_per > 1 or affected_flow_per < 0:
        raise Exception("Invalid percentage")

    # call mcp to get path layout
    mcph.get_fr_sdn_path_by_mcp(nw_graph, flow_specs)
    # don't calculate timeout if not schedulable
    if not mcph.test_all_flow_is_schedulable(flow_specs):
        return None

    n_flows = len(flow_specs)

    n_aff_flow = math.ceil(n_flows * affected_flow_per)
    rand_flow_indx_list = random.sample(range(0, n_flows), n_aff_flow)

    # print("n aff:", n_aff_flow)

    aff_flow_specs = []
    for indx in rand_flow_indx_list:
        _aflow = copy.deepcopy(flow_specs[indx])
        aff_flow_specs.append(_aflow)

    # NOTE: perf_counter_ns() does not work < python 3.7
    # recalculate for getting runtime overhead mcp to get path layout
    t1 = time.perf_counter()
    mcph.get_fr_sdn_path_by_mcp(nw_graph, aff_flow_specs)
    t2 = time.perf_counter()

    # do the double loop timing
    dt1 = time.perf_counter()
    dt2 = time.perf_counter()

    elapsed = (t2 - t1) - (dt2 - dt1)

    # elapsed = elapsed * 0.000001  # ms
    elapsed = elapsed * 1000  # ms
    return elapsed


def init_dict_varying_flow_exp(com_configs, n_switch):
    empty_list = []
    out_data_dict = defaultdict(dict)
    for number_of_flows in com_configs.number_of_flows_list:
        for afp in com_configs.affected_flow_per_list:
            out_data_dict[n_switch][number_of_flows][afp] = empty_list

    return out_data_dict


def run_varying_flow_exp(common_configs):

    out_data_dict = defaultdict(lambda: defaultdict(dict))

    for number_of_flows in common_configs.number_of_flows_list:
        nw_graph = mcph.setup_network_graph_without_mininet(common_configs.n_default_sw, common_configs.num_hosts_per_switch,
                                                            common_configs.link_delay, common_configs.link_bw)
        flow_specs = mcph.prepare_flow_specifications(common_configs.n_default_sw, common_configs.num_hosts_per_switch, number_of_flows,
                                                      common_configs.delay_budget_lb_ub, common_configs.bw_req_lb_ub)

        for afp in common_configs.affected_flow_per_list:
            etime_list = []
            for cnt in range(common_configs.n_trials_per_exp):
                # get computation time in ms
                print("==VARY_FLOW_EXP== N_SW", common_configs.n_default_sw,
                      ", N_FLOWS:", number_of_flows, ", AFP:", afp, ", Trial #", cnt + 1)
                etime = compute_fr_sdn_runtime(nw_graph, flow_specs, afp)
                etime_list.append(etime)

            # print(etime_list)
            out_data_dict[common_configs.n_default_sw][number_of_flows][afp] = etime_list

    return out_data_dict


# vary the network topology
def run_varying_switch_exp(common_configs):

    out_data_dict = defaultdict(lambda: defaultdict(dict))

    for n_switch in common_configs.num_switch_list:
        nw_graph = mcph.setup_network_graph_without_mininet(n_switch, common_configs.num_hosts_per_switch,
                                                            common_configs.link_delay, common_configs.link_bw)
        flow_specs = mcph.prepare_flow_specifications(n_switch, common_configs.num_hosts_per_switch,
                                                      common_configs.n_default_flow,
                                                      common_configs.delay_budget_lb_ub, common_configs.bw_req_lb_ub)

        for afp in common_configs.affected_flow_per_list:
            etime_list = []
            for cnt in range(common_configs.n_trials_per_exp):
                # get computation time in ms
                print("==VARY_SWITCH_EXP== N_SW", n_switch, ", N_FLOWS:", common_configs.n_default_flow,
                      ", AFP:", afp, ", Trial #", cnt + 1)
                etime = compute_fr_sdn_runtime(nw_graph, flow_specs, afp)
                etime_list.append(etime)

            # print(etime_list)
            out_data_dict[n_switch][common_configs.n_default_flow][afp] = etime_list

    return out_data_dict


if __name__ == '__main__':

    exp_configs = CommonConfigs(n_default_sw=10,
                                n_default_flow=15,
                                num_switch_list=[5, 10, 15, 20],
                                num_hosts_per_switch=2,
                                link_delay=25,
                                link_bw=10,
                                number_of_flows_list=[3, 9, 15, 21, 27, 33],
                                delay_budget_lb_ub=(20000, 30000),
                                bw_req_lb_ub=(1, 1),
                                n_trial_per_exp=50,
                                affected_flow_per_list=[0.1, 0.25, 0.5, 0.75])

    # vary_flow_dict = run_varying_flow_exp(common_configs=exp_configs)
    # odc = FRSDNFlowOutClass(exp_configs, vary_flow_dict)
    # hf.write_object_to_file(odc, 'varying_flow_exp.pickle.gzip')

    vary_switch_dict = run_varying_switch_exp(common_configs=exp_configs)
    odc = FRSDNFlowOutClass(exp_configs, vary_switch_dict)
    hf.write_object_to_file(odc, 'varying_switch_exp.pickle.gzip')

    # print(vary_flow_dict)
    # print(vary_switch_dict)

    print("Script Finished!")
