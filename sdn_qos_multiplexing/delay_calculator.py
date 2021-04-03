# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"

import math
from config import *


def fifo_delay_eqn(tag_flow, same_sw_flow_set, w):

    sum_delay = 0
    for fk in same_sw_flow_set:
        if fk.prio == tag_flow.prio:
            sum_delay += math.ceil((w + 1)/fk.period) * fk.pkt_processing_time

    qi = sum_delay - w

    return qi


def max_delay(tag_flow, same_sw_flow_set):
    """ An upper bound of delay """
    # maxdelay = []
    # for fk in same_sw_flow_set:
    #     # if with the same prio-level
    #     if fk.prio == tag_flow.prio:
    #         maxdelay.append(fk.e2e_deadline)
    #
    # return max(maxdelay)

    return tag_flow.period


def get_fifo_delay_by_pck_size(tag_flow_indx, flow_specs, same_sw_flow_set):

    tag_flow = flow_specs[tag_flow_indx]

    fifo_delay = 0
    for fk in same_sw_flow_set:
        # if with the same prio-level
        if fk.prio == tag_flow.prio:
            fifo_delay += fk.pkt_processing_time
    return fifo_delay


def isFeasible(tag_flow, same_sw_flow_set):

    # check whether a set of flow using same switch (and same prio) is feasible

    util = 0
    for fk in same_sw_flow_set:
        if fk.prio == tag_flow.prio:
            util += fk.pkt_processing_time / fk.period

    if util < 1.0:
        return True

    return False


def calculate_fifo_busy_interval_recurrence(tag_flow_indx, flow_specs, same_sw_flow_set, w, w_plusone):

    tag_flow = flow_specs[tag_flow_indx]

    if not isFeasible(tag_flow, same_sw_flow_set):
        # print("Max delay:", max_delay(tag_flow, same_sw_flow_set))
        return max_delay(tag_flow, same_sw_flow_set)  # return the max length

    sumdj = 0
    for fk in same_sw_flow_set:
        sumdj += fk.pkt_processing_time

    wi = max(sumdj, w_plusone)

    cnt = 0
    while True:

        t1 = 0
        for fj in same_sw_flow_set:
            if fj.prio == tag_flow.prio:
                if fj.id != tag_flow.id:

                    t1 += math.ceil(wi/fj.period) * fj.pkt_processing_time

        t2 = max(0, math.ceil((wi-w)/tag_flow.period) * tag_flow.pkt_processing_time)

        wi_new = t1 + t2

        # print("wi", wi, "wnew:", wi_new)
        if wi_new == wi:
            # print("Converged!")
            break

        wi = wi_new  # update and continue

        cnt += 1

        # put some loop bound and return max delay (just in case)
        if cnt > PARAMS.MAX_LOOP_COUNT:
            return max_delay(tag_flow, same_sw_flow_set)  # return the max length

    return wi


def get_fifo_window_sizes(tag_flow_indx, flow_specs):

    """ Returns the set of window sizes Wi(\tilde{omega}) """

    tag_flow = flow_specs[tag_flow_indx]
    same_sw_flow_set = flow_specs

    window_list = []

    # w = tag_flow.period - 1

    w_plusone = 0
    for fk in same_sw_flow_set:
        if fk.prio == tag_flow.prio:
            if fk.id != tag_flow.id:
                w_plusone += fk.pkt_processing_time

    # print("W_plus_one:", w_plusone)

    for w in range(tag_flow.period-1, -1, -1):
        wi = calculate_fifo_busy_interval_recurrence(tag_flow_indx=tag_flow_indx,
                                                 flow_specs=flow_specs,
                                                 same_sw_flow_set=same_sw_flow_set,
                                                 w=w,
                                                 w_plusone=w_plusone)

        window_list.append(wi)
        w_plusone = wi  # update

    window_list = list(set(window_list))  # remove duplicates
    # print("window list is", window_list)
    # print("Tag flow period:", tag_flow.period)

    return window_list


def get_fifo_delay(tag_flow_indx, flow_specs, same_sw_flow_set):

    tag_flow = flow_specs[tag_flow_indx]

    if not isFeasible(tag_flow, same_sw_flow_set):
        # print("Return due to infeasibility!")
        return max_delay(tag_flow, same_sw_flow_set)  # return the max length

    # window_list = get_fifo_window_sizes(tag_flow_indx, flow_specs)
    # window_list = max(window_list)

    # loop through whole period instead of busy-window
    # (this is to resolve the problem of millisecond/microsecond unit conversion)
    window_list = tag_flow.period
    max_fifo = 0

    # get the max fifo delay
    # for w in window_list:
    for w in range(window_list):
        qi = fifo_delay_eqn(tag_flow, same_sw_flow_set, w)
        if qi > max_fifo:
            max_fifo = qi

    #
    #
    # # calculate so-called utilization
    # util = 0
    # for fk in flow_specs:
    #     util += fk.pkt_processing_time/fk.period
    #
    # print("total util is:", util)

    return max_fifo


def get_priority_interference_delay(tag_flow_indx, flow_specs, same_sw_flow_set):
    """ returns the interference due to priority queuing """

    tag_flow = flow_specs[tag_flow_indx]
    egress_blocking = 0  # TODO: should we change that?

    intf = 0

    for fk in same_sw_flow_set:
        if fk.prio < tag_flow.prio:
            intf += math.ceil(tag_flow.period/fk.period) * fk.pkt_processing_time

    return egress_blocking + intf
