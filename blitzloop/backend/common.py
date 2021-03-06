#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012-2017 Hector Martin "marcan" <hector@marcansoft.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 or version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import time

from blitzloop.matrix import Matrix
from blitzloop import graphics

class BaseDisplay(object):
    BLACK = (0.0, 0.0, 0.0, 1.0)
    TRANSPARENT = (0.0, 0.0, 0.0, 0.0)
    def __init__(self, width=640, height=480, fullscreen=False, aspect=None):
        self.kbd_handler = None
        self.exit_handler = None
        self.should_exit = False
        self.win_width = self.width = width
        self.win_height = self.height = height
        self.cache_win = None
        self.aspect_cache = None
        self.matrix = Matrix()
        self.set_aspect(aspect)
        self.clear_color = self.BLACK
        self.cleanup = None
        self.fullscreen = fullscreen
        self.fps = None

    def toggle_fullscreen(self):
        pass

    def set_aspect(self, aspect):
        if not aspect:
            aspect = self.win_width / self.win_height
        self.aspect = aspect

        if self.cache_win != (self.win_width, self.win_height):
            self.aspect_cache = {}
            self.cache_win = (self.win_width, self.win_height)
        if aspect in self.aspect_cache:
            self.viewmatrix, self.width, self.height = self.aspect_cache[aspect]
            return

        display_aspect = self.win_width / self.win_height
        if display_aspect > self.aspect:
            self.width = int(round(self.aspect * self.win_height))
            self.height = self.win_height
        else:
            self.width = self.win_width
            self.height = int(round(self.win_width / self.aspect))
        off_x = int((self.win_width - self.width) / 2)
        off_y = int((self.win_height - self.height) / 2)

        matrix = Matrix()
        matrix.translate(-1.0, -1.0)
        matrix.scale(2.0/self.win_width, 2.0/self.win_height)
        matrix.translate(off_x, off_y, 0)
        matrix.scale(self.width, self.width, 1)
        self.viewmatrix = matrix
        self.aspect_cache[self.aspect] = matrix, self.width, self.height

    def commit_matrix(self, uniform):
        m = self.viewmatrix * self.matrix
        self.gl.glUniformMatrix4fv(uniform, 1, False, m.m)

    def set_render_gen(self, gen):
        self.frames = gen()

    def set_keyboard_handler(self, f):
        self.kbd_handler = f

    def set_exit_handler(self, f):
        self.exit_handler = f

    def queue_exit(self):
        self.should_exit = True

    def do_exit(self):
        if self.exit_handler:
            eh = self.exit_handler
            self.exit_handler = None
            eh()

    def _initialize(self):
        # Set up common GL state
        self.gl.glActiveTexture(self.gl.GL_TEXTURE0)
        self.gl.glBlendFunc(self.gl.GL_ONE, self.gl.GL_ONE_MINUS_SRC_ALPHA)
        self.gl.glEnable(self.gl.GL_BLEND)

    def _render(self):
        self.matrix.reset()

        self.gl.glClearColor(*self.clear_color)
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        next(self.frames)
        graphics.get_renderer().cleanup()

    def main_loop(self):
        while True:
            try:
                self.st = self.lt = time.time()
                self._render()
            except StopIteration:
                break
            self.swap_buffers()

    def log(self, msg):
        t = time.time()
        print("[%5.02f %5.02f] %s" % (
            (t - self.st) * 1000,
            (t - self.lt) * 1000,
            msg))
        self.lt = t

    def round_coord(self, c):
        return int(round(c * self.width)) / self.width

    @property
    def top(self):
        return self.height / self.width

    def get_mpv_params(self):
        return {}
