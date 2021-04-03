# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"

import networkx as nx
import flow_config as fc
import expermient_handler as eh
import path_generator as pg


def get_four_node_topo(_debug=False):
    # propagation and transmission delay (in millisecond)
    # 505 nanosecond propagation delay, packetSize/linkBW transmission delay
    # link BW 1 GBps
    prop_tran_delay = ((1000*8)/(1 * 8000000))*1000 + 0.000505
    prop_tran_delay = prop_tran_delay * 1000  # change to microsecond

    print("Prop and transmission delay (us):", prop_tran_delay)

    link_bw = 10 * 8000000  # link capacity in kbps
    link_data = {'prop_delay': prop_tran_delay, 'link_bw': link_bw}

    nw_graph = nx.Graph()

    # add switches
    nw_graph.add_node("s1")
    nw_graph.add_node("s2")
    nw_graph.add_node("s3")
    nw_graph.add_node("s4")

    # add hosts
    nw_graph.add_node("h1")
    nw_graph.add_node("h2")
    nw_graph.add_node("h3")
    nw_graph.add_node("h4")
    nw_graph.add_node("h5")
    nw_graph.add_node("h6")
    nw_graph.add_node("h7")
    nw_graph.add_node("h8")
    nw_graph.add_node("h9")
    nw_graph.add_node("h10")
    nw_graph.add_node("hd1")
    nw_graph.add_node("hd2")


    # add edges
    nw_graph.add_edge("s1", "s2", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s2", "s4", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s1", "s3", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s2", "s3", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])

    nw_graph.add_edge("s1", "h10", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s1", "h1", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s1", "h2", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s1", "h3", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s1", "h4", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s1", "h5", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s1", "h6", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])

    nw_graph.add_edge("s2", "hd1", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])

    nw_graph.add_edge("s3", "h7", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s3", "h8", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s3", "h9", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])

    nw_graph.add_edge("s4", "hd2", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])

    if _debug:
        # print the topology
        print(nw_graph.edges(data=True))

        # print adjacency list to screen
        print('adjacency matrix')
        A = nx.adjacency_matrix(nw_graph)
        print(A.todense())

    return nw_graph


def create_flow_spec(_debug=False):
    flow_specs = []  # a set of flows with parameters

    # change accordingly for each flow -- put some value just for demonstration
    period = 5  # in microsecond
    # e2e_deadline = 800  # in microsecond
    e2e_deadline = 3000  # in microsecond
    pckt_size = 1000 * 8  # size of the packets (in bits)
    pkt_processing_time = 17.0  # corresponding processing time (in microsecond)
    # bw_req = pckt_size / (5/1000) # Kbps
    bw_req = 200 * 8000  # Kbps

    print("BW req (for each flow):", bw_req)

    # lower value means higher priority
    f_1 = fc.Flow(id=0, src="h1", dst="hd1", period=period, e2e_deadline=e2e_deadline,
             pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
             prio=2)

    f_2 = fc.Flow(id=1, src="h2", dst="hd2", period=period, e2e_deadline=e2e_deadline,
                  pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
                  prio=2)

    f_3 = fc.Flow(id=2, src="h3", dst="hd1", period=period, e2e_deadline=e2e_deadline,
                  pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
                  prio=1)
    f_4 = fc.Flow(id=3, src="h4", dst="hd2", period=period, e2e_deadline=e2e_deadline,
                  pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
                  prio=1)
    f_5 = fc.Flow(id=4, src="h5", dst="hd1", period=period, e2e_deadline=e2e_deadline,
                  pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
                  prio=0)
    f_6 = fc.Flow(id=5, src="h6", dst="hd2", period=period, e2e_deadline=e2e_deadline,
                  pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
                  prio=0)
    f_7 = fc.Flow(id=6, src="h7", dst="hd1", period=period, e2e_deadline=e2e_deadline,
                  pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
                  prio=2)
    f_8 = fc.Flow(id=7, src="h8", dst="hd1", period=period, e2e_deadline=e2e_deadline,
                  pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
                  prio=1)
    f_9 = fc.Flow(id=8, src="h9", dst="hd1", period=period, e2e_deadline=e2e_deadline,
                  pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
                  prio=0)
    f_10 = fc.Flow(id=9, src="h10", dst="hd2", period=period, e2e_deadline=e2e_deadline,
                  pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
                  prio=1)

    flow_specs.append(f_1)
    flow_specs.append(f_2)
    flow_specs.append(f_3)
    flow_specs.append(f_4)
    flow_specs.append(f_5)
    flow_specs.append(f_6)
    flow_specs.append(f_7)
    flow_specs.append(f_8)
    flow_specs.append(f_9)
    flow_specs.append(f_10)

    for f in flow_specs:
        f.bw_req = bw_req

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
    flow_specs = create_flow_spec(_debug=False)
    # isSched = eh.run_path_layout_experiment(topology, flow_specs)

    path_gen_prop = pg.PathGenerator(topology=topology, flow_specs=flow_specs, _debug=True)

    path_gen_prop.run_path_layout_algo()

    print("\n** Note: Lower prio value means higher priority.\n")

    isSched = path_gen_prop.is_schedulable()

    if isSched:
        print("---> Flow Set is Schedulable with the corresponding paths <---")
    else:
        print("---> Flow Set is NOT Schedulable with the corresponding paths <---")


if __name__ == "__main__":

    get_path_by_algo()


