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
from constants.overlay import OverlayMode, OverlayPosition, OverlayLayout
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

        sys.stdout.callback = self.write_to_overlays

        self.current_theme = None

        self.tekken_position = None
        self.tekken_resolution = None
        self.tekken_screen_mode = None

        self.current_overlay: Overlay
        self.current_overlay = None

        self.overlay_model = OverlayModel()

        self.overlays_enabled = False

        self.active_slots = 0
        self.overlay_slots = [None] * list(OverlayLayout).pop().value

        self.reloadable_initial_settings = initial_settings
        self.reload()

    def enable_automatic_overlay_hide(self, enable):
        for overlay_id in self.overlays:
            self.overlays[overlay_id].set_automatic_hide(enable)

    def enable_overlays(self, enable):
        self.overlays_enabled = enable
        for slot_index in range(self.active_slots):
            self.overlays[self.overlay_slots[slot_index]].set_enable(
                self.overlays_enabled
            )

    def change_overlay_layout(self, layout):
        if self.active_slots < layout.value:
            min_value = self.active_slots
            max_value = layout.value
            enable = True
        else:
            min_value = layout.value
            max_value = self.active_slots
            enable = False
        for turn_id in self.overlay_slots[min_value:max_value]:
            self.overlays[turn_id].set_enable(enable)
        self.active_slots = layout.value

    def change_overlay_mode(self, mode: OverlayMode, slot, swap):
        sys.stdout.write('Overlay Manager - Overlay Mode Change: ENTER')

        overlay = self.overlays[self.overlay_slots[slot]]
        previous_mode = OverlayMode(self.overlay_slots[slot])

        sys.stdout.write(
            'Overlay Manager - Layout: {}, Overlay Slot: {}, Swap: {}'.format(
                OverlayLayout(self.active_slots).name, slot + 1, swap
            )
        )
        sys.stdout.write(
            'Overlay Manager - Overlay Slots IDs: {}'.format(
                [
                    OverlayMode(overlay_id).name
                    for overlay_id in self.overlay_slots
                ]
            )
        )
        sys.stdout.write(
            'Overlay Manager - Overlay Slots: {}'.format(
                [self.overlays[overlay_id] for overlay_id in self.overlay_slots]
            )
        )

        if swap:
            previous_slot = self.overlay_slots.index(
                self.overlays[mode.value].__class__.CLASS_ID
            )
            self.overlay_slots[slot], self.overlay_slots[previous_slot] = (
                self.overlay_slots[previous_slot], self.overlay_slots[slot]
            )
            sys.stdout.write(
                'Overlay Manager - Overlay Slots IDs Swapped: {}'.format(
                    [
                        OverlayMode(overlay_id).name
                        for overlay_id in self.overlay_slots
                    ]
                )
            )
            if self.active_slots == 1:
                sys.stdout.write(
                    'Overlay Manager - Turning {} overlay off'.format(
                        previous_mode.name
                    )
                )
                overlay.set_enable(False)
                sys.stdout.write(
                    'Overlay Manager - Turning {} overlay on'.format(mode.name)
                )
                self.overlays[mode.value].set_enable(True)
            previous_settings = overlay.set_settings_from_overlay(
                self.overlays[mode.value]
            )
            self.overlays[mode.value].set_settings(*previous_settings)
            sys.stdout.write(
                'Overlay Manager - Overlay Slots Settings Swapped: {}'.format(
                    [
                        self.overlays[overlay_id]
                        for overlay_id in self.overlay_slots
                    ]
                )
            )
        else:
            sys.stdout.write(
                'Overlay Manager - Turning {} overlay off'.format(
                    previous_mode.name
                )
            )
            overlay.set_enable(False)
            change_overlay = self.overlays.get(mode.value)
            if not change_overlay:
                change_overlay = self.__add_overlay(
                    mode, previous_overlay=overlay
                )
                self.overlay_slots[slot] = change_overlay.__class__.CLASS_ID
            else:
                sys.stdout.write(
                    "Overlay Manager - Changing {} overlay settings to {}'s"
                    .format(mode.name, previous_mode.name)
                )
                previous_settings = change_overlay.set_settings_from_overlay(
                    overlay
                )
                overlay.set_settings(*previous_settings)
            sys.stdout.write(
                'Overlay Manager - Changing from {} to {} overlay'.format(
                    previous_mode.name, mode.name
                )
            )
            if self.overlays_enabled:
                sys.stdout.write(
                    'Overlay Manager - Turning {} overlay on'.format(mode.name)
                )
                change_overlay.set_enable(True)

        sys.stdout.write('Overlay Manager - Overlay Mode Change: EXIT')

    def change_overlay_position(self, position, slot, swap):
        overlay = self.overlays[self.overlay_slots[slot]]

        sys.stdout.write('Overlay Manager - Overlay Position Change: ENTER')
        sys.stdout.write(
            'Overlay Manager - Layout: {}, Overlay Slot: {}, Swap: {}'.format(
                OverlayLayout(self.active_slots).name, slot + 1, swap
            )
        )
        sys.stdout.write(
            'Overlay Manager - Overlay Slots: {}'.format(
                [self.overlays[overlay_id] for overlay_id in self.overlay_slots]
            )
        )

        if swap:
            swap_overlay = next(
                self.overlays[overlay_id]
                for overlay_id in self.overlay_slots
                if self.overlays[overlay_id].position == position
            )
            previous_position = overlay.position
            overlay.set_position(position)
            swap_overlay.set_position(previous_position)
            sys.stdout.write(
                'Overlay Manager - Overlay Slots Position Swapped: {}'.format(
                    [
                        self.overlays[overlay_id]
                        for overlay_id in self.overlay_slots
                    ]
                )
            )
        else:
            overlay.set_position(position)
            sys.stdout.write(
                'Overlay Manager - Overlay Position Changed: {}'.format(overlay)
            )

        sys.stdout.write('Overlay Manager - Overlay Position Change: EXIT')


    def change_overlay_theme(self, theme_dict):
        self.current_theme = theme_dict
        for overlay_id in self.overlays:
            self.overlays[overlay_id].set_theme(theme_dict)

    def get_overlay_mode(self, slot):
        return OverlayMode(
            self.overlays[self.overlay_slots[slot]].__class__.CLASS_ID
        )

    def reload(self):
        if self.reloadable_initial_settings:
            initial_settings = self.reloadable_initial_settings.config[
                'DEFAULT'
            ]
        else:
            initial_settings = DefaultSettings.SETTINGS['DEFAULT']

        for slot in range(1, list(OverlayLayout).pop().value + 1):
            mode = OverlayMode[
                initial_settings.get('overlay_{}_mode'.format(slot))
            ]
            self.overlay_slots[slot - 1] = mode.value

            if self.overlays.get(mode.value):
                overlay = self.overlays[mode.value]
            else:
                overlay = self.__add_overlay(mode)

            overlay.set_position(
                OverlayPosition[
                    initial_settings.get('overlay_{}_position'.format(slot))
                ]
            )

            overlay.set_theme(
                self.overlay_model.get_theme(
                    self.overlay_model.get_index_by_filename(
                        mode.name,
                        initial_settings.get('overlay_{}_theme'.format(slot))
                    ),
                    mode.name
                )
            )

        self.enable_automatic_overlay_hide(
            initial_settings.get('overlay_automatic_hide')
        )
        self.set_framedata_overlay_column_settings(
            initial_settings.get('framedata_overlay_columns')
        )
        self.active_slots = (
            OverlayLayout[
                initial_settings.get('overlay_layout')
            ].value
        )
        self.enable_overlays(initial_settings.get('overlay_enable'))

    def set_framedata_overlay_column_settings(self, column_settings):
        frame_data_overlay = self.overlays.get(OverlayMode.FRAMEDATA.value)
        if not frame_data_overlay:
            frame_data_overlay = self.__add_overlay(OverlayMode.FRAMEDATA)
        frame_data_overlay.set_display_columns(column_settings)

    def write_to_overlays(self, string):
        for overlay_id in self.overlay_slots:
            overlay = self.overlays.get(overlay_id)
            if(
                    isinstance(overlay, WritableOverlay)
                    and overlay.enabled
            ):
                overlay.write(string)

    def __add_overlay(self, overlay_mode, previous_overlay=None):
        sys.stdout.write(
            'Overlay Manager - Creating {} overlay'.format(overlay_mode.name)
        )
        overlay_id = overlay_mode.value
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

        if previous_overlay:
            sys.stdout.write(
                "Overlay Manager - Initializing {} overlay with {}'s settings"
                .format(
                    overlay_mode.name,
                    OverlayMode(previous_overlay.__class__.CLASS_ID).name
                )
            )
            self.overlays[overlay_id].set_settings_from_overlay(
                previous_overlay
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
