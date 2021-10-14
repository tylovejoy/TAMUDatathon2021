from utility.transformation_matrix import TransformationMatrix
from utility.pose_data import get_bolt_rgbd, make_pointcloud
from utility.pose_estimation import rmseT, evaluate_random, evaluate_batch, evaluate_remote
from scipy.spatial.transform import Rotation as R
import numpy as np


def baseline_estimator(orig_rgbd):
    orig_pcd = make_pointcloud(orig_rgbd)

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

    def estimator(transformed_rgbd):
        trns_pcd = make_pointcloud(transformed_rgbd)

        orig_normal, src_center = get_bolt_head(orig_pcd)
        trns_normal, trns_center = get_bolt_head(trns_pcd)

        translation = trns_center - src_center
        return TransformationMatrix.compose(
            rotation(orig_normal, trns_normal), translation)

    return estimator


if __name__ == '__main__':
    transform = TransformationMatrix.from_xyzwpr(0,10,10,90,0,0)
    untransformed = get_bolt_rgbd().depth
    transformed = get_bolt_rgbd(transform)
    # calculate rsmeT on my transformation estimate
    estimator = baseline_estimator(untransformed)
    estimate = estimator(transformed)
    loss = rmseT(estimate, transform)
    print(loss)
    # use utility function to do this
    loss = evaluate_random(estimator)
    # run evaluation on batch
    loss = evaluate_batch(estimator)
    
    # submit to server
    loss = evaluate_remote(estimator)