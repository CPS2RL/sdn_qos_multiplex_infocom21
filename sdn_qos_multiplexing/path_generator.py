# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"

import networkx as nx
import copy
from collections import defaultdict
import delay_calculator as dc
import random
import flow_config as fc
from config import *


class CandidatePathData():
    """ Save candidate paths data """
    def __init__(self, flowid, path, intf_indx=0, visited=False):
        self.flowid = flowid
        self.path = path
        self.intf_indx = intf_indx
        self.visited = visited


def get_candidate_path_dict_size(candidate_paths):
    count = 0
    for flowid, candidate_path_data in candidate_paths.items():
        for cpd in candidate_path_data:
            count += 1

    return count


class PathGenerator:
    """ Helper class for path generator"""

    def __init__(self, topology, flow_specs, _debug=True):
        self.topology = copy.deepcopy(topology)  # create own copy
        self.bkp_topology = None  # None for now, this is for backup path topology
        self.failed_edge_list = None  # update later with the failed edge(s)
        self.flow_specs = copy.deepcopy(flow_specs)
        self.affected_flow_list = None  # will be updated later (for the flows we provide backup)
        self.DEBUG = _debug  # if true print output

    def get_shortest_path_by_flow_id(self, flowid):

        # some error checking
        flow = self.get_flow_by_id(flowid)
        if flow is None:
            print("Invalid flow ID!!")
            return None

        src = flow.src
        dst = flow.dst
        path = nx.shortest_path(self.topology, source=src, target=dst)

        return path

    def get_flow_by_id(self, flowid):

        flow = None
        for f in self.flow_specs:
            if f.id == flowid:
                flow = copy.deepcopy(f)
                break

        return flow

    def get_flow_idex_by_id(self, flowid):

        indx = None
        for i in range(len(self.flow_specs)):
            if flowid == i:
                indx = i
                break

        return indx

    def get_all_simple_paths_by_flow_id(self, flowid):

        # some error checking
        flow = self.get_flow_by_id(flowid)
        if flow is None:
            print("Invalid flow ID!!")
            return None

        src = flow.src
        dst = flow.dst
        paths = nx.all_simple_paths(self.topology, source=src, target=dst)
        paths = list(paths)  # convert generator to a list

        return paths

    def get_all_simple_paths_by_src_dst(self, src, dst):

        paths = nx.all_simple_paths(self.topology, source=src, target=dst)
        paths = list(paths)  # convert generator to a list

        return paths

    def get_all_simple_paths_by_src_dst_for_backup_path(self, src, dst):

        paths = nx.all_simple_paths(self.bkp_topology, source=src, target=dst)
        paths = list(paths)  # convert generator to a list

        return paths

    def get_feasible_simple_paths_by_flow_id(self, flowid):

        # some error checking
        flow = self.get_flow_by_id(flowid)
        if flow is None:
            print("Invalid flow ID!!")
            return None

        src = flow.src
        dst = flow.dst

        if flow.flowtype == 'forward':
            paths = self.get_all_simple_paths_by_src_dst(src, dst)
        else:
            paths = self.get_all_simple_paths_by_src_dst_for_backup_path(src, dst)

        if paths is None:
            return None

        feasible_paths = []
        for path in paths:
            pdelay_sum = 0
            for i in range(len(path)-1):
                e0 = path[i]
                e1 = path[i+1]

                if flow.flowtype == 'forward':
                    pdelay = self.topology[e0][e1]['prop_delay']
                else:
                    pdelay = self.bkp_topology[e0][e1]['prop_delay']

                pdelay_sum += pdelay

            if pdelay_sum <= flow.e2e_deadline:
                p = copy.deepcopy(path)  # for safety copy to a new object
                feasible_paths.append(p)

        return feasible_paths

    def get_all_candidate_paths(self):

        """Returns all possible candidate paths (for all flows)
        A dictionary. Key: flowid, Value: the class instance CandidatePathData """

        candidate_paths = defaultdict(list)
        for flow in self.flow_specs:
            flowid = flow.id
            simplepaths = self.get_feasible_simple_paths_by_flow_id(flowid)
            # print("flowid:", flowid, "#of simple paths", len(simplepaths))

            # in case no simple path found
            if len(simplepaths) == 0:

                if flow.flowtype == 'forward':
                    simplepaths = nx.all_shortest_paths(self.topology, source=flow.src, target=flow.dst)
                else:
                    simplepaths = nx.all_shortest_paths(self.bkp_topology, source=flow.src, target=flow.dst)

                simplepaths = list(simplepaths)
                # print("Get shortest paths. Flowid:", flowid, "length:", len(simplepaths))
                # print("simplepaths", simplepaths)

            for p in simplepaths:
                cpd = CandidatePathData(flowid=flowid, path=p)
                candidate_paths[flowid].append(cpd)

        # print("Printing Candidate paths:")
        # self.print_candidate_paths(candidate_paths)
        return candidate_paths

    def get_all_candidate_paths_for_affected_flows(self):

        """Returns all possible candidate paths (for the affected flows)
        A dictionary. Key: flowid, Value: the class instance CandidatePathData """

        candidate_paths = defaultdict(list)
        for flow in self.flow_specs:
            if flow.flowtype == 'backup':
                flowid = flow.id
                simplepaths = self.get_feasible_simple_paths_by_flow_id(flowid)
                # print("flowid:", flowid, "#of simple paths", len(simplepaths))

                # in case no simple path found
                if len(simplepaths) == 0:

                    simplepaths = nx.all_shortest_paths(self.bkp_topology, source=flow.src, target=flow.dst)

                    simplepaths = list(simplepaths)
                    # print("Get shortest paths. Flowid:", flowid, "length:", len(simplepaths))
                    # print("simplepaths", simplepaths)

                for p in simplepaths:
                    cpd = CandidatePathData(flowid=flowid, path=p)
                    candidate_paths[flowid].append(cpd)

        # print("Printing Candidate paths:")
        # self.print_candidate_paths(candidate_paths)
        return candidate_paths

    def get_flow_list_by_switch_name(self, candidate_paths, sw_name):
        """ Returns the set of flows using the same switch for a given set of candidate paths"""

        flowid_list = []
        flow_list = []

        # get flowids that routed through the switch
        for flowid, candidate_path_data in candidate_paths.items():
            for cpd in candidate_path_data:
                path = cpd.path
                for node in path:
                    if node == sw_name:
                        flowid_list.append(flowid)

        # remove duplicates
        flowid_list = list(set(flowid_list))

        # create flow list from flow ids

        for fid in flowid_list:
            flow = self.get_flow_by_id(flowid=fid)
            flow_list.append(flow)

        return flow_list

    def get_primary_flowlist_by_switch_name(self, sw_name):
        """ Returns the (primary) flows routed through the switch """

        flow_list = []
        for f in self.flow_specs:
            # some error checking
            if f.flowtype == 'forward':
                if not f.path:
                    print("== Not all flow get path assigned! Flow set is unschedulable! ==")
                    raise Exception("Something wrong in primary flow path assignment")

                for node in f.path:
                    if node == sw_name:
                        flow_list.append(copy.deepcopy(f))
                        # print("Flowid", f.id, "path:", f.path)
                        # print("Sw:", sw_name, "found for path of Flowid", f.id)
                        break

        return flow_list

    def get_total_delay_by_path(self, candidate_paths, flowid, path):

        # print("Flowid:", flowid, "Given Path: ", path)
        path_delay = 0

        tag_flow_indx = self.get_flow_idex_by_id(flowid=flowid)  # no error checking (assuming flowid is correct)

        for node in path:
            # this is a switch
            if 's' in node:
                same_sw_flow_set = self.get_flow_list_by_switch_name(candidate_paths=candidate_paths,
                                                                     sw_name=node)

                # FIFO delay
                # qi = dc.get_fifo_delay_by_pck_size(tag_flow_indx=tag_flow_indx, flow_specs=self.flow_specs,
                #                                     same_sw_flow_set=same_sw_flow_set)
                qi = dc.get_fifo_delay(tag_flow_indx=tag_flow_indx, flow_specs=self.flow_specs,
                                       same_sw_flow_set=same_sw_flow_set)

                # Priority interference delay
                ii = dc.get_priority_interference_delay(tag_flow_indx=tag_flow_indx, flow_specs=self.flow_specs,
                                                        same_sw_flow_set=same_sw_flow_set)

                # print("FIFO delay:", qi)
                # print("Intf delay:", ii)

                delay = qi + ii
                path_delay += delay

        # now add propagation delay
        prop_delay = self.get_prop_delay_by_path(path)

        path_delay = path_delay + prop_delay

        return path_delay

    def get_total_delay_by_path_for_backup(self, candidate_paths, flowid, path):

        # print("Flowid:", flowid, "Given Path: ", path)
        path_delay = 0

        tag_flow_indx = self.get_flow_idex_by_id(flowid=flowid)  # no error checking (assuming flowid is correct)

        for node in path:
            # this is a switch
            if 's' in node:
                same_sw_flow_set = self.get_flow_list_by_switch_name(candidate_paths=candidate_paths,
                                                                     sw_name=node)

                same_sw_primary_flow_set = self.get_primary_flowlist_by_switch_name(sw_name=node)

                for prflow in same_sw_primary_flow_set:
                    same_sw_flow_set.append(copy.deepcopy(prflow))



                # FIFO delay
                # qi = dc.get_fifo_delay_by_pck_size(tag_flow_indx=tag_flow_indx, flow_specs=self.flow_specs,
                #                                     same_sw_flow_set=same_sw_flow_set)
                qi = dc.get_fifo_delay(tag_flow_indx=tag_flow_indx, flow_specs=self.flow_specs,
                                       same_sw_flow_set=same_sw_flow_set)

                # Priority interference delay TODO
                ii = dc.get_priority_interference_delay(tag_flow_indx=tag_flow_indx, flow_specs=self.flow_specs,
                                                        same_sw_flow_set=same_sw_flow_set)

                # print("FIFO delay:", qi)
                # print("Intf delay:", ii)

                delay = qi + ii
                path_delay += delay

        # now add propagation delay
        prop_delay = self.get_prop_delay_by_path(path)

        path_delay = path_delay + prop_delay

        return path_delay

    def get_prop_delay_by_path(self, path):

        prop_delay = 0
        for i in range(len(path) - 1):
            e0 = path[i]
            e1 = path[i + 1]

            # if this is a switch-switch link
            if 's' in e0 and 's' in e1:
                pdelay = self.topology[e0][e1]['prop_delay']
                prop_delay += pdelay

        return prop_delay

    def get_flow_list_by_edge(self, candidate_paths, node0, node1):
        """ Returns the set of flows using the same switch for a given set of candidate paths"""

        flowid_list = []
        flow_list = []

        # get flowids that routed through the link (node0, node1)
        for flowid, candidate_path_data in candidate_paths.items():
            for cpd in candidate_path_data:
                path = cpd.path
                for i in range(len(path) - 1):
                    e0 = path[i]
                    e1 = path[i + 1]

                    if e0 == node0 and e1 == node1:
                        flowid_list.append(flowid)
                        break

        # remove duplicates
        flowid_list = list(set(flowid_list))

        # create flow list from flow ids

        for fid in flowid_list:
            flow = self.get_flow_by_id(flowid=fid)
            flow_list.append(flow)

        return flow_list

    def get_residual_bw_by_edge(self, candidate_paths, node0, node1):
        link_bw = self.topology[node0][node1]['link_bw']
        flow_list = self.get_flow_list_by_edge(candidate_paths, node0, node1)
        sum_bw_req = 0
        for f in flow_list:
            sum_bw_req += f.bw_req

        res_bw = link_bw - sum_bw_req

        return res_bw

    def get_bw_utilization_by_path(self, candidate_paths, flowid, path):

        tag_flow = self.get_flow_by_id(flowid=flowid)

        bw_util = 0

        for i in range(len(path) - 1):
            e0 = path[i]
            e1 = path[i + 1]

            # if this is a switch-switch link
            if 's' in e0 and 's' in e1:
                res_bw = self.get_residual_bw_by_edge(candidate_paths, e0, e1)

                if res_bw == 0:  # if no residual BW, set to large number
                    bw_util = PARAMS.LARGE_NUMBER
                else:
                    # util = tag_flow.pckt_size/res_bw
                    util = tag_flow.bw_req / res_bw
                    bw_util += util  # sum-up for the path

        # if negative, set to a large value
        if bw_util < 0:
            bw_util = PARAMS.LARGE_NUMBER

        return bw_util

    def get_intf_indx_by_path(self, candidate_paths, flowid, path):

        # print("Flowid:", flowid, "Given Path: ", path)

        tag_flow = self.get_flow_by_id(flowid=flowid)  # no error checking (assuming flowid is correct)

        total_delay = self.get_total_delay_by_path(candidate_paths, flowid, path)
        prop_delay = self.get_prop_delay_by_path(path)
        queuing_delay = total_delay - prop_delay

        bw_util = self.get_bw_utilization_by_path(candidate_paths, flowid, path)

        # intf_indx = tag_flow.e2e_deadline - prop_delay + queuing_delay + bw_util
        intf_indx = total_delay - tag_flow.e2e_deadline + bw_util

        return intf_indx

    def get_intf_indx_by_path_for_backup(self, candidate_paths, flowid, path):

        # print("Flowid:", flowid, "Given Path: ", path)

        tag_flow = self.get_flow_by_id(flowid=flowid)  # no error checking (assuming flowid is correct)

        total_delay = self.get_total_delay_by_path_for_backup(candidate_paths, flowid, path)
        # prop_delay = self.get_prop_delay_by_path(path)
        # queuing_delay = total_delay - prop_delay

        bw_util = self.get_bw_utilization_by_path(candidate_paths, flowid, path)

        # intf_indx = tag_flow.e2e_deadline - prop_delay + queuing_delay + bw_util
        intf_indx = total_delay - tag_flow.e2e_deadline + bw_util

        return intf_indx

    def terminate_loop(self, candidate_paths):
        """ The function returns whether we can terminate the loop in path generation """

        for flowid, candidate_path_data in candidate_paths.items():
            for cpd in candidate_path_data:
                if not cpd.visited:
                    return False

        # for flowid, candidate_path_data in candidate_paths.items():
        #     if len(candidate_path_data) > 1:
        #         return False
        return True

    def print_candidate_paths(self, candidate_paths):

        cnt = 0
        for flow in self.flow_specs:
            flowid = flow.id
            cpathdata = candidate_paths[flowid]

            for cpd in cpathdata:
                path = cpd.path
                print("Entry", cnt, "## Flowid", flowid,  "Path", path, "II:", cpd.intf_indx, "visited:", cpd.visited)
                cnt +=1

    def update_candiate_paths(self, candidate_paths):
        """ Update candidate path dictionary:
            Deletes the path with max II,
            set 'path' (in 'Flow' variable) if the path is the only available path for the flow
            Update 'visited' flag"""

        max_ii = -1 * PARAMS.LARGE_NUMBER
        max_fid = -1
        max_cpd = None
        for flowid, candidate_path_data in candidate_paths.items():
            for cpd in candidate_path_data:
                if not cpd.visited:
                    path = cpd.path
                    intf_indx = self.get_intf_indx_by_path(candidate_paths=candidate_paths, flowid=flowid, path=path)
                    cpd.intf_indx = intf_indx  # update intf_indx
                    # print("Flow id:", flowid, "II Index:", intf_indx, "visited", cpd.visited)
                    if intf_indx > max_ii:
                        max_ii = intf_indx
                        max_fid = flowid
                        max_cpd = cpd

        # print("\n Before: ===")
        # self.print_candidate_paths(candidate_paths)

        if max_fid >= 0:
            if self.DEBUG:
                print("MaxII flowid:", max_fid, "Max II:", max_ii, "MaxII path:", max_cpd.path)

            cpdlist = candidate_paths[max_fid]

            # the flow has more than one candidate path
            if len(cpdlist) > 1:
                # remove the path from list
                candidate_paths[max_fid].remove(max_cpd)

            elif len(cpdlist) == 1:
                # this is the only path for the flow
                # candidate_paths[max_fid].remove(max_cpd)
                max_cpd.visited = True
                flowindx = self.get_flow_idex_by_id(max_fid)
                self.flow_specs[flowindx].path = copy.deepcopy(max_cpd.path)

                if self.DEBUG:
                    print("Got last candidate path for Flow#", max_fid, ":: set the path variable and update residual BW.")

                # update residual bandwidth
                for i in range(len(max_cpd.path) - 1):
                    e0 = max_cpd.path[i]
                    e1 = max_cpd.path[i + 1]

                    # if this is a switch-switch link
                    if 's' in e0 and 's' in e1:
                        self.topology[e0][e1]['link_bw'] -= self.flow_specs[flowindx].bw_req

            # print("\n After: ===")
            # self.print_candidate_paths(candidate_paths)

    def update_candiate_paths_for_backup(self, candidate_paths):
        """ Update candidate path dictionary:
            Deletes the path with max II,
            set 'path' (in 'Flow' variable) if the path is the only available path for the flow
            Update 'visited' flag"""

        max_ii = -1 * PARAMS.LARGE_NUMBER
        max_fid = -1
        max_cpd = None
        for flowid, candidate_path_data in candidate_paths.items():
            for cpd in candidate_path_data:
                if not cpd.visited:
                    path = cpd.path
                    intf_indx = self.get_intf_indx_by_path_for_backup(candidate_paths=candidate_paths, flowid=flowid, path=path)
                    cpd.intf_indx = intf_indx  # update intf_indx
                    # print("Flow id:", flowid, "II Index:", intf_indx, "visited", cpd.visited)
                    if intf_indx > max_ii:
                        max_ii = intf_indx
                        max_fid = flowid
                        max_cpd = cpd

        # print("\n Before: ===")
        # self.print_candidate_paths(candidate_paths)

        if max_fid >= 0:
            if self.DEBUG:
                print("MaxII flowid:", max_fid, "Max II:", max_ii, "MaxII path:", max_cpd.path)

            cpdlist = candidate_paths[max_fid]

            # the flow has more than one candidate path
            if len(cpdlist) > 1:
                # remove the path from list
                candidate_paths[max_fid].remove(max_cpd)

            elif len(cpdlist) == 1:
                # this is the only path for the flow
                # candidate_paths[max_fid].remove(max_cpd)
                max_cpd.visited = True
                flowindx = self.get_flow_idex_by_id(max_fid)
                self.flow_specs[flowindx].path = copy.deepcopy(max_cpd.path)

                if self.DEBUG:
                    print("Backup path :: Got last candidate path for Flow#", max_fid, ":: set the path variable and update residual BW.")

                # update residual bandwidth
                for i in range(len(max_cpd.path) - 1):
                    e0 = max_cpd.path[i]
                    e1 = max_cpd.path[i + 1]

                    # if this is a switch-switch link
                    if 's' in e0 and 's' in e1:
                        self.topology[e0][e1]['link_bw'] -= self.flow_specs[flowindx].bw_req

            # print("\n After: ===")
            # self.print_candidate_paths(candidate_paths)

    def get_max_flowid(self):

        maxid = -1
        for f in self.flow_specs:
            if f.id > maxid:
                maxid = f.id

        return maxid

    def update_topo_for_backup_path(self, n_link_fail):

        sw_sw_link_list = []

        edgelist = list(self.topology.edges_iter(data=True))

        for e in edgelist:
            if 's' in e[0] and 's' in e[1]:
                sw_sw_link_list.append(copy.deepcopy(e))

        # print(sw_sw_link_list)

        if n_link_fail >= len(sw_sw_link_list):
            raise Exception("Number of failed link is greater than all switch-switch links. Not implemented this case!")

        rnd_link_indx_list = random.sample(range(len(sw_sw_link_list)), n_link_fail)

        self.bkp_topology = copy.deepcopy(self.topology)

        self.failed_edge_list = []
        for rindx in rnd_link_indx_list:
            e_rem = sw_sw_link_list[rindx]
            self.bkp_topology.remove_edge(*e_rem[:2])
            self.failed_edge_list.append(copy.deepcopy(e_rem))  # also add that link
            print("== Falied edge: (", e_rem[0], e_rem[1], ") ==")

        # print("== printing original topo == ")
        # print(self.topology.edges(data=True))
        # print("== printing backup topo == ")
        # print(self.bkp_topology.edges(data=True))

    def update_flow_and_topo_for_backup_path(self, n_link_fail, EXP_NAME):

        if n_link_fail <= 0:
            raise Exception("Number of failed link should be greater than 0.")

        self.update_topo_for_backup_path(n_link_fail=n_link_fail)
        self.update_flow_specs_for_backup_path(EXP_NAME)

    # return the index in the path, if the falied edge is on the path or -1 otherwise
    def check_failed_link_in_flow_path(self, path, failed_e0, failed_e1):

        # print("Path:", path, "Failed0:", failed_e0, "Failed1:", failed_e1)
        for nodeindx in range(len(path)-1):
            if (path[nodeindx] == failed_e0 and path[nodeindx+1] == failed_e1) or \
                    (path[nodeindx] == failed_e1 and path[nodeindx+1] == failed_e0):
                # print("Failed edge found in the path")
                return nodeindx

        return -1

    def update_backup_path_residual_bw(self, flow, path):
        """ Update the residual bw of the backup path toplogy """

        for nodeindx in range(len(path)-1):
            e0 = path[nodeindx]
            e1 = path[nodeindx+1]
            if 's' in e0 and 's' in e1:
                if self.bkp_topology.has_edge(e0, e1):
                    self.bkp_topology[e0][e1]['link_bw'] -= flow.bw_req

    def update_flow_specs_for_backup_path(self, EXP_NAME):

        fid_list = []

        # saves all flow id for which we are calculating backup
        if EXP_NAME == PARAMS.EXP_BACKUP_ALL_FLOW:
            for f in self.flow_specs:
                if f.flowtype == "forward":
                    fid_list.append(f.id)

        elif EXP_NAME == PARAMS.EXP_BACKUP_HP_FLOW:
            for f in self.flow_specs:
                if f.flowtype == "forward" and f.prio == 0:
                    fid_list.append(f.id)
        else:
            raise Exception("Invalid Experiment Name for Backup Path!!")


        # print(self.failed_edge_list)

        fail_el = self.failed_edge_list[0]  # at present we only consider a single link fail

        # fail_el = ['s2', 's4']  # temp TODO: remove

        maxid = self.get_max_flowid()
        # critical_flow_list = []
        self.affected_flow_list = []
        cflowid = maxid + 1
        for f in self.flow_specs:
            # highest prio (critical flows)
            if f.id in fid_list:
                is_affected_path_idx = self.check_failed_link_in_flow_path(path=f.path, failed_e0=fail_el[0], failed_e1=fail_el[1])

                if is_affected_path_idx >= 0:

                    partial_path = copy.deepcopy(f.path[0:is_affected_path_idx+1])
                    consumed_delay = self.get_consumed_delay_by_partial_path(flowid=f.id, partial_path=partial_path)

                    newsrc = partial_path[len(partial_path)-1]  # last node in partial path will be source

                    newflow = fc.Flow(id=cflowid, src=newsrc, dst=f.dst, period=f.period, e2e_deadline=f.e2e_deadline-consumed_delay,
                                 pckt_size=f.pckt_size, pkt_processing_time=f.pkt_processing_time,
                                 prio=f.prio, flowtype="backup")

                    # self.flow_specs.append(copy.deepcopy(newflow))
                    self.affected_flow_list.append(copy.deepcopy(newflow))
                    cflowid += 1  # increase id counter

                    # update residual BW
                    self.update_backup_path_residual_bw(flow=f, path=partial_path)

                    if self.DEBUG:
                        print("ID:", f.id, "Path:", f.path, "Failed Edge: (", fail_el[0], ",", fail_el[1], ")")
                        print("Failed edge found in the path")
                        print("Partial path:", partial_path)
                        print("Consumed delay:", consumed_delay)
                else:
                    # update residual BW
                    self.update_backup_path_residual_bw(flow=f, path=f.path)

            else:
                # update residual BW
                self.update_backup_path_residual_bw(flow=f, path=f.path)


        for indx in range(len(self.affected_flow_list)):
            cflow = self.affected_flow_list[indx]
            # cflow.id = maxid + indx + 1
            # cflow.flowtype = "backup"
            self.flow_specs.append(copy.deepcopy(cflow))

        # if len(self.affected_flow_list) == 0:
        #     print("No flow is affected by link failure")


        #
        # print("=== Printing flow specs: ===")
        # for f in self.flow_specs:
        #     print("\nID:", f.id)
        #     print("Source:", f.src)
        #     print("Destination:", f.dst)
        #     print("Period:", f.period)
        #     print("E2E Deadline:", f.e2e_deadline)
        #     print("Packet Size:", f.pckt_size)
        #     print("Packet Processing time:", f.pkt_processing_time)
        #     print("Prio:", f.prio)
        #     print("Type:", f.flowtype)

        # print("== printing original topo == ")
        # print(self.topology.edges(data=True))
        # print("== printing backup topo == ")
        # print(self.bkp_topology.edges(data=True))

    def run_path_layout_algo(self):
        """ This is the main algorithm that generates path"""

        candidate_paths = self.get_all_candidate_paths()

        isRunnable = self.check_all_flow_has_candidate_path(candidate_paths)
        if not isRunnable:
            raise Exception("Not all flow gets candidate path -- algorithm will not work. Mark flowset UNSCHEDULABLE.")
        else:
            print("\nCandidate path generation complete. All flow has at least one candidate path.")

        all_cand_dict_size = get_candidate_path_dict_size(candidate_paths)
        print("# of Candidate paths:", all_cand_dict_size)

        if self.DEBUG:
            print("Running path layout algorithm (pruning path with max interference) ...")

        count = 0
        while True:
            if self.DEBUG:
                print("\n==== Iteration #", count, "====")

            count += 1
            self.update_candiate_paths(candidate_paths)

            # print("Printing candidate paths...")
            # self.print_candidate_paths(candidate_paths)

            if self.terminate_loop(candidate_paths):
                print("Done with path layout!! Terminating loop...")
                # print("Printing candidate paths...")
                # self.print_candidate_paths(candidate_paths)
                break

            if count > all_cand_dict_size+1:
                print("!!! Loop running more than #of candidate paths. Terminating... [Flow set is not schedulable] !!!")

    def run_path_layout_algo_for_backup_path(self):
        """ This is the main algorithm that generates backup path
            Returns False if unable to find any path """

        try:
            candidate_paths = self.get_all_candidate_paths_for_affected_flows()
        except nx.exception.NetworkXNoPath:
            print("\nNo candidate path found for Backup path flows. Flowset is UNSCHEDULABLE!")
            return False


        # candidate_paths = self.get_all_candidate_paths_for_affected_flows()
        # print("candidate path:")
        #
        # self.print_candidate_paths(candidate_paths=candidate_paths)

        isRunnable = self.check_all_affected_flow_has_candidate_path(candidate_paths)
        if not isRunnable:
            raise Exception("Not all Affected flow gets candidate path -- algorithm will not work. "
                            "Mark flowset UNSCHEDULABLE.")
        else:
            print("\nBACKUP PATH Candidate path generation complete. All affected flow has at least one candidate path.")

        all_cand_dict_size = get_candidate_path_dict_size(candidate_paths)
        print("# of Candidate paths:", all_cand_dict_size)

        if self.DEBUG:
            print("Running path layout algorithm :: BACKUP (pruning path with max interference) ...")

        count = 0
        while True:
            if self.DEBUG:
                print("\n==== Iteration #", count, "====")

            count += 1
            self.update_candiate_paths_for_backup(candidate_paths)

            # print("Printing candidate paths...")
            # self.print_candidate_paths(candidate_paths)

            if self.terminate_loop(candidate_paths):
                print("Done with path layout!! Terminating loop...")
                # print("Printing candidate paths...")
                # self.print_candidate_paths(candidate_paths)
                break

            if count > all_cand_dict_size+1:
                print("!!! Loop running more than #of candidate paths. Terminating... [Flow set is not schedulable] !!!")

        return True

    def check_all_flow_has_candidate_path(self, candidate_paths):

        cpath_fid = list(candidate_paths.keys())
        fid_list = []
        for f in self.flow_specs:
            fid_list.append(copy.deepcopy(f.id))

        if set(cpath_fid) == set(fid_list):
            return True

        return False

    def check_all_affected_flow_has_candidate_path(self, candidate_paths):

        cpath_fid = list(candidate_paths.keys())
        fid_list = []
        for f in self.flow_specs:
            if f.flowtype == 'backup':
                fid_list.append(copy.deepcopy(f.id))

        if set(cpath_fid) == set(fid_list):
            return True

        return False

    def is_schedulable(self):
        """Check the schedulability of the flow-set"""
        for f in self.flow_specs:
            if not f.path:
                print("== Not all flow get path assigned! Flow set is unschedulable! ==")
                return False

        isSched = True
        # print paths
        if self.DEBUG:
            for f in self.flow_specs:
                print("Flowid:", f.id, "Path:", f.path)

        # prepare a dict to store all assigned paths
        allocated_paths = defaultdict(list)
        for f in self.flow_specs:
            flowid = f.id
            path = f.path
            cpd = CandidatePathData(flowid=flowid, path=path)
            allocated_paths[flowid].append(cpd)

        # check delay and BW constraints:
        for f in self.flow_specs:
            total_delay = self.get_total_delay_by_path(allocated_paths, f.id, f.path)
            if self.DEBUG:
                print("\nFlowid:", f.id, "Prio:", f.prio, "Observed Delay:", total_delay, "E2E deadline:", f.e2e_deadline)
            if total_delay > f.e2e_deadline:
                # print("####  Delay Constraint violated for Flowid:", f.id,
                #       " ==> Deadline:", f.e2e_deadline, "Observed Delay:", total_delay, "####")
                if self.DEBUG:
                    print("==> Delay Constraint violated for Flowid:", f.id)
                # return False
                isSched = False

            for i in range(len(f.path) - 1):
                e0 = f.path[i]
                e1 = f.path[i + 1]

                # if this is a switch-switch link
                if 's' in e0 and 's' in e1:
                    if self.topology[e0][e1]['link_bw'] < 0:
                        # print("####  BW Constraint violated for Flow:", f.id,
                        #       "Link BW:", self.topology[e0][e1]['link_bw'], "####")
                        if self.DEBUG:
                            print("==> BW Constraint violated for Flow:", f.id, "Link:", e0, "-", e1)
                        # return False
                        isSched = False

        # return True
        return isSched

    def run_shortest_path_algo(self):

        nx.set_edge_attributes(self.topology, 'cost', 1)  # add a new attribute COST

        # print("\n\n printing topo info...")
        # print(self.topology.edges(data=True))

        for flow in self.flow_specs:
            try:
                spath = nx.shortest_path(self.topology, source=flow.src, target=flow.dst, weight="cost")
                flow.path = copy.deepcopy(spath)  # update path
            except nx.NetworkXNoPath:
                print("No SP returned by NetworkX!")
                flow.path = []
                continue

            # update residual bandwidth
            for i in range(len(spath) - 1):
                e0 = spath[i]
                e1 = spath[i + 1]

                # if this is a switch-switch link
                if 's' in e0 and 's' in e1:
                    self.topology[e0][e1]['link_bw'] -= flow.bw_req
                    if self.topology[e0][e1]['link_bw'] <= 0:
                        print("\nSP: Link overloaded! -> Current flow", flow.id)
                        self.topology[e0][e1]['link_bw'] = PARAMS.LARGE_NUMBER  # set the high cost for that link

    def get_consumed_delay_by_partial_path(self, flowid, partial_path):
        """Checks how much delay budget we consumed before reaching failed edge """
        allocated_paths = defaultdict(list)
        for f in self.flow_specs:
            cpd = CandidatePathData(flowid=f.id, path=f.path)
            allocated_paths[flowid].append(cpd)

        consumed_delay = self.get_total_delay_by_path(allocated_paths, flowid, partial_path)

        if self.DEBUG:
        # if 1:
            print("\nFlowid:", self.flow_specs[flowid].id, "Prio:", self.flow_specs[flowid].prio,
                  "Consumed Delay:", consumed_delay, "E2E deadline:", self.flow_specs[flowid].e2e_deadline)

        return consumed_delay


def is_schedulable_by_flow_specs(topology, flow_specs, DEBUG=True):
    """Check the schedulability of the flow-set"""

    tcopy = copy.deepcopy(topology)

    # if DEBUG:
    #     for e in tcopy.edges():
    #         e0 = e[0]
    #         e1 = e[1]
    #         print("Available BW", tcopy[e0][e1]['link_bw'], "Link:", e0, "-", e1)

    for f in flow_specs:
        if not f.path:
            print("== Not all flow get path assigned! Flow set is unschedulable! ==")
            return False

    isSched = True
    # print paths
    if DEBUG:
        for f in flow_specs:
            print("Flowid:", f.id, "Path:", f.path)

    pg = PathGenerator(topology=topology, flow_specs=flow_specs, _debug=True)
    # prepare a dict to store all assigned paths
    allocated_paths = defaultdict(list)
    for f in flow_specs:
        flowid = f.id
        path = f.path
        cpd = CandidatePathData(flowid=flowid, path=path)
        allocated_paths[flowid].append(cpd)

    # check delay and BW constraints:
    for f in flow_specs:
        total_delay = pg.get_total_delay_by_path(allocated_paths, f.id, f.path)
        if DEBUG:
            print("\nFlowid:", f.id, "Prio:", f.prio, "Observed Delay:", total_delay, "E2E deadline:", f.e2e_deadline)
        if total_delay > f.e2e_deadline:
            # print("####  Delay Constraint violated for Flowid:", f.id,
            #       " ==> Deadline:", f.e2e_deadline, "Observed Delay:", total_delay, "####")
            if DEBUG:
                print("==> Delay Constraint violated for Flowid:", f.id)
            # return False
            isSched = False

        for i in range(len(f.path) - 1):
            e0 = f.path[i]
            e1 = f.path[i + 1]

            # if this is a switch-switch link
            if 's' in e0 and 's' in e1:
                # if topology[e0][e1]['link_bw'] < 0:
                #     # print("####  BW Constraint violated for Flow:", f.id,
                #     #       "Link BW:", self.topology[e0][e1]['link_bw'], "####")
                #     if DEBUG:
                #         print("==> BW Constraint violated for Flow:", f.id, "Link:", e0, "-", e1)
                #     # return False
                #     isSched = False
                tcopy[e0][e1]['link_bw'] -= f.bw_req
                print("Link:", e0, "-", e1, "Residual BW", tcopy[e0][e1]['link_bw'])

                if tcopy[e0][e1]['link_bw'] < 0:
                    # print("####  BW Constraint violated for Flow:", f.id,
                    #       "Link BW:", self.topology[e0][e1]['link_bw'], "####")
                    if DEBUG:
                        print("==> BW Constraint violated for Flow:", f.id, "Link:", e0, "-", e1)
                    # return False
                    isSched = False

    # return True
    return isSched


