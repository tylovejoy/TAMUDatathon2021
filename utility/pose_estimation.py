from .transformation_matrix import TransformationMatrix
import numpy as np
import requests
from collections import namedtuple
from utility.pose_data import TRANFORM_BOUNDS, get_bolt_depthimage, get_random_transform

ImageResponse = namedtuple('ImageResponse', ['color', 'depth', 'image_id'])


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
    transform_truth = get_random_transform()
    transformed = get_bolt_depthimage(transform_truth)
    transform_estimate = estimator(transformed)
    return transform_error(transform_truth, transform_estimate)


def evaluate_batch(estimator, count=100):
    return np.mean([evaluate_random(estimator) for _ in range(count)])


def _get_image():
    endpoint = 'http://138.197.220.122:8090/'
    response = requests.get(
        endpoint + 'pose/transformed_bolt_depthimage/').json()
    print(response)
    return ImageResponse(
        np.array(response[0]),
        np.array(response[1]),
        response[2]
    )


def _post_estimates(estimates, myname):
    endpoint = 'http://138.197.220.122:8090/'
    res = requests.post(endpoint + 'pose/estimate/', {
        'estimates': estimates,
        'name': myname
    })
    return res.json()['mean_rmseT']


def make_submission(estimator):
    import os
    username = os.getenv('DISCORD_USERNAME')
    if not username:
        raise Exception(
            'Please set the environment variable "DISCORD_USERNAME"')

    estimates = []
    for _ in range(10):
        img = _get_image()
        estimate = estimator(img)
        estimates.append(
            {'estimate': estimate.to_list(), 'image_id': img.image_id})
    mean_rmseT = _post_estimates(estimates, username)
    return mean_rmseT
