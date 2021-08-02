
from pyrunner.worker.abstract import Worker


def get_curr_trial(worker: Worker):
    [id, code] = worker.argv
    trial_id = int(id)
    trials_map = worker.context['trials_map']
    trial = trials_map[code]
    return code, trial_id, trial