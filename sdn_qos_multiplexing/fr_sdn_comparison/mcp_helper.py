# __author__ = 'Monowar Hasan'
# from __future__ import division
import networkx as nx
# import sys
from collections import defaultdict
import math
import pandas as pd
import random
import itertools
# from model.intent import Intent
# from synthesis.synthesis_lib import SynthesisLib

from copy import deepcopy

def noncontiguoussample(n, k):

    # How many numbers we are not picking
    total_skips = n - k

    # Distribute the additional skips across the range
    skip_cutoffs = random.sample(range(total_skips + 1), k)
    skip_cutoffs.sort()

    # Construct the final set of numbers based on our skip distribution
    samples = []
    for index, skip_spot in enumerate(skip_cutoffs):
        # This is just some math-fu that translates indices within the
        # skips to values in the overall result.
        samples.append(1 + index + skip_spot)

    return samples


def get_random_link_data(link_delay, link_bw):

    # delay = random.randint(delay / 5, delay)  # get a random delay

    # bw in BPS and delay in second
    link_data = {'link_delay': float(link_delay) * 0.000001, 'link_bw': link_bw * 1000000}
    return link_data


def setup_network_graph_without_mininet(num_switches, num_hosts_per_switch, link_delay, link_bw):

    nw_graph = nx.Graph()
    switch_names = []

    # setup the switches
    for i in range(num_switches):
        nw_graph.add_node("s" + str(i + 1))
        switch_names.append("s" + str(i + 1))
        # add hosts per switch
        for j in range(num_hosts_per_switch):
            nw_graph.add_node("h" + str(i + 1) + str(j + 1))

            # add link
            link_data = get_random_link_data(link_delay, link_bw)
            nw_graph.add_edge("s" + str(i + 1),
                              "h" + str(i + 1) + str(j + 1),
                              link_delay=link_data['link_delay'],
                              link_bw=link_data['link_bw'])

    #  Add links between switches
    if num_switches > 1:
        for i in range(num_switches - 1):
            link_data = get_random_link_data(link_delay, link_bw)
            nw_graph.add_edge(switch_names[i], switch_names[i + 1],
                              link_delay=link_data['link_delay'],
                              link_bw=link_data['link_bw'])

        #  Form a ring only when there are more than two switches
        if num_switches > 2:
            link_data = get_random_link_data(link_delay, link_bw)
            nw_graph.add_edge(switch_names[0], switch_names[-1],
                              link_delay=link_data['link_delay'],
                              link_bw=link_data['link_bw'])

            # create some random links
            nodelist = noncontiguoussample(num_switches - 1, int(num_switches / 2.0))

            for i in range(len(nodelist) - 1):
                switch_names[nodelist[i]]

                link_data = get_random_link_data(link_delay, link_bw)

                nw_graph.add_edge(switch_names[nodelist[i]], switch_names[nodelist[i + 1]],
                                  link_delay=link_data['link_delay'],
                                  link_bw=link_data['link_bw'])

    # print('adjacency matrix')
    # print(nx.adjacency_matrix(nw_graph).todense())
    # print('end adjacency matrix')
    #
    # print(nw_graph.edges(data=False))

    return nw_graph


def print_flow_paths(flow_specs):
    for flow in flow_specs:
        print("src:", flow.src_host_id, "dst:", flow.dst_host_id, "path:", flow.path)


def print_flow_specs(flow_specs):
    for flow in flow_specs:
        print("src:", flow.src_host_id)
        print("dst:", flow.dst_host_id)
        print("delay budget:", flow.delay_budget)
        print("bw req:", flow.bw_req)
        print("path:", flow.path)


def prepare_flow_specifications(number_of_switches, hps, number_of_RT_flows,
                                delay_budget_lb_ub, bw_req_lb_ub):

    flow_specs = []

    flowlist = list(itertools.product(range(1, number_of_switches+1), range(1, hps+1)))

    # for real-time flows
    # if unique number (e.g. unique flow-per host) required
    # index_list = random.sample(range(len(flowlist)), number_of_RT_flows + 1) # for real-time flows

    # generate random indices (#of_RT_flows)
    index_list = [random.randint(0, len(flowlist) - 1) for i in range(number_of_RT_flows)]

    for i in range(number_of_RT_flows):
        indx = flowlist[index_list[i]]
        _idx0 = int(indx[0])
        rnd = itertools.chain(range(1, _idx0) , range(_idx0 + 1, number_of_switches+1))
        rnd = list(rnd)

        nxtindx = (random.choice(rnd), random.randint(1, hps))

        delay_budget = random.randint(delay_budget_lb_ub[0], delay_budget_lb_ub[1])
        bw_req = random.randint(bw_req_lb_ub[0], bw_req_lb_ub[1])

        _flow = get_flow(indx, nxtindx, delay_budget, bw_req)

        flow_specs.append(_flow)

    return flow_specs


def get_flow(indx, nxtindx, delay_budget, bw_req):

    src = "h" + str(indx[0]) + str(indx[1])
    dst = "h" + str(nxtindx[0]) + str(nxtindx[1])

    _flow = FlowSpecification(src_host_id=src,
                              dst_host_id=dst,
                              delay_budget=delay_budget,
                              bw_req=bw_req)

    return _flow


class FlowSpecification:
    def __init__(self, src_host_id, dst_host_id, delay_budget, bw_req):
        self.src_host_id = src_host_id
        self.dst_host_id = dst_host_id

        self.delay_budget = delay_budget * 0.000001  # convert microsecond to second
        self.bw_req = bw_req * 1000000  # in BPS

        self.path = None


class MCPHelper(object):

    def __init__(self, nw_graph, hmax, delay_budget, bw_budget, bw_req_flow, x=10):
        self.nw_graph = nw_graph
        self.x = x
        self.d = defaultdict(dict)
        self.pi = defaultdict(dict)

        self.hmax = hmax
        self.bw_req_flow = bw_req_flow
        self.delay_budget = delay_budget
        self.bw_budget = bw_budget

    def init_mcp(self, src, itr):

        if itr == 1:
            loop_range = self.x
        elif itr == 2:
            loop_range = int(math.floor(self.bw_budget))
        else:
            raise NotImplementedError

        for v in self.nw_graph.nodes():
            for i in range(loop_range + 1):
                self.d[v][i] = float("inf")
                self.pi[v][i] = float("nan")

        for i in range(self.x + 1):
            self.d[src][i] = 0.0

    def get_bandwidth(self, u, v):

        if self.nw_graph[u][v]['link_bw'] == 0:
            return 1.0

        return float(self.bw_req_flow) / float(self.nw_graph[u][v]['link_bw'])

    def get_new_bandwidth(self, u, v):

        return math.ceil((self.get_bandwidth(u, v) * self.x) / self.bw_budget)

    def get_delay(self, u, v):

        return self.nw_graph[u][v]['link_delay']

    def get_new_delay(self, u, v):

        return math.ceil((self.get_delay(u, v) * self.x) / float(self.delay_budget))

    def relax_mcp(self, u, v, k, itr):

        if itr == 1:
            w1 = self.get_delay(u, v)
            w2_prime = self.get_new_bandwidth(u, v)
            loop_range = self.x

        elif itr == 2:
            w1 = self.get_new_delay(u, v)
            w2_prime = self.get_bandwidth(u, v)
            loop_range = int(math.floor(self.bw_budget))

        else:
            raise NotImplementedError

        kprime = int(k + w2_prime)

        # print("kprime:", kprime, "w2_prime:", w2_prime)

        if 0 <= kprime <= loop_range:
            if self.d[v][kprime] > self.d[u][k] + w1:
                self.d[v][kprime] = self.d[u][k] + w1
                self.pi[v][kprime] = u

    def calculate_mcp_ebf(self, src, dst, itr):

        # print "=== Calculating MCP_EBF ==="

        if itr == 1:
            loop_range = self.x
        elif itr == 2:
            loop_range = int(math.floor(self.bw_budget))
        else:
            raise NotImplementedError

        self.init_mcp(src, itr)

        number_of_nodes = len(list(self.nw_graph.nodes()))
        for i in range(1, number_of_nodes):
            for k in range(loop_range+1):
                for edge in self.nw_graph.edges():
                    u = edge[0]
                    v = edge[1]
                    self.relax_mcp(u, v, k, itr)

    def extract_path(self, src, dst, itr):

        path = []
        traverse_done = False
        current_node = dst

        if itr == 1:
            loop_range = self.x
        elif itr == 2:
            loop_range = int(math.floor(self.bw_budget))
        else:
            raise NotImplementedError

        count = 0
        maxcount = 1000000  # some arbitrary large number

        while not traverse_done:
            count += 1
            if count > maxcount:
                # raise ValueError('Unable to find path within maximum timeout')
                return None

            for k in range(loop_range + 1):
                if not pd.isnull(self.pi[current_node][k]):
                    path.append(current_node)
                    current_node = self.pi[current_node][k]
                    break
                if current_node == src:
                    path.append(current_node)
                    traverse_done = True
                    break

        return path

    def check_solution(self, dst, itr):
        if itr == 1:
            c1 = self.delay_budget
        elif itr == 2:
            c1 = self.x
        else:
            raise NotImplementedError

        for k in range(self.x+1):
            if self.d[dst][k] <= c1:
                return True

        return False

    def get_path_layout(self, src, dst):
        path_src_2_dst = []
        itr = 2
        for i in range(1, itr + 1):

            self.calculate_mcp_ebf(src, dst, i)

            if self.check_solution(dst, i):
                # print("Path found at pass {}".format(i))
                path = self.extract_path(src, dst, i)
                if path is None:
                    return path_src_2_dst  # return empty
                path_src_2_dst = path[::-1]
                return path_src_2_dst
            # else:
            #     print("Unable to find path at pass {}".format(i))

        return path_src_2_dst


def print_graph(nw_graph):

    print("print nodes..")
    print(nw_graph.nodes())

    print("print edges...")
    print(nw_graph.edges())


def get_link_data(nw_graph, node1_id, node2_id, query_type):
    # link_data = nw_graph[node1_id][node2_id]['link_data']
    link_data = nw_graph[node1_id][node2_id][query_type]
    return link_data


def get_bw_budget(nw_graph, bw_req_flow, hmax):
    max_bw_util = 0
    for i in nw_graph.edges():

        link_bw = get_link_data(nw_graph, i[0], i[1], 'link_bw')

        if link_bw == 0:
            bw_util = hmax
        else:
            bw_util = hmax * float(bw_req_flow) / float(link_bw)

        if bw_util >= max_bw_util:
            max_bw_util = bw_util

    return max_bw_util


def calibrate_graph(input_graph):

    nw_graph = nx.DiGraph()
    graph = input_graph

    for i in graph.nodes():
        nw_graph.add_node(i)

    # create bidirectional links
    for i in graph.edges():
        # ld = get_link_data(input_graph, i[0], i[1])
        link_delay = get_link_data(input_graph, i[0], i[1], 'link_delay')
        link_bw = get_link_data(input_graph, i[0], i[1], 'link_bw')
        nw_graph.add_edge(i[0], i[1], link_delay=link_delay, link_bw=link_bw)
        nw_graph.add_edge(i[1], i[0], link_delay=link_delay, link_bw=link_bw)

    return nw_graph


def calculate_hmax(nw_graph):

    hmax = nx.number_of_nodes(nw_graph)
    return hmax


def update_reamining_bw(nw_graph, current_flow):
    # print "updating remaining bw..."
    # reduce the bw that allocated to that flow-path
    for i in range(1, len(current_flow.path) - 1):
        nw_graph[current_flow.path[i]][current_flow.path[i+1]]['link_bw'] -= current_flow.bw_req
        nw_graph[current_flow.path[i+1]][current_flow.path[i]]['link_bw'] -= current_flow.bw_req


def print_path(nw_config):

    print("....Printing flow path....")

    for current_flow in nw_config.flow_specs:
        path = current_flow.path
        if not path:
            print("No path found for flow {} to {}".format(current_flow.src_host_id, current_flow.dst_host_id))
        else:
            print("Path found for flow {} to {}".format(current_flow.src_host_id, current_flow.dst_host_id))
            print(path)


def print_delay_budget(nw_config):

    print("....Printing delay budget....")

    for current_flow in nw_config.flow_specs:
        print("Delay budget for flow {} to {} is {}".format(current_flow.src_host_id, current_flow.dst_host_id,
                                                            current_flow.delay_budget))


def test_all_flow_is_schedulable(flow_specs):

    for current_flow in flow_specs:
        if not current_flow.path:
            return False

    return True


def get_fr_sdn_path_by_mcp(nw_graph, flow_specs, x=10):

    for flow_id, current_flow in enumerate(flow_specs):

        src = current_flow.src_host_id
        dst = current_flow.dst_host_id

        bw_req_flow = current_flow.bw_req  # BPS
        hmax = calculate_hmax(nw_graph)
        delay_budget = current_flow.delay_budget
        bw_budget = get_bw_budget(nw_graph, bw_req_flow, hmax)
        nw_graph = calibrate_graph(nw_graph)
        mh = MCPHelper(nw_graph, hmax, delay_budget, bw_budget, bw_req_flow, x)
        path = mh.get_path_layout(src, dst)

        # if not path:
        #     # print("No path found for flow {} to {}".format(current_flow.src_host_id, current_flow.dst_host_id))
        if path:
            # print("Path found for flow {} to {}".format(current_flow.src_host_id, current_flow.dst_host_id))
            # print(path)
            # set the path for the flow
            current_flow.path = path

            # decrease the available bw in the path
            update_reamining_bw(nw_graph, current_flow)


# returns most or least congested link
def get_tagged_link(nw_graph, flow_specs):
    edge_visit_count = defaultdict(dict)

    # initialize

    print("edge list:", nw_graph.edges())
    for e in nw_graph.edges():
        n1 = e[0]
        n2 = e[1]
        edge_visit_count[n1][n2] = 0
        edge_visit_count[n2][n1] = 0


    # traverse and update count
    for flow in flow_specs:
        path = flow.path

        if path:
            for pp in range(len(path)-1):
                n1 = path[pp]
                n2 = path[pp+1]
                edge_visit_count[n1][n2] += 1
                edge_visit_count[n2][n1] += 1

    print("edge visit count", edge_visit_count)