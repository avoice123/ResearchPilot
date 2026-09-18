class Experiment:
    def __init__(
            self,
            experiment_id,
            kf,
            kinj,
            acc_i,
            acc_iq,
            acc_p,
            state_file,
            result_file,
            created_at
    ):
        self.id = experiment_id
        self.kf = kf
        self.kinj = kinj
        self.acc_i = acc_i
        self.acc_iq = acc_iq
        self.acc_p = acc_p
        self.state_file = state_file
        self.result_file = result_file
        self.created_at = created_at
    def show_experiment(self):
        print(
            f"实验id={self.id}\n"
            f"KF={self.kf}\n"
            f"KINJ={self.kinj}\n"
            f"ACC_I={self.acc_i}\n"
            f"ACC_IQ={self.acc_iq}\n"
            f"ACC_P={self.acc_p}\n"
            f"state_file={self.state_file}\n"
            f"result_file={self.result_file}\n"
            f"created_at={self.created_at}\n"
        )