from typing import List
import numpy as np
import requests
import os
from collections import namedtuple
from typing import Callable

from utility.transformation_matrix import TransformationMatrix
from .scoring_client import _get_username

DepthImage = namedtuple('DepthImage', ['gray', 'depth'])

try:
  _path_here = os.path.dirname(__file__)
  _grays = np.load(os.path.join(_path_here, '../images/gray.npy'))
  _depths = np.load(os.path.join(_path_here, '../images/depth.npy'))
  test_images = [DepthImage(gray, depth) for gray, depth in zip(_grays, _depths)]
except:
  raise Exception('Please download the pose data from shorturl.at/lrKL8 and put the two files in the images folder')
  

def transform_error(estimate: TransformationMatrix, truth: TransformationMatrix) -> float:
    """
    Evaluation metric
    - Root square mean error of the concatenated
    rotation (extrinsic euler in degrees) and translation
    """
    estimate = np.concatenate([estimate.rotation_euler, estimate.translation])
    truth = np.concatenate([truth.rotation_euler, truth.translation])
    return np.sqrt(((estimate - truth) ** 2).mean())


def evaluate_random(estimator: Callable[[DepthImage], TransformationMatrix]) -> float:
    from utility.pose_data import get_bolt_depthimage, get_random_transform
    transform_truth = get_random_transform()
    transformed = get_bolt_depthimage(transform_truth)
    transform_estimate = estimator(transformed)
    return transform_error(transform_truth, transform_estimate)


class SubmissionResult:
    def __init__(self, json_response) -> None:
        self.mean_error = json_response['mean_error']
        self.ranking = json_response['ranking']

    def __str__(self):
        return f'Mean rmse={self.mean_error:.4f}\n'\
               f'Your ranking: #{self.ranking}'

    def __repr__(self) -> str:
        return self.__str__()


def make_submission(estimates: List[TransformationMatrix]) -> SubmissionResult:
    endpoint = 'http://138.197.220.122:8090/'
    res = requests.post(endpoint + f'pose/submit/{_get_username()}', json={
        'estimates': estimates.tolist(),
    })
    return SubmissionResult(res.json())
