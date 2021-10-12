import requests

class RemoteEnv:
    def __init__(self, myname):
        self.endpoint = 'https://gm-datathon.herokuapp.com/' # 'http://127.0.0.1:5000/'
        self.myname = myname
        self.resetted = False

    def reset(self):
        self.resetted = True
        response = requests.get(self.endpoint + 'reset/?name=' + self.myname)
        return response.json()['state']

    def step(self, action):
        if not self.resetted:
            raise Exception('Must call reset.')

        response = requests.post(self.endpoint + 'step/', json={
            'name': self.myname,
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
    def step(self, robot_position):
        return super().step(robot_position)


if __name__ == '__main__':
    import numpy as np
    import pandas as pd
    import sys
    assert len(sys.argv) >= 2, 'please provide your name as command line argument. E.g. ">>> python remote_env.py foobar"'
    name = sys.argv[1]
    env = RobotorqueEnv(name)
    state = env.reset()
    done = False
    history = []
    import time
    start = time.time()

    def get_robot_position(state):
        # replace with your actor code!!
        return np.random.uniform(-10, 10)

    while not done:
        action = get_robot_position(state)
        state, r, done, info = env.step(action)
        history.append(info)
    print(time.time() - start)
    print(pd.DataFrame(history))