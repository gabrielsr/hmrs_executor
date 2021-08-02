import os
from collections import namedtuple

from pyrunner import Worker
from commons.utils import get_curr_trial

def get_nurse_new_pos(nurse_config):
    relocate_nurse = {
        "PC Room 1": [-1, -1],
        "PC Room 2": [-1, -1],
        "PC Room 3": [-1, +1],
        "PC Room 4": [+1, +1],
        "PC Room 5": [-1, +1],
        "PC Room 6": [+1, +1],
        "PC Room 7": [-1, +1],
        "PC Room 8": [+1, +1],
        "IC Room 1": [-1, +1],
        "IC Room 2": [-1, -1],
        "IC Room 3": [-1, +1],
        "IC Room 4": [-1, -1],
        "IC Room 5": [+1, -1],
        "IC Room 6": [+1, +1],
    }
    nurse_pos = nurse_config["position"]
    nurse_loc = nurse_config["location"]
    x, y = 0, 1
    return [nurse_pos[x] + relocate_nurse[nurse_loc][x],
            nurse_pos[y] + relocate_nurse[nurse_loc][y]]

def prepare_environment(self):
    self.endsim = False
    idx = 0
    self.nurses_config = self.config[idx]["nurses"]
    self.robots_config = self.config[idx]["robots"]
    self.create_env_file(self.config[idx]["id"], self.config[idx]["code"])
    self.create_dockers()
    self.create_robots()
    self.save_compose_file()



def get_nurse_pose_str(nurse_config):
    nurse_pos = get_nurse_new_pos(nurse_config)
    print(str(nurse_pos))
    nurse_str = str(nurse_pos).replace(',',';')
    return nurse_str



class CreateDockerComposeEnv(Worker):
    def run(self):
        trial_code, n_trial, trial_config = get_curr_trial(self)
        robots_config = trial_config['robots']
        n_robots = len(robots_config)

        work_dir = self.context['work_dir']
        env_file_path = work_dir.joinpath('sim.env')
        
        with open(env_file_path, "w") as ef:

            nurse_pose_str = get_nurse_pose_str(trial_config['nurses'][0])

            ef.write("TRIAL="+str(n_trial)+'\n')
            ef.write('\n')
            ef.write("TRIAL_CODE="+str(trial_code)+'\n')
            ef.write('\n')
            ef.write("NURSE_POSE="+nurse_pose_str+'\n')
            ef.write('\n')
            ef.write('N_ROBOTS='+str(n_robots)+'\n')
            ef.write('\n')
            for robot in robots_config:
                # name
                id_str = (robot["id"])
                ef.write('ROBOT_NAME_%d=turtlebot%d\n'%(id_str,id_str))
                # pose
                pose_str = str(robot["position"]).replace(',',';')
                pose_env = ("ROBOT_POSE_%d="%(id_str))+pose_str
                ef.write(pose_env+'\n')
                # batt level
                batt_level_str = robot["battery_charge"]*100
                batt_level_env = "BATT_INIT_STATE_%d=%.2f"%(id_str,batt_level_str)
                ef.write(batt_level_env+'\n')
                batt_slope_str = robot["battery_discharge_rate"]*100
                batt_slope_env = "BATT_SLOPE_STATE_%d=%.2f"%(id_str, batt_slope_str)
                ef.write(batt_slope_env+'\n')
                ef.write('\n')
        
        self.context['env_file_path'] = env_file_path

