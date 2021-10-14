import open3d as o3d
import matplotlib.pyplot as plt
import numpy as np
import copy
from .transformation_matrix import TransformationMatrix
from .visualizer import visualizer
import os

DEFAULT_VIEW = {
    "field_of_view" : 60.0,
    "front" : [ -1, 0, 0 ],
    "lookat" : [ 0, 0, 0 ],
    "up" : [ 0, 0, 1.0 ],
    "zoom" : 1
}

# These are the bounds that we will transform the bolt
# from its home pose. Make sure you can handle anything in this range.
TRANFORM_BOUNDS = {
  'rotation': [10, 10, 10],
  'translation': [0, 30, 20],
}


_pinhole_camera_parameters = visualizer.vis.get_view_control().convert_to_pinhole_camera_parameters()

_PATH_HERE = os.path.dirname(__file__)
_bolt_mesh = o3d.io.read_triangle_mesh(os.path.join(_PATH_HERE, "bolt.stl"))
_bolt_mesh.compute_vertex_normals()
_bolt_mesh.compute_triangle_normals()


def get_random_transform():
  return TransformationMatrix.make_random(
    TRANFORM_BOUNDS['rotation'], TRANFORM_BOUNDS['translation'])


def get_bolt_rgbd(transform=TransformationMatrix()):
    transformed = copy.deepcopy(_bolt_mesh).transform(transform)
    visualizer.draw_geometries([transformed], view=DEFAULT_VIEW, moveable=False)

    color = visualizer.vis.capture_screen_float_buffer(False)
    depth = visualizer.vis.capture_depth_float_buffer(False)
    visualizer.remove(transformed)
    visualizer.render()
    return o3d.geometry.RGBDImage.create_from_color_and_depth(color, depth)


def show_rgbd(rgbd):
    plt.figure(figsize=(15,15))
    plt.subplot(121)
    plt.title('Depth')
    plt.imshow(np.asarray(rgbd.depth))
    plt.subplot(122)
    plt.title('Color')
    plt.imshow(np.asarray(rgbd.color))
    plt.show()


def make_pointcloud(depth):
    return o3d.geometry.PointCloud()\
           .create_from_depth_image(
               depth,
               _pinhole_camera_parameters.intrinsic,
               _pinhole_camera_parameters.extrinsic)
