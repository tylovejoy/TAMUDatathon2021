from typing import Any, Dict, Union, Tuple
import requests
from utility.pose_data import DepthImage, get_bolt_depthimage

from utility.transformation_matrix import TransformationMatrix
from .scoring_client import _get_username, Challenge
import numpy as np
from nptyping import NDArray


class RemoteEnvironment:
    endpoint = 'http://138.197.220.122:8090'

    def __init__(self):
        self.username = _get_username()
        self.resetted = False

    def reset(self):
        self.resetted = True
        response = requests.get(f'{self.endpoint}/robot/reset/{self.username}')
        return response.json()['state']

    def step(self, action, challenge):
        if not self.resetted:
            raise Exception('Must call reset.')

        response = requests.post(
            f'{self.endpoint}/robot/step/{challenge}/{self.username}',
            json={'action': np.array(action).tolist()},
        )

        data = response.json()
        if data['done']:
            self.resetted = False

        return data['state'], data['reward'], data['done'], data['info']


class RobotorqueEnvironment(RemoteEnvironment):
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

    def step(self, robot_positions: NDArray[Any, float]) -> \
            Tuple[Union[DepthImage, TransformationMatrix], float, bool, Dict]:
        """Call this function to progress the physical environment one timestep.
        
        state is going to be a pose if you have chosen Challenge.ROBOT, else it will be
        a DepthImage if you have chosen Challenge.COMBINED.
        info contains a dictonary of information that may be interesting to you for debugging purposes
        but you are NOT allowed to use for your solution.
        When you reach the NUM_STEPS, done will be True and you can access your ranking through
        the info variable.
        """
        assert len(robot_positions) == self.CONTROLS_PER_CAPTURE
        state, reward, done, info = super().step(robot_positions, self.challenge)
        state = self._parse_state(state)
        return state, reward, done, info
