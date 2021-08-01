
import os
import json

from enum import Enum
from string import Template

PARENT_ID = 2

def join_it(vars, sep:str =','):
    return sep.join(map(str, vars))

def format_proc_template_file(proc_template_file,
                                proc_file, experiment_trials_file):

    with open(proc_template_file, 'r') as templ_file, \
         open(experiment_trials_file, 'r') as trial_file,\
         open(proc_file, 'w') as proc_dest_file:

        trials = json.load(trial_file)
        proc_id = PARENT_ID + 1
        proc_ids = []
        trial_jogs = []
        for trial in trials:
            id = trial['id']
            code = trial['code']
            trial_jog = [
                proc_id, # ID
                proc_id - 1, # PARENT_IDS
                1, # MAX_ATTEMPTS
                0, # RETRY_WAIT_TIME
                f'exec {id}_{code}', # PROCESS_NAME
                'workers', # MODULE_NAME
                'ExecTrial', # WORKER_NAME
                ','.join(map(str,[id, code])), # ARGUMENTS
                '$ENV{APP_LOG_DIR}/' + f'exec_{id}_{code}.log' # LOGFILE
            ]
            proc_ids.append(proc_id)
            trial_jogs.append('\t\t|'.join(map(str,trial_jog)))
            proc_id += 1
        
        trial_jogs_content = '\n'.join(trial_jogs)

        # substitute in the template
        subs= {
            'trials_jobs': trial_jogs_content,
            'proc_ids': join_it(proc_ids, ',')
        }
        src = Template(templ_file.read())
        result = src.safe_substitute(subs)
        
        # write the new proc file
        proc_dest_file.write(result)


