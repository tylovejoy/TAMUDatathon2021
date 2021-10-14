import requests
import os


class RemoteEnv:
    endpoint = 'http://138.197.220.122:8090/'

    def __init__(self):
        self.username = os.getenv('DISCORD_USERNAME')
        if not self.username:
            raise Exception(
                'Please set the environment variable "DISCORD_USERNAME"')
        self.resetted = False

    def reset(self):
        self.resetted = True
        response = requests.get(self.endpoint + 'reset/?name=' + self.username)
        return response.json()['state']

    def step(self, action):
        if not self.resetted:
            raise Exception('Must call reset.')

        response = requests.post(self.endpoint + 'step/', json={
            'name': self.username,
            'action': action
        })

        data = response.json()
        if data['done']:
            self.resetted = False

        return data['state'], data['reward'], data['done'], data['info']


class RobotorqueEnv(RemoteEnv):
    """
    state: array of length 2. First element is the position of robot,
        second is the (last-observed) position of the bolt
    reward: max(5 - mm between bolt and robot, 0)
    done: boolean. True if finished episode (at 1000 steps)
    info: data that might be helpful for debugging but can't use to make predictions
    """
    NUM_STEPS = 100
    OBSERVE_TIMESTEP = 0.2
    MAX_ROBOT_SPEED = 100  # mm / s
