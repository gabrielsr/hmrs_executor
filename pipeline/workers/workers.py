# <app_root_dir>/python/workers.py
from collections import namedtuple

from datetime import datetime
from pyrunner import Worker

import os
import json

def emit_slack_message(message):
  # Assume implementation
  # ...
  print(message)

def load_to_mysql(df):
  # Assume implementation
  # ...
  print(df)

def write_as_parquet(df, path):
  # Assume implementation
  # ...
  print(df)
  print(path)

# Broadcast job start notification
class Start(Worker):
  def run(self):
    # Print function also works, but we can take advantage of
    # advanced features with the provided logger.
    self.logger.info('Starting Experiment Execution')
    abs_dir_path = os.path.dirname(os.path.realpath(__file__))
    trials_file = abs_dir_path + '/../config/trials.json'
    self.context['trials_file'] = trials_file
      

    run_date_str = datetime.now().strftime('%Y-%m-%d')
    emit_slack_message('Starting daily data download for {}'.format(run_date_str))

    # The self.context is a special thread-safe shared dictionary,
    # which can be read or modified from any Worker.
    self.context['run_date_str'] = run_date_str

class LoadTrials(Worker):
    def run(self):
      self.logger.info('loading trials')
      trials_file = self.context['trials_file']
      with open(trials_file) as f:
          self.context['trials'] = json.load(f)

class ExecTrial(Worker):
    args = namedtuple('trial_args', 'id code')
    def run(self):
        trial_params = ExecTrial.args(*self.argv)
        print(trial_params.id)

# Broadcast job end notification
class End(Worker):
  def run(self):
    self.logger.info('Completed experiment')
    # emit_slack_message('Successfully completed daily data download for {}'.format(run_date_str))