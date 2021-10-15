from utility.transformation_matrix import TransformationMatrix
from utility.pose_data import get_bolt_depthimage, make_pointcloud
from utility.pose_estimation import transform_error, evaluate_random, evaluate_batch, make_submission
from scipy.spatial.transform import Rotation as R
import numpy as np


def baseline_estimator(orig_depthimage):
    orig_pcd = make_pointcloud(orig_depthimage)

    def fit_plane(pcd):
        plane_model, inliers = pcd.segment_plane(distance_threshold=0.01,
                                                 ransac_n=3,
                                                 num_iterations=1000)
        inlier_cloud = pcd.select_by_index(inliers)
        return plane_model, inlier_cloud

    def get_bolt_head(pcd):
        plane_model, inlier_cloud = fit_plane(pcd)
        normal = plane_model[:3]
        center = np.median(inlier_cloud, axis=0)
        return normal, center

    def rotation(orig_normal, trns_normal):
        vec = np.cross(orig_normal-trns_normal)
        unit = vec / np.linalg.norm(vec)
        rotvec = unit * np.dot(orig_normal-trns_normal)
        return R.from_rotvec(rotvec).as_matrix()

    def estimator(transformed_depthimage):
        trns_pcd = make_pointcloud(transformed_depthimage)

        orig_normal, src_center = get_bolt_head(orig_pcd)
        trns_normal, trns_center = get_bolt_head(trns_pcd)

        translation = trns_center - src_center
        return TransformationMatrix.compose(
            rotation(orig_normal, trns_normal), translation)

    return estimator


if __name__ == '__main__':
    transform = TransformationMatrix.from_xyzwpr([0, 10, 10, 90, 0, 0])
    untransformed = get_bolt_depthimage().depth
    transformed = get_bolt_depthimage(transform)
    # calculate rsmeT on my transformation estimate
    estimator = baseline_estimator(untransformed)
    estimate = estimator(transformed)
    loss = transform_error(estimate, transform)
    print(loss)
    # use utility function to do this
    loss = evaluate_random(estimator)
    # run evaluation on batch
    loss = evaluate_batch(estimator)

    # submit to server
    loss = make_submission(estimator)
