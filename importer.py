from scipy.io import loadmat
def read_state(state_path):
    data = loadmat(state_path)
    return {"KF":data["KF"].item() ,"KINJ":data["KINJ"].item()}
def read_result(result_path):
    data = loadmat(result_path)
    return {"ACC_I":data["ACC_I"].item() ,"ACC_IQ":data["ACC_IQ"].item(),"ACC_P":data["ACC_P"].item()}

def merge_experiment(state_info, result_info):
    return state_info| result_info
