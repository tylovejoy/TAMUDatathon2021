import requests

class ScoringClient:
    def __init__(self, myname):
        self.endpoint = 'https://gm-datathon.herokuapp.com/' #'http://127.0.0.1:5000/'
        self.myname = myname

    def get_highscores(self):
        response = requests.get(self.endpoint + 'highscores/?name=' + self.myname)
        return response.json()

    def get_myscores(self):
        response = requests.get(self.endpoint + 'myscores/?name=' + self.myname)
        return response.json()


if __name__ == '__main__':
    import sys
    assert len(sys.argv) >= 2, 'please provide your name as command line argument. E.g. ">>> python remote_env.py foobar"'
    name = sys.argv[1]
    client = ScoringClient(name)
    print(client.get_highscores())
    print(client.get_myscores())
