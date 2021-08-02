#!/usr/bin/env python3

import os, sys
from pyrunner import PyRunner
from pathlib import Path

from generate_trial_jobs import format_proc_template_file

if __name__ == '__main__':
  # Determine absolute path of this file's parent directory at runtime
  abs_dir_path = os.path.dirname(os.path.realpath(__file__))

  # Store path to default config and .lst file
  config_file = '{}/config/app_profile'.format(abs_dir_path)
  proc_file = '{}/config/hmrs_executor.lst'.format(abs_dir_path)
  proc_template_file = '{}/config/hmrs_executor_template.lst'.format(abs_dir_path)
  experiment_trials_file = '{}/config/trials.json'.format(abs_dir_path)
  work_dir = '{}/../work_dir'.format(abs_dir_path)

  work_dir_path = Path(work_dir)
  work_dir_path.mkdir(parents=True, exist_ok=True)
  # format_proc_template_file(proc_template_file=proc_template_file, 
  #                           proc_file=proc_file, experiment_trials_file=experiment_trials_file)

  # Init PyRunner and assign default config and .lst file
  app = PyRunner(config_file=config_file, proc_file=proc_file)
  app.context['work_dir'] = work_dir_path.resolve()
  # Initiate job and exit driver with return code
  app.config['nozip'] = True
  sys.exit(app.execute())
