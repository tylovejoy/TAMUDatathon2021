import open3d as o3d
import matplotlib.pyplot as plt
import numpy as np
import copy
from .transformation_matrix import TransformationMatrix
from .visualizer import visualizer
import os
from collections import namedtuple

DepthImage = namedtuple('DepthImage', ['gray', 'depth'])

# These are the bounds that we will transform the bolt
# from its home pose. Make sure you can handle anything in this range.
TRANFORM_BOUNDS = {
    'rotation': [0, 20, 20],
    'translation': [(0, 30), (-45, 45), (-20, 20)],
}

_DEFAULT_VIEW = {
    "field_of_view": 60.0,
    "front": [-1, 0, 0],
    "lookat": [0, 0, 0],
    "up": [0, 0, 1.0],
    "zoom": 1
}
visualizer.set_view(_DEFAULT_VIEW)
_pinhole_camera_parameters = \
    visualizer.vis.get_view_control().convert_to_pinhole_camera_parameters()

_PATH_HERE = os.path.dirname(__file__)
_bolt_mesh = o3d.io.read_triangle_mesh(os.path.join(_PATH_HERE, "bolt.stl"))
_bolt_mesh.compute_vertex_normals()
_bolt_mesh.compute_triangle_normals()


def get_random_transform() -> TransformationMatrix:
    return TransformationMatrix.make_random(
        TRANFORM_BOUNDS['rotation'], TRANFORM_BOUNDS['translation'])


def get_bolt_depthimage(transform=TransformationMatrix()) -> DepthImage:
    transformed = copy.deepcopy(_bolt_mesh).transform(transform)
    visualizer.draw_geometries(
        [transformed], view=_DEFAULT_VIEW, moveable=False)

    color = visualizer.vis.capture_screen_float_buffer(False)
    depth = visualizer.vis.capture_depth_float_buffer(False)
    visualizer.remove(transformed)
    visualizer.render()
    depthimage = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color, depth)
    # depth seems to gets read in /1000 (don't know why... camera intrinsics?)
    # so we adjust for that here
    depth = np.asarray(depthimage.depth) * 1000
    return DepthImage(np.asarray(depthimage.color), depth)


def show_depthimage(depthimage: DepthImage) -> None:
    plt.figure(figsize=(15, 15))
    plt.subplot(121)
    plt.title('Depth')
    plt.imshow(depthimage.depth)
    plt.subplot(122)
    plt.title('Grayscale')
    plt.imshow(depthimage.gray, cmap='gray')
    plt.show()


def make_pointcloud(depthimage: DepthImage) -> o3d.geometry.PointCloud:
    pcd = o3d.geometry.PointCloud()\
        .create_from_rgbd_image(
        o3d.geometry.RGBDImage.create_from_color_and_depth(
            o3d.geometry.Image(depthimage.gray),
            o3d.geometry.Image(depthimage.depth),
        ),
        _pinhole_camera_parameters.intrinsic,
        _pinhole_camera_parameters.extrinsic)

    # changing to pointcloud scales down.
    # don't know why... maybe camera intrinsics?
    center = pcd.get_center()
    pcd.translate(-center)
    pcd.scale(1000, np.zeros(3))
    pcd.translate(center*1000)
    # camera extrinsics should have captured the fact that the camera is x=-52
    # due to the zoom, but it doesn't for some reason. So we adjust for that here.
    return pcd.translate([-52.87, 0, 0])
