import os
import threading
import time
import keyboard

import open3d as o3d

from robotorque.utility.positioned_frame import PositionedFrame

from ovis.utility.file import make_new_dir

# from multiprocessing import Process, Lock
from threading import Lock, Thread
class Visualizer:
    """
    Non-blocking stateful visualizer (can add, update and remove geometries).
    """
    def __init__(self, view=None, img_save_path=None):
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window()
        self._view = view
        self._img_save_path = img_save_path
        if img_save_path:
            make_new_dir(img_save_path, delete_old=True)
        self.geometries = dict()

    def __del__(self):
        print('calling destructer')
        self.vis.destroy_window()

    def _vis_loop(self):
        while True:
            if keyboard.is_pressed('q'):
                break
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

    def draw_geometries(self, new_geometries, view=None):
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
        self._vis_loop()

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
