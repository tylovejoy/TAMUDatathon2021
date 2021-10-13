from transformation_matrix import TransformationMatrix
import numpy as np
import copy


def rmseT(g_est, g_gt):
    """
    Evaluation metric
    - rmseT: Root square mean error of transformation (rmseT) represents
    the root-mean-square error between estimated transformation g_{est}
    and ground truth transformation g_{gt}.
    """
    return np.sqrt(((g_est - g_gt) ** 2).mean())


def evaluate_random(estimator):
    transform_truth = TransformationMatrix.make_random()
    transformed = copy.deepcopy(bolt_rgbd).transform(transform_truth)
    transform_estimate = estimator(transformed)
    return rmseT(transform_truth, transform_estimate)


def evaluate_batch(estimator, count=100):
    return np.mean([evaluate_random(target) for _ in range(count)])


def _get_image():
    response = requests.get(endpoint + '/transformed_bolt_rgbd').data
    return response


def _post_estimates(estimates, myname):
    res = requests.post(endpoint + '/estimate', {
        'estimates': estimate,
        'myname': myname
    })
    return res.json()['mean_rmseT']


def evaluate_batch(estimator, myname):
    from threading import Pool
    threads = Pool(100)
    estimates = threads.map(_get_image) \
        .map(lambda res: {'estimate': estimator(res.image), 'id': res.id}) \
        .reduce(np.concatenate)
    mean_rmseT = _post_estimates(estimates, myname)
    return mean_rmseT
