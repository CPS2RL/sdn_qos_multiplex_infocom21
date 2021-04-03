__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"


from config import *
import expermient_handler as eh

import exp_model_validation_large_topo as tfsample


if __name__ == "__main__":

    topology = tfsample.get_four_node_topo()
    flow_specs = tfsample.create_flow_spec(_debug=False)

    # eh.run_path_layout_experiment_with_backup_path(topology, flow_specs, EXP_NAME=PARAMS.EXP_BACKUP_ALL_FLOW, _debug=True)
    #
    #
    eh.run_primary_backup_path_schedulablity_experiment(n_flow_each_prio_list=PARAMS.N_FLOW_EACH_PRIO_LIST_SCHED,
                                                           base_e2e_beta_list=PARAMS.BASE_E2E_BETA_LIST_BACKUP_PATH,
                                                           output_filename=PARAMS.EXP_SCHED_FORWAD_BACKUP_PATH_FILENAME)


    print("Experiment Finished!!")
