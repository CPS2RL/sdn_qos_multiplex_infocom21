# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"

import networkx as nx
import flow_config as fc
import expermient_handler as eh
import path_generator as pg


def get_four_node_topo(_debug=False):
    # propagation and transmission delay (in millisecond)
    # 505 nanosecond propagation delay, packetSize/linkBW transmission delay
    # link BW 10 GBps
    # prop_tran_delay = ((1000*8)/85899345920)*1000 + 0.000505
    prop_tran_delay = ((1000 * 8) / (10 * 8000000)) * 1000 + 0.000505

    prop_tran_delay = prop_tran_delay * 1000  # change to microsecond
    link_bw = 10 * 1000  # link capacity in kbps
    link_data = {'prop_delay': prop_tran_delay, 'link_bw': link_bw}

    nw_graph = nx.Graph()

    # add switches
    nw_graph.add_node("s1")
    nw_graph.add_node("s2")
    nw_graph.add_node("s3")
    nw_graph.add_node("s4")

    # add hosts
    nw_graph.add_node("h10")
    nw_graph.add_node("h20")
    nw_graph.add_node("h30")
    nw_graph.add_node("h40")


    # add edges
    nw_graph.add_edge("s1", "s2", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s2", "s3", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s1", "s3", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s2", "s4", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])

    nw_graph.add_edge("s1", "h10", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s2", "h20", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s3", "h30", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s4", "h40", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])

    if _debug:
        # print the topology
        print(nw_graph.edges(data=True))

        # print adjacency list to screen
        print('adjacency matrix')
        A = nx.adjacency_matrix(nw_graph)
        print(A.todense())

    return nw_graph


def create_flow_spec(_debug=False, is_path_given=True, is_longer_path_for_f4=False):
    flow_specs = []  # a set of flows with parameters

    # change accordingly for each flow -- put some value just for demonstration
    period = 3125  # in microsecond
    e2e_deadline = 800  # in microsecond
    pckt_size = 1000 * 8  # size of the packets (in bits)
    pkt_processing_time = 17.5  # corresponding processing time (in microsecond)
    bw_req = pckt_size / (3125/1000)
    # bw_req = 2500

    print ("BW req (for each flow):", bw_req)

    # lower value means higher priority, also create high priority flows first (e.g., lower id)
    f_1 = fc.Flow(id=0, src="h10", dst="h20", period=period, e2e_deadline=e2e_deadline,
             pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
             prio=0)
    f_1.bw_req = bw_req

    f_2 = fc.Flow(id=1, src="h30", dst="h20", period=period, e2e_deadline=e2e_deadline,
                 pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
                 prio=0)
    f_2.bw_req = bw_req

    f_3 = fc.Flow(id=2, src="h10", dst="h40", period=period, e2e_deadline=e2e_deadline,
                  pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
                  prio=0)
    f_3.bw_req = bw_req

    f_4 = fc.Flow(id=3, src="h10", dst="h40", period=period, e2e_deadline=e2e_deadline,
                  pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
                  prio=0)
    f_4.bw_req = bw_req

    if is_path_given:
        f_1.path = ['h10', 's1', 's2', 'h20']  # hard-coded the path for this experiment
        f_2.path = ['h30', 's3', 's1', 's2', 'h20']  # hard-coded the path for this experiment
        f_3.path = ['h10', 's1', 's2', 's4', 'h40']  # hard-coded the path for this experiment
        if is_longer_path_for_f4:
            f_4.path = ['h10', 's1', 's3', 's2', 's4', 'h40']  # hard-coded the path for this experiment
        else:
            f_4.path = ['h10', 's1', 's2', 's4', 'h40']  # hard-coded the path for this experiment

    flow_specs.append(f_1)
    flow_specs.append(f_2)
    flow_specs.append(f_3)
    flow_specs.append(f_4)

    if _debug:
        print("=== Printing flow specs: ===")
        for f in flow_specs:
            print("\nID:", f.id)
            print("Source:", f.src)
            print("Destination:", f.dst)
            print("E2E Deadline:", f.e2e_deadline)
            print("Packet Size:", f.pckt_size)
            print("Packet Processing time:", f.pkt_processing_time)
            print("Prio:", f.prio)
            print("Path:", f.path)

    return flow_specs


def get_path_by_algo():

    print("\n==== EXPERIMENT: HOW THE ALGORITHM PICKS PATH FOR ALL FLOWS (IF PATHS ARE NOT ASSIGNED) =====")
    topology = get_four_node_topo()
    flow_specs = create_flow_spec(_debug=False, is_path_given=True)
    # isSched = eh.run_path_layout_experiment(topology, flow_specs)

    path_gen_prop = pg.PathGenerator(topology=topology, flow_specs=flow_specs, _debug=True)

    path_gen_prop.run_path_layout_algo()
    isSched = path_gen_prop.is_schedulable()
    if isSched:
        print("---> Flow Set is Schedulable with the corresponding paths <---")
    else:
        print("---> Flow Set is NOT Schedulable with the corresponding paths <---")

    # for indx, f in enumerate(flow_specs):
    #     # print("\nID:", f.id)
    #     print("\nID:", "F"+str(indx+1))
    #     # print("Source:", f.src)
    #     # print("Destination:", f.dst)
    #     # print("E2E Deadline:", f.e2e_deadline)
    #     # print("Packet Size:", f.pckt_size)
    #     # print("Packet Processing time:", f.pkt_processing_time)
    #     # print("Prio:", f.prio)
    #     print("Path:", f.path)
    #     # print("Observed E2E Delay (us):", delay_list[indx])


def observe_delay_from_hw_topo(is_longer_path_for_f4):

    print("\n==== RUNNING THE EXPERIMENTS WITH THE PATH BY ASISH -> Longer Path:", is_longer_path_for_f4, " =====")

    topology = get_four_node_topo()
    flow_specs = create_flow_spec(_debug=False, is_path_given=True, is_longer_path_for_f4=is_longer_path_for_f4)
    delay_list = eh.get_delay_by_by_flow_spec_with_path(topology=topology, flow_specs=flow_specs)

    path_gen_prop = pg.PathGenerator(topology=topology, flow_specs=flow_specs, _debug=True)

    isSched = pg.is_schedulable_by_flow_specs(topology, flow_specs, DEBUG=True)

    if isSched:
        print("---> Flow Set is Schedulable with the corresponding paths <---")
    else:
        print("---> Flow Set is NOT Schedulable with the corresponding paths <---")

    #
    # # print e2e delay
    # for indx, f in enumerate(flow_specs):
    #     # print("\nID:", f.id)
    #     print("\nID:", "F"+str(indx+1))
    #     # print("Source:", f.src)
    #     # print("Destination:", f.dst)
    #     # print("E2E Deadline:", f.e2e_deadline)
    #     # print("Packet Size:", f.pckt_size)
    #     # print("Packet Processing time:", f.pkt_processing_time)
    #     # print("Prio:", f.prio)
    #     print("Path:", f.path)
    #     print("Observed E2E Delay (us):", delay_list[indx])

    # print("==== DONE WITH ASISH PATHS =====")


if __name__ == "__main__":

    observe_delay_from_hw_topo(is_longer_path_for_f4=True)
    observe_delay_from_hw_topo(is_longer_path_for_f4=False)

    get_path_by_algo()


