# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"


from config import *
import expermient_handler as eh


if __name__ == "__main__":

    eh.run_non_mp_pri_back_path_schedulablity_experiment(n_flow_each_prio_list=PARAMS.N_FLOW_EACH_PRIO_LIST_NON_MP_BACK_SCHED,
                                                           base_e2e_beta_list=PARAMS.BASE_E2E_BETA_LIST_BACKUP_PATH,
                                                           output_filename=PARAMS.EXP_SCHED_NON_MP_FORWAD_BACKUP_PATH_FILENAME)


    print("Experiment Finished!!")
