__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"

from config import *
import expermient_handler as eh


if __name__ == "__main__":

    eh.run_multiplxe_no_multiplex_schedulablity_experiment(n_flow_each_prio_list=PARAMS.N_FLOW_EACH_PRIO_LIST_SCHED,
                                                           base_e2e_beta_list=PARAMS.BASE_E2E_BETA_LIST_MULTIPLEX_COMP,
                                                           exp_name=PARAMS.EXP_WITHOUT_MULTIPLEX,
                                                           output_filename=PARAMS.EXP_SCHED_WITHOUT_MULTIPLEX_FILENAME)

    eh.run_multiplxe_no_multiplex_schedulablity_experiment(n_flow_each_prio_list=PARAMS.N_FLOW_EACH_PRIO_LIST_SCHED,
                                                           base_e2e_beta_list=PARAMS.BASE_E2E_BETA_LIST_MULTIPLEX_COMP,
                                                           exp_name=PARAMS.EXP_WITH_MULTIPLEX,
                                                           output_filename=PARAMS.EXP_SCHED_WITH_MULTIPLEX_FILENAME)

    print("Experiment Finished!!")
