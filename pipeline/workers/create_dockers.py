from commons.collections import arr_to_map
from workers.load import Start

from enum import Enum

import random
from pyrunner import Worker
import json
import yaml

# from .prepare_env import get_curr_trial

from commons.utils import get_curr_trial

class Cmds(Enum):
    start_hospital_sim = '/bin/bash -c "source /ros_ws/devel/setup.bash && Xvfb -screen 0 100x100x24 :%d & DISPLAY=:%d morse run morse_hospital_sim -noaudio"'
def get_pose(loc):
    poses = {
        "IC Corridor": [-37, 15],
        "IC Room 1": [-39.44, 33.98, 0.00],
        "IC Room 2": [-32.88, 33.95, 3.14],
        "IC Room 3": [-40.23, 25.37, 0.00],
        "IC Room 4": [-33.90, 18.93, 3.14],
        "IC Room 5": [-38.00, 21.50, 0.00],
        "IC Room 6": [-38.00, 10.00, 0.00],
        "PC Corridor": [-19, 16],
        "PC Room 1": [-28.50, 18.00,-1.57],
        "PC Room 2": [-27.23, 18.00,-1.57],
        "PC Room 3": [-21.00, 18.00,-1.57],
        "PC Room 4": [-19.00, 18.00,-1.57],
        "PC Room 5": [-13.50, 18.00,-1.57],
        "PC Room 6": [-11.50, 18,-1.57],
        "PC Room 7": [-4, 18,-1.57],
        "PC Room 8": [-27.23, 13.00, 1.57],
        "PC Room 9": [-26.00, 13.00, 1.57],
        "PC Room 10": [-18.00, 13.00, 1.57],
        "Reception": [-1, 20],
        "Pharmacy Corridor": [0, 8],
        "Pharmacy": [-2, 2.6],
    }
    return poses[loc]

class Robot(object):
    """docstring for Robot"""
    def __init__(self, n, loc, batt_level, skills, config, context):
        super(Robot, self).__init__()
        self.id = n
        self.pose = get_pose(loc)
        self.batt_level = batt_level
        self.skills = skills
        # self.plan = plan
        self.config = config
        self.env_file_path = context['env_file_path']

        self.repre = {'id': self.id,
                      'pose': self.pose,
                      'batt_level': self.batt_level,
                      'skills': self.skills
                      }
        self.motion_pkg_name = 'motion_ctrl'
        self.pytrees_pkg_name = 'py_trees'
        self.motiond = None
        self.pytreesd = None
        self.build_motion_docker()
        self.build_pytrees_docker()

    def get_id(self):
        return self.id

    def get_pose(self):
        return self.pose

    def get_batt_level(self):
        return self.batt_level

    def get_motion_docker(self):
        return ('motion_ctrl'+str(self.id), self.motiond)

    def get_pytrees_docker(self):
        return ('py_trees'+str(self.id), self.pytreesd)

    def get_params(self):
        return self.repre

    def __str__(self):
        return json.dumps(self.repre)

    def build_motion_docker(self):
        # motion_ctrl:
        #     build:
        #       context: ./docker
        #       dockerfile: Dockerfile.motion
        #     container_name: motion_ctrl
        #     runtime: runc
        #     depends_on:
        #       - master
        #     ports:
        #       - "11311:11311"
        #     volumes:
        #       - ./docker/motion_ctrl:/ros_ws/src/motion_ctrl/
        #       - ./docker/turtlebot3_hospital_sim:/ros_ws/src/turtlebot3_hospital_sim/
        #     environment:
        #       - "ROS_HOSTNAME=motion_ctrl"
        #       - "ROS_MASTER_URI=http://motion_ctrl:11311"
        #       - "ROBOT_NAME=turtlebot1"
        #     env_file:
        #       - test.env
        #     # command: /bin/bash -c "source /ros_ws/devel/setup.bash && roslaunch motion_ctrl base_navigation.launch"
        #     command: /bin/bash -c "source /ros_ws/devel/setup.bash && roslaunch motion_ctrl base_navigation.launch & rosrun topic_tools relay /move_base_simple/goal /turtlebot1/move_base_simple/goal"
        #     # command: /bin/bash -c "source /ros_ws/devel/setup.bash && roscore"
        #     tty: true
        #     privileged: true
        #     networks:
        #       morsegatonet:
        #         ipv4_address: 10.2.0.6
        package_name = 'motion_ctrl'
        cointainer_name = self.motion_pkg_name+str(self.id)
        self.motiond = {
            'build': {
                'context' : './docker',
                'dockerfile': 'Dockerfile.motion',
            },
            'container_name': cointainer_name,
            'runtime': 'runc',
            'depends_on': ['master'],
            # 'ports': ["9090:9090"],
            'env_file': [self.env_file_path],
            'volumes': ['./docker/'+self.motion_pkg_name+':/ros_ws/src/'+self.motion_pkg_name+'/', './docker/turtlebot3_hospital_sim:/ros_ws/src/turtlebot3_hospital_sim/', './log/:/root/.ros/logger_sim/'],
            'environment': ["ROS_HOSTNAME="+cointainer_name, "ROS_MASTER_URI=http://master:11311", "ROBOT_NAME=turtlebot"+str(self.id)],
            # 'command': '/bin/bash -c "source /ros_ws/devel/setup.bash && roslaunch motion_ctrl base_navigation.launch & rosrun topic_tools relay /move_base_simple/goal /turtlebot1/move_base_simple/goal"'
            'command': '/bin/bash -c "source /ros_ws/devel/setup.bash && roslaunch motion_ctrl base_navigation.launch --wait"',
            'tty': True,
            'privileged': True,
            # 'networks': {
            #     'morsegatonet': {
            #         'ipv4_address': '10.2.0.6'
            #     }
            # },
            'networks': ['morsegatonet']
        }

    def build_pytrees_docker(self):
        # py_trees1:
        #     build:
        #       context: ./docker
        #       dockerfile: Dockerfile.pytrees
        #     container_name: py_trees1
        #     runtime: runc
        #     depends_on:
        #       - motion_ctrl
        #     env_file:
        #       - .env
        #     devices:
        #       - "/dev/dri"
        #       - "/dev/snd"
        #     environment:
        #       - "ROS_HOSTNAME=py_trees1"
        #       - "ROS_MASTER_URI=http://motion_ctrl:11311"
        #       - "QT_X11_NO_MITSHM=1"
        #       - "DISPLAY=$DISPLAY"
        #       - "XAUTHORITY=$XAUTH"
        #       - "QT_GRAPHICSSYSTEM=native"
        #       - "PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native"
        #       - "ROBOT_NAME=turtlebot1"
        #     volumes:
        #       - /tmp/.docker.xauth:/tmp/.docker.xauth:rw
        #       - /tmp/.X11-unix:/tmp/.X11-unix:rw
        #       - /var/run/dbus:/var/run/dbus:ro
        #       - /etc/machine-id:/etc/machine-id:ro
        #       - ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native
        #       - ~/.config/pulse/cookie:/root/.config/pulse/cookie
        #       - ./docker/py_trees_ros_behaviors:/ros_ws/src/py_trees_ros_behaviors/
        #     # command: /bin/bash -c "source /ros_ws/install/setup.bash && ros2 topic pub /std_out std_msgs/msg/String data:\ \'HelloWorld\'\ "
        #     command: python3 /ros_ws/src/bridge.py
        #     command: /bin/bash -c "source /opt/ros/noetic/setup.bash && ros2 run ros1_bridge dynamic_bridge --bridge-all-topics "
        #     tty: true
        #     networks:
        #       morsegatonet:
        #         ipv4_address: 10.2.0.8
        package_name = 'py_trees'
        cointainer_name = self.pytrees_pkg_name+str(self.id)
        self.pytreesd = {
            'build': {
                'context' : './docker',
                'dockerfile': 'Dockerfile.pytrees',
            },
            'container_name': cointainer_name,
            'runtime': 'runc',
            'depends_on': ['motion_ctrl'+str(self.id)],
            'env_file': [self.env_file_path],
            'volumes': ['/tmp/.docker.xauth:/tmp/.docker.xauth:rw',
                '/tmp/.X11-unix:/tmp/.X11-unix:rw',
                '/var/run/dbus:/var/run/dbus:ro',
                '/etc/machine-id:/etc/machine-id:ro',
                #'${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native',
                '~/.config/pulse/cookie:/root/.config/pulse/cookie',
                './docker/py_trees_ros_behaviors:/ros_ws/src/py_trees_ros_behaviors/'
                ],
            'environment': ["ROS_HOSTNAME="+cointainer_name, "ROS_MASTER_URI=http://master:11311", "ROBOT_NAME=turtlebot"+str(self.id), "SKILLS="+str(self.skills), "ROBOT_CONFIG="+json.dumps(self.config)],
            # 'command': '/bin/bash -c "source /ros_ws/devel/setup.bash && roslaunch motion_ctrl base_navigation.launch & rosrun topic_tools relay /move_base_simple/goal /turtlebot1/move_base_simple/goal"'
            'command': '/bin/bash -c "colcon build && source /ros_ws/install/setup.bash && ros2 launch py_trees_ros_behaviors tutorial_seven_docking_cancelling_failing_launch.py"',
            'tty': True,
            # 'networks': {
            #     'morsegatonet': {
            #         'ipv4_address': '10.2.0.8'
            #     }
            # },
            'networks': ['morsegatonet']
        }

class CreateDockers(Worker):
    def run(self):
        try:
            self.do_run()
        except Exception as e:
            print(e)

    def do_run(self):
        c = self.context
        env_path = c['env_file_path']
        work_dir = c['work_dir']

        code, trial_id, trial = get_curr_trial(self)
        robots_config, nurses_config = trial['robots'], trial['nurses']
        
        display_idx = random.choice([1,2,3])
        morse_cmd = Cmds.start_hospital_sim.value
        
        morse = {
            'build': {
                'context' : './docker',
                'dockerfile': 'Dockerfile.app',
            },
            'runtime': 'runc',
            'container_name': 'morse',
            'depends_on': ['master'],
            # 'devices': ["/dev/dri", "/dev/snd"],
            'env_file': [env_path],
            'environment': ["ROS_HOSTNAME=morse", "ROS_MASTER_URI=http://master:11311", "QT_X11_NO_MITSHM=1"],
            'volumes': ['/tmp/.X11-unix:/tmp/.X11-unix:rw', '~/.config/pulse/cookie:/root/.config/pulse/cookie', './docker/hmrs_hostpital_simulation/morse_hospital_sim:/ros_ws/morse_hospital_sim'],
            'expose': ["8081", "3000", "3001"],
            # 'command': 'roslaunch rosbridge_server rosbridge_websocket.launch',
            # 'command': 'rosrun tf2_web_republisher tf2_web_republisher',
            'command': (morse_cmd%(display_idx,display_idx)),
            'tty': True,
            'networks': ['morsegatonet']
        }
        master = {
            'build': {
                'context' : './docker',
                'dockerfile': 'Dockerfile.motion',
            },
            'container_name': 'master',
            'env_file': [env_path],
            'environment': ["ROBOTS_CONFIG="+json.dumps(robots_config), "NURSES_CONFIG="+json.dumps(nurses_config)],
            'volumes': ['./log/:/root/.ros/logger_sim/', './docker/motion_ctrl:/ros_ws/src/motion_ctrl/'],
            'command': '/bin/bash -c "source /ros_ws/devel/setup.bash && roslaunch src/motion_ctrl/launch/log.launch"',
            'tty': True,
            'networks': {
                'morsegatonet': {
                    'ipv4_address': '10.2.0.5'
                }
            },
        }
        ros1_bridge = {
            'build': {
                'context' : './docker',
                'dockerfile': 'Dockerfile.pytrees',
            },
            'container_name': 'ros1_bridge',
            'runtime': 'runc',
            'depends_on': ['master'],
            'env_file': [env_path],
            'volumes': ['/tmp/.docker.xauth:/tmp/.docker.xauth:rw', '/tmp/.X11-unix:/tmp/.X11-unix:rw', '/var/run/dbus:/var/run/dbus:ro'],
            'environment': ["ROS_HOSTNAME=ros1_bridge", "ROS_MASTER_URI=http://master:11311"],
            'command': '/bin/bash -c "source /opt/ros/noetic/setup.bash && ros2 run ros1_bridge dynamic_bridge --bridge-all-topics "',
            'tty': True,
            # 'networks': {
            #     'morsegatonet': {
            #         'ipv4_address': '10.2.0.8'
            #     }
            # },
            'networks': ['morsegatonet']
        }
        networks = {
            'morsegatonet': {
                'driver': 'bridge',
                'ipam': {
                    'driver': 'default',
                    'config': [{'subnet': '10.2.0.0/16'}],
                }
            }
        }
        services = {
            'morse': morse,
            'master': master,
            'ros1_bridge': ros1_bridge,
        }
        docker_compose = {
            'version': "2.3",
            'services': services,
            'networks': networks,
        }
   
        # create_robots
        
        robots_servs = []
        # build robots
        for r_config in robots_config:
            r_id = r_config["id"]
            r_loc = r_config["location"]
            robot = Robot(r_id, r_loc, r_config["battery_charge"], r_config["skills"], r_config, c)
            print(robot)
            r_motion_name, r_motion_serv = robot.get_motion_docker()
            r_pytrees_name, r_pytrees_serv = robot.get_pytrees_docker()
            robot_info = {
                'id': r_id,
                'robot': robot,
                'motion_name': r_motion_name,
                'motion_serv': r_motion_serv,
                'pytrees_name': r_pytrees_name,
                'pytrees_serv': r_pytrees_serv,
            }
            robots_servs.append(robot_info)
            print(r_config["local_plan"])
        for i in range(0, len(robots_config)):
            services[robots_servs[i]["motion_name"]] = robots_servs[i]["motion_serv"]
            services[robots_servs[i]["pytrees_name"]] = robots_servs[i]["pytrees_serv"]
        # print(self.services)


        # save save_compose_file
        docker_compose_setup_file =  work_dir.joinpath('experiment_trials.yaml')
        with open(docker_compose_setup_file, 'w') as file:
            documents = yaml.dump(docker_compose, file)