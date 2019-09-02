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

import sys

from config import DefaultSettings
from constants.event import GraphicSettingsChangeEvent
from constants.overlay import OverlayMode, OverlayPosition
from gui.model import OverlayModel
from patterns.factory import OverlayFactory
from patterns.observer import Subscriber
from patterns.singleton import Singleton

from .overlay import Overlay
from .writable_overlay import WritableOverlay

class OverlayManager(metaclass=Singleton):
    """
    """
    def __init__(self, launcher, initial_settings=None):
        self.launcher = launcher

        graphic_settings_publisher = (
            self.launcher.game_state.graphic_settings_publisher
        )
        subscriber = Subscriber()
        graphic_settings_publisher.register(
            GraphicSettingsChangeEvent.RESOLUTION, subscriber,
            self.__resolution_change
        )
        graphic_settings_publisher.register(
            GraphicSettingsChangeEvent.SCREEN_MODE, subscriber,
            self.__screen_mode_change
        )
        graphic_settings_publisher.register(
            GraphicSettingsChangeEvent.POSITION, subscriber,
            self.__position_change
        )

        self.overlay_factory = OverlayFactory()
        self.overlays = dict()

        sys.stdout.callback = self.write_to_overlay

        self.current_theme = None

        self.tekken_position = None
        self.tekken_resolution = None
        self.tekken_screen_mode = None

        self.current_overlay: Overlay
        self.current_overlay = None

        self.overlay_model = OverlayModel()

        self.overlay_enabled = False

        self.reloadable_initial_settings = initial_settings
        self.reload()

    def enable_automatic_overlay_hide(self, enable):
        for overlay_id in self.overlays:
            self.overlays[overlay_id].set_automatic_hide(enable)

    def enable_overlay(self, enable):
        self.overlay_enabled = enable
        self.current_overlay.set_enable(self.overlay_enabled)

    def change_overlay(self, mode: OverlayMode):
        sys.stdout.write('Turning overlay off')
        self.current_overlay.set_enable(False)
        self.overlays[self.current_overlay.__class__.CLASS_ID] = (
            self.current_overlay
        )
        change_overlay = self.overlays.get(mode.value)
        if not change_overlay:
            sys.stdout.write('creating new overlay')
            change_overlay = self.__add_overlay(mode.value)
        sys.stdout.write('changing overlay')
        self.current_overlay = change_overlay
        sys.stdout.write('Turning overlay on')
        if self.overlay_enabled:
            self.current_overlay.set_enable(True)

    def change_overlay_position(self, position):
        for overlay_id in self.overlays:
            self.overlays[overlay_id].set_position(position)

    def change_overlay_theme(self, theme_dict):
        for overlay_id in self.overlays:
            self.overlays[overlay_id].set_theme(theme_dict)

    def reload(self):
        if self.reloadable_initial_settings:
            initial_settings = self.reloadable_initial_settings.config[
                'DEFAULT'
            ]
        else:
            initial_settings = DefaultSettings.SETTINGS['DEFAULT']

        if self.current_overlay:
            self.current_overlay.set_enable(False)
            self.change_overlay(
                OverlayMode[initial_settings.get('overlay_mode')]
            )
        else:
            self.current_overlay = self.__add_overlay(
                OverlayMode[initial_settings.get('overlay_mode')].value
            )
        self.change_overlay_position(
            OverlayPosition[initial_settings.get('overlay_position')]
        )
        self.change_overlay_theme(
            self.overlay_model.get_theme(
                self.overlay_model.get_index_by_filename(
                    initial_settings.get('overlay_theme')
                )
            )
        )
        self.set_framedata_overlay_column_settings(
            initial_settings.get('framedata_overlay_columns')
        )
        self.enable_automatic_overlay_hide(
            initial_settings.get('overlay_automatic_hide')
        )
        self.enable_overlay(initial_settings.get('overlay_enable'))

    def set_framedata_overlay_column_settings(self, column_settings):
        frame_data_overlay = self.overlays.get(OverlayMode.FRAMEDATA.value)
        if not frame_data_overlay:
            frame_data_overlay = self.__add_overlay(OverlayMode.FRAMEDATA.value)
        frame_data_overlay.set_display_columns(column_settings)

    def write_to_overlay(self, string):
        if(
                isinstance(self.current_overlay, WritableOverlay)
                and self.current_overlay.enabled
        ):
            self.current_overlay.write(string)

    def __add_overlay(self, overlay_id):
        self.overlays[overlay_id] = self.overlay_factory.create_class(
            overlay_id, self.launcher
        )
        if self.tekken_screen_mode:
            self.overlays[overlay_id].set_tekken_screen_mode(
                self.tekken_screen_mode
            )
        if self.tekken_resolution:
            self.overlays[overlay_id].set_tekken_resolution(
                self.tekken_resolution
            )
        if self.tekken_position:
            self.overlays[overlay_id].set_tekken_position(self.tekken_position)

        if self.current_overlay:
            self.overlays[overlay_id].copy_settings_from_overlay(
                self.current_overlay
            )

        return self.overlays[overlay_id]

    def __position_change(self, position):
        self.tekken_position = position
        for overlay in self.overlays.values():
            overlay.set_tekken_position(position)

    def __resolution_change(self, resolution):
        self.tekken_resolution = resolution
        for overlay in self.overlays.values():
            overlay.set_tekken_resolution(resolution)

    def __screen_mode_change(self, screen_mode):
        self.tekken_screen_mode = screen_mode
        for overlay in self.overlays.values():
            overlay.set_tekken_screen_mode(screen_mode)
