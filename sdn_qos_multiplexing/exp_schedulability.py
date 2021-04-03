__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"

from config import *
import expermient_handler as eh


if __name__ == "__main__":

    eh.run_schedulablity_experiment(n_flow_each_prio_list=PARAMS.N_FLOW_EACH_PRIO_LIST_SCHED,
                                        base_e2e_beta_list=PARAMS.BASE_E2E_BETA_LIST)

    print("Experiment Finished!!")
