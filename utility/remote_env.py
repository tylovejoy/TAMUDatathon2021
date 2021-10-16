from typing import Any
import requests
from utility.pose_data import get_bolt_depthimage

from utility.transformation_matrix import TransformationMatrix
from .scoring_client import _get_username, Challenge
import numpy as np
from nptyping import NDArray


class RemoteEnv:
    endpoint = 'http://138.197.220.122:8090'

    def __init__(self):
        self.username = _get_username()
        self.resetted = False

    def reset(self):
        self.resetted = True
        response = requests.get(
            self.endpoint + f'/robot/reset/{self.username}')
        return response.json()['state']

    def step(self, action, challenge):
        if not self.resetted:
            raise Exception('Must call reset.')

        response = requests.post(self.endpoint + f'/robot/step/{challenge}/{self.username}', json={
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
    done: boolean. True if finished episode (at 200 steps)
    info: data that might be helpful for debugging but can't use to make predictions
    """
    NUM_STEPS = 200
    OBSERVE_TIMESTEP = 0.2  # s
    MAX_ROBOT_SPEED = 100  # mm / s
    CONTROLS_PER_CAPTURE = 10  # meaning 0.02 control time

    def __init__(self, challenge: Challenge):
        super().__init__()
        self.challenge = challenge

    def _parse_state(self, s):
        bolt_pose = TransformationMatrix(np.array(s[0]))
        robot_pose = TransformationMatrix(np.array(s[1]))
        if self.challenge == Challenge.ROBOT:
            return {'robot_pose': robot_pose, 'bolt_pose': bolt_pose}
        elif self.challenge == Challenge.COMBINED:
            return {'robot_pose': robot_pose, 'bolt_pose': get_bolt_depthimage(s['bolt_pose'])}
        raise Exception('Invalid Challenge')

    def reset(self):
        s = super().reset()
        return self._parse_state(s)

    def step(self, robot_positions: NDArray[Any, float]):
        assert len(robot_positions) == self.CONTROLS_PER_CAPTURE
        s, r, d, i = super().step(robot_positions, self.challenge)
        s = self._parse_state(s)
        return s, r, d, i
