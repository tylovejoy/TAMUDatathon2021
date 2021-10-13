from utility.transformation_matrix import TransformationMatrix
from utility.data import get_bolt_rgbd
import numpy as np
import copy


def _baseline_estimater(source, target):
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

    def rotation():
        vec = np.cross(src_normal-tgt_normal)
        unit = vec / np.linalg.norm(vec)
        rotvec = unit * np.dot(src_normal-tgt_normal)
        return R.from_rotvec(rotvec).as_matrix()

    src_normal, src_center = get_bolt_head(source)
    tgt_normal, tgt_center = get_bolt_head(target)

    translation = tgt_center - src_center
    return TransformationMatrix.compose(rotation(), translation)


if __name__ == '__main__':
    transform = TransformationMatrix.make_random(10, [0, 30, 20])
    untransformed = get_bolt_rgbd().depth
    transformed = get_bolt_rgbd(transform)

