import numpy as np
import requests
import os
from collections import namedtuple
from tqdm import tqdm

DepthImage = namedtuple('DepthImage', ['gray', 'depth'])

_path_here = os.path.dirname(__file__)
_grays = np.load(os.path.join(_path_here, '../images/gray.npy'))
_depths = np.load(os.path.join(_path_here, '../images/depth.npy'))
test_images = [DepthImage(gray, depth) for gray, depth in zip(_grays, _depths)]


def transform_error(estimate, truth):
    """
    Evaluation metric
    - Root square mean error of the concatenated
    rotation (extrinsic euler in degrees) and translation
    """
    estimate = np.concatenate([estimate.rotation_euler, estimate.translation])
    truth = np.concatenate([truth.rotation_euler, truth.translation])
    return np.sqrt(((estimate - truth) ** 2).mean())


def evaluate_random(estimator):
    from utility.pose_data import get_bolt_depthimage, get_random_transform
    transform_truth = get_random_transform()
    transformed = get_bolt_depthimage(transform_truth)
    transform_estimate = estimator(transformed)
    return transform_error(transform_truth, transform_estimate)


def _post_estimates(estimates, myname):
    endpoint = 'http://138.197.220.122:8090/'
    res = requests.post(endpoint + f'pose/submit/{myname}', json={
        'estimates': estimates.tolist(),
    })
    return res.json()


def make_submission(estimates):
    import os
    username = os.getenv('DISCORD_USERNAME')
    if not username:
        raise Exception(
            'Please set the environment variable "DISCORD_USERNAME"')

    return _post_estimates(estimates, username)
