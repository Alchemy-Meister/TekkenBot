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

from constants.overlay import OverlayPosition
from patterns.observer import Subscriber
from tekken import Launcher
from win32.user32 import Rect
from win32.utils import mouse

class Overlay(ABC):
    """
    """
    WIDTH = 2560
    HEIGHT = 1440
    TRANSPARENCY_CAPABLE = not 'Windows-7' in platform.platform()

    def __init__(self, launcher: Launcher):
        self.launcher = launcher
        self._tekken_scale = None
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

        self.is_resizing = False
        self.resize_start = True
        self.skip_resize_event = False
        self.previous_event = None

        self.transparent_color = 'white'

        self.__tekken_rect = None
        self.__position = None

        self.overlay = tk.Toplevel(width=0, height=0)
        self.overlay.withdraw()

        self.set_position(OverlayPosition.TOP)

        self.overlay.attributes('-topmost', True)
        self.overlay.protocol('WM_DELETE_WINDOW', self.__on_delete_window)
        self.overlay.bind('<Configure>', self._on_resize_window)

        subscriber = Subscriber()
        launcher.publisher.register(
            Launcher.Event.UPDATED, subscriber, self.__update
        )
        launcher.publisher.register(
            Launcher.Event.CLOSED, subscriber, self.__stop
        )

    def on(self):
        self.enabled = True

    def off(self):
        self.enabled = False
        self.hide()

    def set_position(self, position):
        self.__position = position

        self.is_draggable = self.__position == OverlayPosition.DRAGGABLE
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
            self.is_resizing = True
            self.__update_coordinates(force_update=True)
            self.is_resizing = False
        except AttributeError:
            pass

    def set_theme(self, theme_dict):
        self.transparent_color = theme_dict.get('transparent')

    def hide(self):
        self.visible = False
        self.overlay.withdraw()

    def show(self):
        self.visible = True
        self.overlay.deiconify()

    def _set_dimensions(self, width, height):
        self.coordinates['width'] = width
        self.coordinates['height'] = height

    def __update(self, is_state_updated):
        if self.enabled:
            success = self.__update_coordinates()
            if self.coordinates_initialized and success:
                previous_visible_state = self.visible
                self._update_visible_state()
                if(
                        previous_visible_state != self.visible
                    ):
                    if self.visible:
                        self.show()
                        self.overlay.focus_force()
                    else:
                        self.hide()
            else:
                self.hide()
            if is_state_updated:
                self._update_state()

    def __on_delete_window(self):
        pass

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
                self.window_dimensions[1] = round(
                    event.width / self.window_proportion
                )

                overlay_scale = Overlay.__calculate_scale(
                    [self.window_dimensions[0], self.window_dimensions[1]],
                    [self.coordinates['width'], self.coordinates['height']]
                )
                self.is_resizing = True
                width, height = self._resize_overlay_widgets(
                    overlay_scale=overlay_scale
                )
                self.window_dimensions[0] = width
                self.window_dimensions[1] = height
                self.is_resizing = False
                if self.resize_start:
                    self.resize_start = False
                    self.overlay.after(100, self.force_resize_proportion)

        self.previous_event = event
        if self.skip_resize_event:
            self.skip_resize_event = False

    def force_resize_proportion(self):
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
            self.overlay.after(100, self.force_resize_proportion)

    @abstractmethod
    def _resize_overlay_widgets(self, overlay_scale=None):
        pass

    def __update_coordinates(self, force_update=False):
        tekken_rect = (
            self.launcher.game_state.get_reader().get_tekken_window_rect(
                foreground_only=(
                    self.dimensions_initialized
                    and not self.is_draggable
                    and not force_update
                )
            )
        )
        if tekken_rect:
            if self.__tekken_rect != tekken_rect or force_update:
                self.dimensions_initialized = True
                self.__tekken_rect = tekken_rect

                updated_scale = Overlay.__calculate_scale(
                    [tekken_rect.width, tekken_rect.height],
                    [Overlay.WIDTH, Overlay.HEIGHT]
                )
                if self._tekken_scale != updated_scale or force_update:
                    self._tekken_scale = updated_scale
                    self._resize_overlay_widgets()
                    self._update_dimensions()
                if not self.is_draggable or not self.coordinates_initialized:
                    self.__update_location(tekken_rect=tekken_rect)

                if self.is_draggable and self.coordinates_initialized:
                    self.overlay.geometry(
                        '{}x{}'.format(
                            self.coordinates['width'],
                            self.coordinates['height']
                        )
                    )
                else:
                    self.overlay.geometry(
                        '{}x{}+{}+{}'.format(
                            self.coordinates['width'],
                            self.coordinates['height'],
                            self.coordinates['x'],
                            self.coordinates['y']
                        )
                    )
                    self.coordinates_initialized = True
            return True
        return False

    def __update_location(self, tekken_rect: Rect):
        self.coordinates['x'] = math.ceil(
            (tekken_rect.left + tekken_rect.right) / 2
            - self.coordinates['width'] / 2
        )
        if self.__position == OverlayPosition.TOP:
            self.coordinates['y'] = tekken_rect.top
        elif self.__position == OverlayPosition.BOTTOM:
            self.coordinates['y'] = (
                tekken_rect.bottom - self.coordinates['height']
            )

    @abstractmethod
    def _update_dimensions(self):
        pass

    @abstractmethod
    def _update_visible_state(self):
        pass

    @abstractmethod
    def _update_state(self):
        pass

    def __stop(self):
        self.dimensions_initialized = False
        self.coordinates_initialized = False

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

    @staticmethod
    def _get_font_text_dimensions(font, text):
        width = font.measure(text)
        height = font.metrics('linespace')
        return width, height

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
