import os
import time
from typing import List
import open3d as o3d
import shutil


def make_new_dir(path, delete_old=False):
    if delete_old and os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


class _Visualizer:
    """
    Non-blocking stateful visualizer (can add, update and remove geometries).
    Will keep a window open until you delete the instance.
    """

    def __init__(self, view=None, img_save_path=None, visible=True):
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(visible=visible)
        self._view = view
        self._img_save_path = img_save_path
        if img_save_path:
            make_new_dir(img_save_path, delete_old=True)
        self.geometries = dict()

    def __del__(self):
        print('destroying visualizer')
        self.vis.destroy_window()

    def _vis_loop(self):
        while True:
            self.render()
            time.sleep(.01)

    def render(self):
        self.vis.poll_events()
        self.vis.update_renderer()

    def add(self, geometry):
        self.geometries[geometry] = geometry
        self.vis.add_geometry(geometry)

    def update(self, geometry):
        self.vis.update_geometry(geometry)

    def remove(self, geometry):
        self.vis.remove_geometry(geometry)

    def draw_geometries(self, new_geometries: List[o3d.geometry.Geometry], view: dict=None, moveable=False):
        """
        This should be the only function you need. Pass in a list of geometries to visualize them.
        Pass in a custom view if you want to view from a different angle. 
        Set moveable to True if you want to be able to jog/rotate the camera via click and drag. 
        If True, the window will block your program until you do a keyboard interrupt.
        If False, the window will not block but you will not be able to move the camera. 
        """
        for g in new_geometries:
            if g in self.geometries:
                self.update(g)
            else:
                self.add(g)
        # remove anything we are currently displaying that isn't in new_geometries
        updated = dict()
        for g in self.geometries:
            if g in new_geometries:
                updated[g] = g
            else:
                self.remove(self.geometries[g])
        self.geometries = updated
        view = view or self._view
        if view:
            self.set_view(view)
        self.render()
        if moveable:
            print('Press ctrl+c to stop (or press interrupt if in jupyter)')
            try:
                self._vis_loop()
            except KeyboardInterrupt:
                pass

    def set_view(self, config):
        view = self.vis.get_view_control()
        view.set_up(config['up'])
        view.set_zoom(config['zoom'])
        view.set_lookat(config['lookat'])
        view.set_front(config['front'])

    def save_img(self, override_path=None):
        if override_path:
            path = override_path
        elif self._save_img_path:
            nfiles = len(os.listdir(self._save_img_path))
            path = os.path.join(self._save_img_path, f'img_{nfiles}.jpg')
        else:
            raise Exception('No save path provided')
        self.vis.capture_screen_image(path)


# singleton
# don't instantiate yourself. Use this instance.
print('Instantiating visualizer')

_DEFAULT_VIEW = {
    "field_of_view": 60.0,
    "front": [-1, 0, 0],
    "lookat": [0, 0, 0],
    "up": [0, 0, 1.0],
    "zoom": 1
}

visualizer = _Visualizer(view=_DEFAULT_VIEW, visible=True)
