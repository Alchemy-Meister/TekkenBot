#!/usr/bin/env python3

# Copyright (c) 2019, Alchemy Meister
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice,this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
"""
from abc import ABC, abstractmethod
import math
import platform
import tkinter as tk
import tkinter.font as tkfont

from config import DefaultSettings
from constants.graphic_settings import ScreenMode
from constants.overlay import OverlayPosition
from patterns.observer import Subscriber
from tekken import Launcher
from win32.utils import mouse

class Overlay(ABC):
    """
    """
    WIDTH = 2560
    HEIGHT = 1440
    TRANSPARENCY_CAPABLE = not 'Windows-7' in platform.platform()

    def __init__(self, launcher: Launcher):
        self.launcher = launcher

        self.automatic_hide = DefaultSettings.SETTINGS['DEFAULT'].get(
            'overlay_automatic_hide'
        )
        self.coordinates = {
            'x': 0, 'y': 0, 'width': 0, 'height': 0
        }
        self.window_dimensions = [0, 0]
        self.window_proportion = None

        self.coordinates_initialized = False
        self.dimensions_initialized = False
        self.visible = False
        self.enabled = False
        self.is_draggable = False

        self.is_resizing = True
        self.resize_start = True
        self.skip_resize_event = False
        self.previous_event = None

        self.transparent_color = 'white'

        self.tekken_screen_mode = None
        self.tekken_resolution = None
        self.tekken_position = None

        self.overlay_scale = None
        self._tekken_scale = None
        self.__tekken_rect = None

        self.previous_position = None
        self.position = None

        self.overlay = tk.Toplevel(width=0, height=0)
        self.overlay.withdraw()

        self.set_position(OverlayPosition.TOP)

        self.overlay.attributes('-topmost', True)
        self.overlay.protocol('WM_DELETE_WINDOW', self.__on_delete_window)
        self.overlay.bind('<Configure>', self._on_resize_window)

        subscriber = Subscriber()

        launcher.publisher.register(
            Launcher.Event.INITIALIZED,
            subscriber,
            self.__set_initialization_flag
        )
        launcher.publisher.register(
            Launcher.Event.UPDATED, subscriber, self.__update
        )
        launcher.publisher.register(
            Launcher.Event.CLOSED, subscriber, self.__stop
        )

    def __repr__(self):
        return '{}(position = {}, previous_position = {})'.format(
            self.__class__.__name__, self.position, self.previous_position
        )

    def set_settings(self, automatic_hide, position, previous_position):
        self.set_position(position)
        self.previous_position = previous_position
        self.set_automatic_hide(automatic_hide)

    def set_settings_from_overlay(self, other_overlay):
        previous_settings = (
            self.automatic_hide, self.position, self.previous_position
        )
        self.set_position(other_overlay.position)
        self.previous_position = other_overlay.previous_position
        self.set_automatic_hide(other_overlay.automatic_hide)
        return previous_settings

    def set_automatic_hide(self, enable):
        if enable != self.automatic_hide:
            self.automatic_hide = enable
            if enable:
                self.visible = True

    def set_enable(self, enable):
        if enable != self.enabled:
            self.enabled = enable
            if not self.enabled:
                self.__hide()

    def set_position(self, position):
        if position != self.position:
            was_draggable = self.position == OverlayPosition.DRAGGABLE
            self.position = position

            self.is_draggable = self.position == OverlayPosition.DRAGGABLE
            Overlay.__set_cursor_to_all_widgets(
                self.overlay, '' if self.is_draggable else 'none'
            )
            self.overlay.overrideredirect(not self.is_draggable)
            self.overlay.wm_attributes('-topmost', not self.is_draggable)

            if Overlay.TRANSPARENCY_CAPABLE:
                self.overlay.wm_attributes(
                    '-transparentcolor',
                    '' if self.is_draggable else self.transparent_color
                )
                self.overlay.attributes(
                    '-alpha', '1' if self.is_draggable else '0.75'
                )

            try:
                if was_draggable and not self.is_draggable:
                    self._resize_overlay_widgets()
                    self._update_dimensions()
                self._update_position(self.tekken_position)
            except (TypeError, AttributeError):
                pass
        elif self.previous_position:
            self.previous_position = self.position


    def set_tekken_screen_mode(self, screen_mode):
        self.tekken_screen_mode = screen_mode
        if screen_mode == ScreenMode.FULLSCREEN:
            if self.position != OverlayPosition.DRAGGABLE:
                self.previous_position = self.position
                self.set_position(OverlayPosition.DRAGGABLE)
        elif self.previous_position is not None:
            self.set_position(self.previous_position)
            self.previous_position = None

    def set_tekken_resolution(self, resolution):
        self.tekken_resolution = resolution
        self._tekken_scale = Overlay.__calculate_scale(
            resolution,
            [Overlay.WIDTH, Overlay.HEIGHT]
        )
        self.is_resizing = True
        self._resize_overlay_widgets()
        self.is_resizing = False
        self._update_dimensions()

    def set_tekken_position(self, position):
        self.tekken_position = position
        self._update_position(position)

    def set_theme(self, theme_dict):
        self.transparent_color = theme_dict.get('transparent')

    def _on_resize_window(self, event):
        if(
                self.is_draggable
                and self.coordinates_initialized
                and self.previous_event
                and not self.skip_resize_event
                and not self.is_resizing
        ):
            if(
                    (
                        self.previous_event.width != event.width
                        or self.previous_event.height != event.height
                    )
                    and event.width
                    and event.height
            ):
                self.window_dimensions[0] = event.width
                self.window_dimensions[1] = (
                    event.width / self.window_proportion
                )

                self.overlay_scale = Overlay.__calculate_scale(
                    [self.window_dimensions[0], self.window_dimensions[1]],
                    [self.coordinates['width'], self.coordinates['height']]
                )
                self.is_resizing = True
                width, height = self._resize_overlay_widgets(
                    overlay_scale=self.overlay_scale
                )
                self.window_dimensions[0] = width
                self.window_dimensions[1] = round(height)
                self.is_resizing = False
                if self.resize_start:
                    self.resize_start = False
                    self.overlay.after(100, self.__force_resize_proportion)

        self.previous_event = event
        if self.skip_resize_event:
            self.skip_resize_event = False

    @abstractmethod
    def _resize_overlay_widgets(self, overlay_scale=None):
        pass

    def _set_dimensions(self, width, height):
        self.coordinates['width'] = width
        self.coordinates['height'] = height

    @abstractmethod
    def _update_dimensions(self):
        pass

    def _update_position(self, tekken_position):
        if not self.is_draggable or not self.coordinates_initialized:
            self.coordinates['x'] = math.ceil(
                tekken_position[0]
                + self.tekken_resolution[0]
                / 2
                - self.coordinates['width']
                / 2
            )
            game_reader = self.launcher.game_state.get_reader()
            # Prevents misbehavior with using borderless-gaming like software.
            if not game_reader.is_tekken_fullscreen():
                tekken_position_y = (
                    tekken_position[1] + game_reader.get_titlebar_height()
                )
            else:
                tekken_position_y = tekken_position[1]
            if self.position == OverlayPosition.TOP:
                self.coordinates['y'] = tekken_position_y
            elif self.position == OverlayPosition.BOTTOM:
                self.coordinates['y'] = (
                    tekken_position_y
                    + self.tekken_resolution[1]
                    - self.coordinates['height']
                )
            self.overlay.geometry(
                '+{}+{}'.format(
                    self.coordinates['x'],
                    self.coordinates['y']
                )
            )
            self.coordinates_initialized = True

    @abstractmethod
    def _update_state(self):
        pass

    @abstractmethod
    def _update_visible_state(self):
        pass

    @staticmethod
    def _get_fitting_font(scale, font, text, max_font_width, max_font_height):
        def get_font_and_measures(font, size):
            font = tkfont.Font(
                family=font[0],
                size=size
            )
            width, height = Overlay._get_font_text_dimensions(
                font, text
            )
            return font, width, height

        size = math.ceil(font[1] * scale[0])
        sign = (1, -1)[size < 0]
        if not size:
            size = sign

        fitting_font, width, height = get_font_and_measures(font, size)
        while(
                (
                    width > max_font_width
                    or height > max_font_height
                )
                and abs(size) > abs(sign)
        ):
            fitting_font, width, height = get_font_and_measures(font, size)
            size = sign * (abs(size) - 1)

        return fitting_font, width, height

    @staticmethod
    def _get_font_text_dimensions(font, text):
        width = font.measure(text)
        height = font.metrics('linespace')
        return width, height

    def __force_resize_proportion(self):
        if not mouse.is_logical_left_button_down():
            self.overlay.after(
                1000,
                lambda: self.overlay.geometry(
                    '{}x{}'.format(*self.window_dimensions)
                )
            )
            self.resize_start = True
            self.skip_resize_event = True
        else:
            self.overlay.after(100, self.__force_resize_proportion)

    def __hide(self):
        self.visible = False
        self.overlay.withdraw()

    def __on_delete_window(self):
        pass

    def __set_initialization_flag(self):
        if self.coordinates['width'] and self.coordinates['height']:
            self.dimensions_initialized = True

    def __show(self):
        self.visible = True
        self.overlay.deiconify()

    def __stop(self):
        self.dimensions_initialized = False
        self.__hide()

    def __update(self, is_state_updated):
        if self.enabled:
            game_reader = self.launcher.game_state.get_reader()
            if(
                    self.coordinates_initialized
                    and self.dimensions_initialized
                    and (
                        self.is_draggable
                        or game_reader.is_tekken_foreground_wnd()
                    )
            ):
                previous_visible_state = self.visible
                self._update_visible_state()
                if(
                        previous_visible_state != self.visible
                    ):
                    if self.visible:
                        self.__show()
                    else:
                        self.__hide()
            else:
                self.__hide()
            if is_state_updated:
                self._update_state()

    @staticmethod
    def __calculate_scale(current_size, original_size):
        return (
            current_size[0] / original_size[0],
            current_size[1] / original_size[1]
        )

    @staticmethod
    def __set_cursor_to_all_widgets(frame, cursor):
        for child in frame.winfo_children():
            child.configure(cursor=cursor)
            if isinstance(child, tk.Frame):
                Overlay.__set_cursor_to_all_widgets(child, cursor)
