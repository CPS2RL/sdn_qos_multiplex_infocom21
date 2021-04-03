# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"

import networkx as nx
import flow_config as fc
import expermient_handler as eh


def get_three_node_topo(_debug=False):
    # propagation and transmission delay (in millisecond)
    prop_tran_delay = 0.8192 + 0.000505  # 505 nanosecond propagation delay, 0.8192 transmission delay
    link_bw = 10 * 1000  # link capacity in kbps
    link_data = {'prop_delay': prop_tran_delay, 'link_bw': link_bw}

    nw_graph = nx.Graph()

    # add switches
    nw_graph.add_node("s1")
    nw_graph.add_node("s2")
    nw_graph.add_node("s3")

    # add hosts
    nw_graph.add_node("h11")
    nw_graph.add_node("h31")

    # interfering hosts?
    nw_graph.add_node("h21")
    nw_graph.add_node("h22")

    # add edges
    nw_graph.add_edge("s1", "s2", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s2", "s3", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])

    nw_graph.add_edge("s1", "h11", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s3", "h31", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s2", "h21", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])
    nw_graph.add_edge("s2", "h22", prop_delay=link_data['prop_delay'], link_bw=link_data['link_bw'])

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
    period = 1000  # (in millisecond)
    e2e_deadline = 3 * period
    pckt_size = 256 * 8  # size of the packets (in bits)
    pkt_processing_time = 8.548 / 1000  # corresponding processing time (in millisecond)

    # lower value means higher priority, also create high priority flows first (e.g., lower id)
    f_hp = fc.Flow(id=0, src="h11", dst="h31", period=period, e2e_deadline=e2e_deadline,
             pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
             prio=0)
    f_hp.path = ['h11', 's1', 's2', 's3', 'h31']  # hard-coded the path for this experiment

    f_lp = fc.Flow(id=1, src="h11", dst="h31", period=period, e2e_deadline=e2e_deadline,
             pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
             prio=2)
    f_lp.path = ['h11', 's1', 's2', 's3', 'h31']  # hard-coded the path for this experiment

    f_intf = fc.Flow(id=2, src="h21", dst="h31", period=period, e2e_deadline=e2e_deadline,
             pckt_size=pckt_size, pkt_processing_time=pkt_processing_time,
             prio=1)
    f_intf.path = ['h21', 's2', 's3', 'h31']  # hard-coded the path for this experiment

    flow_specs.append(f_hp)
    flow_specs.append(f_lp)
    flow_specs.append(f_intf)

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


if __name__ == "__main__":
    print("Hello")

    topology = get_three_node_topo()
    flow_specs = create_flow_spec(_debug=True)
    delay_list = eh.get_delay_by_by_flow_spec_with_path(topology=topology, flow_specs=flow_specs)

    # print e2e delay
    for indx, f in enumerate(flow_specs):
        print("\nID:", f.id)
        print("Source:", f.src)
        print("Destination:", f.dst)
        print("E2E Deadline:", f.e2e_deadline)
        print("Packet Size:", f.pckt_size)
        print("Packet Processing time:", f.pkt_processing_time)
        print("Prio:", f.prio)
        print("Path:", f.path)
        print("Observed E2E Delay:", delay_list[indx])


