from typing import List
import requests
import os
import pandas as pd

_endpoint = 'http://138.197.220.122:8090'


class Challenge:
    POSE = 'pose'
    ROBOT = 'robot'
    COMBINED = 'combined'


def _get_username() -> str:
    username = os.getenv('DISCORD_USERNAME')
    if not username:
        raise Exception(
            'Please set the environment variable "DISCORD_USERNAME"')
    return username


class HighscoresResult:
    def __init__(self, response_json) -> None:
        self.ranking = response_json['ranking']
        self.scores = response_json['scores']

    def __str__(self):
        return f'Your Ranking: #{self.ranking}\n' +\
            str(pd.DataFrame(self.scores.items(), columns=['name', 'score']).set_index('name'))

    def __repr__(self):
        return self.__str__()


def get_highscores(challenge: Challenge) -> HighscoresResult:
    response = requests.get(
        _endpoint + f'/highscores/{challenge}/{_get_username()}')
    return HighscoresResult(response.json())


def get_myscores(challenge: Challenge) -> List[float]:
    response = requests.get(
        _endpoint + f'/myscores/{challenge}/{_get_username()}')
    return response.json()['scores']


if __name__ == '__main__':
    print(get_highscores(Challenge.POSE))
    print(get_myscores(Challenge.POSE))
