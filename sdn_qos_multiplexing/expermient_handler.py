# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"

from config import *
import flow_config as fc
import delay_calculator as dc
import helper_functions as hf
import output_classes as oc
import topology_config as tc
import networkx as nx
import path_generator as pg
import copy
from collections import defaultdict



class SingleNodeExp:

    def __init__(self, n_flow_each_prio):
        self.flow_specs = []
        self.n_flow_each_prio = n_flow_each_prio

    def create_flow_set(self):
        """ creates flow --> input: number of flows in each priority level """

        # n_rt_flows = n_flow_each_prio * PARAMS.N_PRIO_LEVEL  # total number of RT flows in the systems

        # create flows
        flow_specs = []
        for i in range(PARAMS.N_PRIO_LEVEL):
            for j in range(self.n_flow_each_prio):
                f = fc.get_flow_specs(n_rt_flows=1, n_switch=2, n_host_per_switch=2, nw_diameter=1, prio=i)
                flow_specs.append(f[0])  # since f returns a list

        # update flow ids
        id = 0
        for f in flow_specs:
            f.id = id
            id += 1

        # print flow params
        # for f in flow_specs:
        #     print("ID:", f.id)
        #     print("Source:", f.src)
        #     print("Destination:", f.dst)
        #     print("Period:", f.period)
        #     print("E2E Deadline:", f.e2e_deadline)
        #     print("Prio:", f.prio)

        # save flow_specs
        self.flow_specs = copy.deepcopy(flow_specs)

    def reset_flow_set(self):
        self.flow_specs = []
        self.n_flow_each_prio = -1

    def get_single_node_delay(self, tag_flow_prio, indx=0):
        if tag_flow_prio >= PARAMS.N_PRIO_LEVEL or tag_flow_prio < 0:
            raise ValueError("Invalid priority range!")

        tag_flow_indx = tag_flow_prio*self.n_flow_each_prio + indx

        tag_flow = self.flow_specs[tag_flow_indx]

        qi = dc.get_fifo_delay(tag_flow_indx=tag_flow_indx, flow_specs=self.flow_specs,
                               same_sw_flow_set=self.flow_specs)
        ii = dc.get_priority_interference_delay(tag_flow_indx=tag_flow_indx, flow_specs=self.flow_specs,
                                                same_sw_flow_set=self.flow_specs)

        total_delay = qi + ii

        print("FIFO Delay:", qi)
        print("Priority interference Delay:", ii)
        print("Total delay:", total_delay)
        print("N Flows each queue", self.n_flow_each_prio)
        print("Tag flow period:", tag_flow.period, "Tag flow priority:", tag_flow.prio)
        print("====")

        return total_delay

    def run_single_node_experiment_by_flow_priority(self):

        delay_list = []

        for tag_flow_prio in PARAMS.TAG_FLOW_PRIO_LIST:
            delay = self.get_single_node_delay(tag_flow_prio)
            delay_list.append(delay)

        print("Delay list", delay_list)

        return delay_list


def run_single_node_experiment():
    """ Runs single node experiment with different flow priority and number of flows share same queue """

    all_delay_dict = defaultdict(lambda: defaultdict(dict))

    for n_flow_each_prio in PARAMS.N_FLOW_EACH_PRIO_LIST:
        print("\n#####")
        print("Running for #of flow each queue.. #", n_flow_each_prio)
        print("#####\n")
        for count in range(PARAMS.N_SINGLE_NODE_EXP_SAMPLE_RUN):
            print("====== Sample run.. #", count)
            exp_handler = SingleNodeExp(n_flow_each_prio=n_flow_each_prio)
            exp_handler.create_flow_set()
            delay_list = exp_handler.run_single_node_experiment_by_flow_priority()

            for i in range(len(delay_list)):
                all_delay_dict[n_flow_each_prio][PARAMS.TAG_FLOW_PRIO_LIST[i]][count] = delay_list[i]

    # print("Print dict...")
    # print(all_delay_dict)

    result = oc.ExportSingleNodeDelay(N_FLOW_EACH_PRIO_LIST=PARAMS.N_FLOW_EACH_PRIO_LIST,
                                      TAG_FLOW_PRIO_LIST=PARAMS.TAG_FLOW_PRIO_LIST,
                                      N_SINGLE_NODE_EXP_SAMPLE_RUN = PARAMS.N_SINGLE_NODE_EXP_SAMPLE_RUN,
                                      all_delay_dict=all_delay_dict)

    # saving results to pickle file
    print("--> Saving result to file...")
    hf.write_object_to_file(result, PARAMS.EXP_SINGLE_NODE_FILENAME)


def run_path_layout_experiment(topology, flow_specs, _debug=True):

    # print("=== Printing flow specs: ===")
    # for f in flow_specs:
    #     print("\nID:", f.id)
    #     print("Source:", f.src)
    #     print("Destination:", f.dst)
    #     print("Period:", f.period)
    #     print("E2E Deadline:", f.e2e_deadline)
    #     print("Packet Size:", f.pckt_size)
    #     print("Packet Processing time:", f.pkt_processing_time)
    #     print("Prio:", f.prio)

    path_gen_prop = pg.PathGenerator(topology=topology, flow_specs=flow_specs, _debug=_debug)

    path_gen_prop.run_path_layout_algo()

    # print("\n=== Path info for PROPOSED scheme ===")
    isSched = path_gen_prop.is_schedulable()

    if isSched:
        print("\n=== FLOW SET IS SCHEDULABLE BY PROPOSED SCHEME (MP:True) ====")
    else:
        print("\n===!!! Flow set is NOT SCHEDULABLE by Proposed scheme (MP:True) !!!====")

    return isSched


def run_path_layout_experiment_with_backup_path(topology, flow_specs, EXP_NAME, n_link_fail=1, _debug=True):

    # print("=== Printing flow specs: ===")
    # for f in flow_specs:
    #     print("\nID:", f.id)
    #     print("Source:", f.src)
    #     print("Destination:", f.dst)
    #     print("Period:", f.period)
    #     print("E2E Deadline:", f.e2e_deadline)
    #     print("Packet Size:", f.pckt_size)
    #     print("Packet Processing time:", f.pkt_processing_time)
    #     print("Prio:", f.prio)

    path_gen_backup = pg.PathGenerator(topology=topology, flow_specs=flow_specs, _debug=_debug)
    path_gen_backup.run_path_layout_algo()
    isSched = path_gen_backup.is_schedulable()

    if isSched:
        path_gen_backup.update_flow_and_topo_for_backup_path(n_link_fail, EXP_NAME)

        if len(path_gen_backup.affected_flow_list) == 0:
            print(" \n == No flow is affected by link failure == \n ")
            return True, True
        else:
            is_path_found = path_gen_backup.run_path_layout_algo_for_backup_path()
            if is_path_found:
                isBackupSched = path_gen_backup.is_schedulable()

                if isBackupSched:
                    print("\n=== FLOW set is SCHEDULABLE for *BOTH* primary & backup path ====")
                    return True, True
                else:
                    print("\n=== FLOW set is NOT SCHEDULABLE for backup path ====")
                    return True, False

    else:
        print("\n=== FLOW set is NOT SCHEDULABLE for primary path. Backup path routine is not called ====")
        return False, False


    # if _debug:
    #     for f in path_gen_backup.flow_specs:
    #         print("Flowid:", f.id, "Path:", f.path)


    # path_gen_backup = pg.PathGenerator(topology=topology, flow_specs=flow_specs, _debug=_debug)
    # path_gen_backup.update_flow_and_topo_for_backup_path(n_link_fail)
    #
    # try:
    #     path_gen_backup.run_path_layout_algo()
    #     isSched = path_gen_backup.is_schedulable()
    # except nx.exception.NetworkXNoPath:
    #     isSched = False
    #
    # if isSched:
    #     print("\n=== FLOW set is SCHEDULABLE with backup path ====")
    #     print("N_LINK_FAIL:", n_link_fail)
    # else:
    #     print("\n===!!! Flow set is NOT SCHEDULABLE with backup path !!!====")
    #     print("N_LINK_FAIL:", n_link_fail)
    #
    # return isSched


def run_schedulablity_experiment(n_flow_each_prio_list, base_e2e_beta_list):

    """ Run schedulability experiment """

    sched_count_dict = defaultdict(lambda: defaultdict(dict))
    n_switch = PARAMS.NUMBER_OF_SWITCHES
    n_host_per_switch = PARAMS.NUM_HOST_PER_SWITCH

    for n_flow_each_prio in n_flow_each_prio_list:
        for base_e2e_beta in base_e2e_beta_list:
            print("\nEXPERIMENT: #FLOW_EACH_PRIO:", n_flow_each_prio, "BASE_BETA:", base_e2e_beta)
            sched_count = 0
            for count in range(PARAMS.SCHED_EXP_EACH_TRIAL_COUNT):
                print("\n== EXPERIMENT: #FLOW_EACH_PRIO:", n_flow_each_prio,
                      "BASE_BETA:", base_e2e_beta, "Trial#", count+1, "==")

                # create the topology (you can also hard code it -- a networkx object, similar to RTSS paper)
                topology = tc.TopologyConfiguration(n_switch=n_switch,
                                                    n_host_per_switch=n_host_per_switch,
                                                    link_bw=PARAMS.LINK_BW,
                                                    prop_delay_min=PARAMS.PROP_DELAY_MIN,
                                                    prop_delay_max=PARAMS.PROP_DELAY_MAX)
                random_topo = topology.get_random_topology()  # returns a networkx object

                # specify flow specs
                nw_diameter = tc.get_topo_diameter(random_topo)  # get the diameter
                # print("Network diameter:", nw_diameter)

                flow_specs = fc.get_flow_specs_by_base_deadline_eq_per_queue(n_prio_level=PARAMS.N_PRIO_LEVEL,
                                                                             n_flow_each_prio=n_flow_each_prio,
                                                                             n_switch=n_switch,
                                                                             n_host_per_switch=n_host_per_switch,
                                                                             nw_diameter=nw_diameter,
                                                                             base_e2e_beta=base_e2e_beta)

                isSched = run_path_layout_experiment(random_topo, flow_specs)
                if isSched:
                    sched_count += 1

            sched_count_dict[n_flow_each_prio][base_e2e_beta] = sched_count  # save count

    result = oc.ExportSchedResult(NUMBER_OF_SWITCHES=n_switch,
                                  NUM_HOST_PER_SWITCH=n_host_per_switch,
                                  N_PRIO_LEVEL=PARAMS.N_PRIO_LEVEL,
                                  N_FLOW_EACH_PRIO_LIST=n_flow_each_prio_list,
                                  BASE_E2E_BETA_LIST=base_e2e_beta_list,
                                  SCHED_EXP_EACH_TRIAL_COUNT=PARAMS.SCHED_EXP_EACH_TRIAL_COUNT,
                                  sched_count_dict=sched_count_dict)

    # saving results to pickle file
    print("\n----> Saving schedulability result to file...")
    hf.write_object_to_file(result, PARAMS.EXP_SCHED_FILENAME)


def get_delay_by_by_flow_spec_with_path(topology, flow_specs):
    # this is for interference validation experiments

    path_gen = pg.PathGenerator(topology=topology, flow_specs=flow_specs)
    # prepare a dict to store all assigned paths
    allocated_paths = defaultdict(list)
    delay_list = []
    for f in flow_specs:
        flowid = f.id
        path = f.path
        cpd = pg.CandidatePathData(flowid=flowid, path=path)
        allocated_paths[flowid].append(cpd)
        total_delay = path_gen.get_total_delay_by_path(allocated_paths, f.id, f.path)
        delay_list.append(total_delay)

    return delay_list


def run_multiplxe_no_multiplex_schedulablity_experiment(n_flow_each_prio_list, base_e2e_beta_list, exp_name, output_filename):

    """ Run schedulability experiment (comparing with multiplexing and no multiplexing) """

    sched_count_dict = defaultdict(lambda: defaultdict(dict))
    n_switch = PARAMS.NUMBER_OF_SWITCHES
    n_host_per_switch = PARAMS.NUM_HOST_PER_SWITCH

    for n_flow_each_prio in n_flow_each_prio_list:
        for base_e2e_beta in base_e2e_beta_list:
            print("\nEXPERIMENT: #FLOW_EACH_PRIO:", n_flow_each_prio, "BASE_BETA:", base_e2e_beta)
            sched_count = 0
            for count in range(PARAMS.SCHED_MULTIPLEX_EXP_EACH_TRIAL_COUNT):
                if exp_name == PARAMS.EXP_WITHOUT_MULTIPLEX:
                    print("\n== EXPERIMENT (W/O Mul): #FLOW_EACH_PRIO:", n_flow_each_prio,
                          "BASE_BETA:", base_e2e_beta, "Trial#", count+1, "==")
                if exp_name == PARAMS.EXP_WITH_MULTIPLEX:
                    print("\n== EXPERIMENT (WITH Mul): #FLOW_EACH_PRIO:", n_flow_each_prio,
                          "BASE_BETA:", base_e2e_beta, "Trial#", count+1, "==")

                # create the topology (you can also hard code it -- a networkx object, similar to RTSS paper)
                topology = tc.TopologyConfiguration(n_switch=n_switch,
                                                    n_host_per_switch=n_host_per_switch,
                                                    link_bw=PARAMS.LINK_BW,
                                                    prop_delay_min=PARAMS.PROP_DELAY_MIN,
                                                    prop_delay_max=PARAMS.PROP_DELAY_MAX)
                random_topo = topology.get_random_topology()  # returns a networkx object

                # specify flow specs
                nw_diameter = tc.get_topo_diameter(random_topo)  # get the diameter
                # print("Network diameter:", nw_diameter)

                if exp_name == PARAMS.EXP_WITHOUT_MULTIPLEX:
                    flow_specs = fc.get_flow_specs_by_base_deadline_eq_per_queue(
                        n_prio_level=n_flow_each_prio * PARAMS.N_PRIO_LEVEL,
                        n_flow_each_prio=1,
                        n_switch=n_switch,
                        n_host_per_switch=n_host_per_switch,
                        nw_diameter=nw_diameter,
                        base_e2e_beta=base_e2e_beta)

                elif exp_name == PARAMS.EXP_WITH_MULTIPLEX:
                    flow_specs = fc.get_flow_specs_by_base_deadline_eq_per_queue(n_prio_level=PARAMS.N_PRIO_LEVEL,
                                                                                 n_flow_each_prio=n_flow_each_prio,
                                                                                 n_switch=n_switch,
                                                                                 n_host_per_switch=n_host_per_switch,
                                                                                 nw_diameter=nw_diameter,
                                                                                 base_e2e_beta=base_e2e_beta)
                else:
                    raise ValueError("Invalid Experiment Name")

                isSched = run_path_layout_experiment(random_topo, flow_specs, _debug=False)
                if isSched:
                    sched_count += 1

            sched_count_dict[n_flow_each_prio][base_e2e_beta] = sched_count  # save count

    result = oc.ExportSchedResult(NUMBER_OF_SWITCHES=n_switch,
                                  NUM_HOST_PER_SWITCH=n_host_per_switch,
                                  N_PRIO_LEVEL=PARAMS.N_PRIO_LEVEL,
                                  N_FLOW_EACH_PRIO_LIST=n_flow_each_prio_list,
                                  BASE_E2E_BETA_LIST=base_e2e_beta_list,
                                  SCHED_EXP_EACH_TRIAL_COUNT=PARAMS.SCHED_MULTIPLEX_EXP_EACH_TRIAL_COUNT,
                                  sched_count_dict=sched_count_dict)

    # saving results to pickle file
    print("\n----> Saving schedulability result to file...")
    hf.write_object_to_file(result, output_filename)


def run_primary_backup_path_schedulablity_experiment(n_flow_each_prio_list, base_e2e_beta_list, output_filename):

    """ Run schedulability experiment (comparing with multiplexing and no multiplexing) """

    sched_count_dict_primary = defaultdict(lambda: defaultdict(dict))
    sched_count_dict_bkp_hp = defaultdict(lambda: defaultdict(dict))
    sched_count_dict_bkp_all = defaultdict(lambda: defaultdict(dict))

    n_switch = PARAMS.NUMBER_OF_SWITCHES
    n_host_per_switch = PARAMS.NUM_HOST_PER_SWITCH

    for n_flow_each_prio in n_flow_each_prio_list:
        for base_e2e_beta in base_e2e_beta_list:
            print("\nEXPERIMENT: #FLOW_EACH_PRIO:", n_flow_each_prio, "BASE_BETA:", base_e2e_beta)
            sched_count_primary = 0  # no backup path
            sched_count_bkp_hp = 0  # for hp flow only
            sched_count_bkp_all = 0  # for all flows
            for count in range(PARAMS.SCHED_EXP_EACH_TRIAL_COUNT):

                print("\n== EXPERIMENT (W Bkp path): #FLOW_EACH_PRIO:", n_flow_each_prio,
                      "BASE_BETA:", base_e2e_beta, "Trial#", count+1, "==")

                # create the topology (you can also hard code it -- a networkx object, similar to RTSS paper)
                topology = tc.TopologyConfiguration(n_switch=n_switch,
                                                    n_host_per_switch=n_host_per_switch,
                                                    link_bw=PARAMS.LINK_BW,
                                                    prop_delay_min=PARAMS.PROP_DELAY_MIN,
                                                    prop_delay_max=PARAMS.PROP_DELAY_MAX)
                random_topo = topology.get_random_topology()  # returns a networkx object

                # specify flow specs
                nw_diameter = tc.get_topo_diameter(random_topo)  # get the diameter
                # print("Network diameter:", nw_diameter)

                flow_specs = fc.get_flow_specs_by_base_deadline_eq_per_queue(n_prio_level=PARAMS.N_PRIO_LEVEL,
                                                                             n_flow_each_prio=n_flow_each_prio,
                                                                             n_switch=n_switch,
                                                                             n_host_per_switch=n_host_per_switch,
                                                                             nw_diameter=nw_diameter,
                                                                             base_e2e_beta=base_e2e_beta)

                isSched_primary, isSched_bkp_hp = run_path_layout_experiment_with_backup_path(
                                                                            topology=random_topo, flow_specs=flow_specs,
                                                                            EXP_NAME=PARAMS.EXP_BACKUP_HP_FLOW,
                                                                            _debug=False)
                _, isSched_bkp_all = run_path_layout_experiment_with_backup_path(
                                                                            topology=random_topo, flow_specs=flow_specs,
                                                                            EXP_NAME=PARAMS.EXP_BACKUP_ALL_FLOW,
                                                                            _debug=False)

                if (isSched_primary is not None) and (isSched_bkp_hp is not None) and (isSched_bkp_all is not None):

                    if isSched_primary:
                        sched_count_primary += 1

                    if isSched_bkp_hp:
                        sched_count_bkp_hp += 1

                    if isSched_bkp_all:
                        sched_count_bkp_all += 1

            sched_count_dict_primary[n_flow_each_prio][base_e2e_beta] = sched_count_primary  # save count
            sched_count_dict_bkp_hp[n_flow_each_prio][base_e2e_beta] = sched_count_bkp_hp  # save count
            sched_count_dict_bkp_all[n_flow_each_prio][base_e2e_beta] = sched_count_bkp_all  # save count

    result = oc.ExportForwardBackupPathSchedResult(NUMBER_OF_SWITCHES=n_switch,
                                  NUM_HOST_PER_SWITCH=n_host_per_switch,
                                  N_PRIO_LEVEL=PARAMS.N_PRIO_LEVEL,
                                  N_FLOW_EACH_PRIO_LIST=n_flow_each_prio_list,
                                  BASE_E2E_BETA_LIST=base_e2e_beta_list,
                                  SCHED_EXP_EACH_TRIAL_COUNT=PARAMS.SCHED_EXP_EACH_TRIAL_COUNT,
                                  sched_count_dict_primary=sched_count_dict_primary,
                                  sched_count_dict_bkp_hp=sched_count_dict_bkp_hp,
                                  sched_count_dict_bkp_all=sched_count_dict_bkp_all)

    # saving results to pickle file
    print("\n----> Saving schedulability result to file...")
    hf.write_object_to_file(result, output_filename)


def run_non_mp_pri_back_path_schedulablity_experiment(n_flow_each_prio_list, base_e2e_beta_list, output_filename):

    """ Run schedulability experiment (comparing with multiplexing (w, w/o backup path) and no multiplexing) """

    sched_count_dict_non_mp = defaultdict(lambda: defaultdict(dict))
    sched_count_dict_primary = defaultdict(lambda: defaultdict(dict))
    sched_count_dict_bkp_hp = defaultdict(lambda: defaultdict(dict))
    sched_count_dict_bkp_all = defaultdict(lambda: defaultdict(dict))

    n_switch = PARAMS.NUMBER_OF_SWITCHES
    n_host_per_switch = PARAMS.NUM_HOST_PER_SWITCH

    for n_flow_each_prio in n_flow_each_prio_list:
        for base_e2e_beta in base_e2e_beta_list:
            print("\nEXPERIMENT: #FLOW_EACH_PRIO:", n_flow_each_prio, "BASE_BETA:", base_e2e_beta)

            sched_count_non_mp = 0  # no multiplexing (rtss17)
            sched_count_primary = 0  # no backup path
            sched_count_bkp_hp = 0  # for hp flow only
            sched_count_bkp_all = 0  # for all flows
            for count in range(PARAMS.SCHED_EXP_EACH_TRIAL_COUNT):

                print("\n== EXPERIMENT (W/O MP and W Bkp path): #FLOW_EACH_PRIO:", n_flow_each_prio,
                      "BASE_BETA:", base_e2e_beta, "Trial#", count+1, "==")

                # create the topology (you can also hard code it -- a networkx object, similar to RTSS paper)
                topology = tc.TopologyConfiguration(n_switch=n_switch,
                                                    n_host_per_switch=n_host_per_switch,
                                                    link_bw=PARAMS.LINK_BW,
                                                    prop_delay_min=PARAMS.PROP_DELAY_MIN,
                                                    prop_delay_max=PARAMS.PROP_DELAY_MAX)
                random_topo = topology.get_random_topology()  # returns a networkx object

                # specify flow specs
                nw_diameter = tc.get_topo_diameter(random_topo)  # get the diameter
                # print("Network diameter:", nw_diameter)

                flow_specs_non_multiplex = fc.get_flow_specs_by_base_deadline_eq_per_queue(
                    n_prio_level=min(PARAMS.NON_MULTIPLEX_N_QUEUE, n_flow_each_prio * PARAMS.N_PRIO_LEVEL),
                    n_flow_each_prio=1,
                    n_switch=n_switch,
                    n_host_per_switch=n_host_per_switch,
                    nw_diameter=nw_diameter,
                    base_e2e_beta=base_e2e_beta)

                flow_specs = fc.get_flow_specs_by_base_deadline_eq_per_queue(n_prio_level=PARAMS.N_PRIO_LEVEL,
                                                                             n_flow_each_prio=n_flow_each_prio,
                                                                             n_switch=n_switch,
                                                                             n_host_per_switch=n_host_per_switch,
                                                                             nw_diameter=nw_diameter,
                                                                             base_e2e_beta=base_e2e_beta)

                # run non-multiplexing case (RTSS17 paper)

                # we can't schedule flows more than # of queue
                if n_flow_each_prio * PARAMS.N_PRIO_LEVEL > PARAMS.NON_MULTIPLEX_N_QUEUE:
                    isSched_non_mp = False
                else:
                    isSched_non_mp = run_path_layout_experiment(topology=random_topo, flow_specs=flow_specs_non_multiplex, _debug=False)

                # run with multiplexing and backup path experiment
                isSched_primary, isSched_bkp_hp = run_path_layout_experiment_with_backup_path(
                                                                            topology=random_topo, flow_specs=flow_specs,
                                                                            EXP_NAME=PARAMS.EXP_BACKUP_HP_FLOW,
                                                                            _debug=False)
                _, isSched_bkp_all = run_path_layout_experiment_with_backup_path(
                                                                            topology=random_topo, flow_specs=flow_specs,
                                                                            EXP_NAME=PARAMS.EXP_BACKUP_ALL_FLOW,
                                                                            _debug=False)

                if isSched_non_mp is not None:
                    if isSched_non_mp:
                        sched_count_non_mp += 1

                if (isSched_primary is not None) and (isSched_bkp_hp is not None) and (isSched_bkp_all is not None):

                    if isSched_primary:
                        sched_count_primary += 1

                    if isSched_bkp_hp:
                        sched_count_bkp_hp += 1

                    if isSched_bkp_all:
                        sched_count_bkp_all += 1

            sched_count_dict_non_mp[n_flow_each_prio][base_e2e_beta] = sched_count_non_mp  # save count
            sched_count_dict_primary[n_flow_each_prio][base_e2e_beta] = sched_count_primary  # save count
            sched_count_dict_bkp_hp[n_flow_each_prio][base_e2e_beta] = sched_count_bkp_hp  # save count
            sched_count_dict_bkp_all[n_flow_each_prio][base_e2e_beta] = sched_count_bkp_all  # save count

    result = oc.ExportNonMultiplexForwardBackupPathSchedResult(NUMBER_OF_SWITCHES=n_switch,
                                                               NUM_HOST_PER_SWITCH=n_host_per_switch,
                                                               N_PRIO_LEVEL=PARAMS.N_PRIO_LEVEL,
                                                               N_FLOW_EACH_PRIO_LIST=n_flow_each_prio_list,
                                                               BASE_E2E_BETA_LIST=base_e2e_beta_list,
                                                               SCHED_EXP_EACH_TRIAL_COUNT=PARAMS.SCHED_EXP_EACH_TRIAL_COUNT,
                                                               sched_count_dict_non_mp=sched_count_dict_non_mp,
                                                               sched_count_dict_primary=sched_count_dict_primary,
                                                               sched_count_dict_bkp_hp=sched_count_dict_bkp_hp,
                                                               sched_count_dict_bkp_all=sched_count_dict_bkp_all)

    # saving results to pickle file
    print("\n----> Saving schedulability result to file...")
    hf.write_object_to_file(result, output_filename)
