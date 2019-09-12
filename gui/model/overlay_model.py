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
import os
from pathlib import Path
from config import ReloadableConfigManager
from constants.overlay import OverlayLayout, OverlayMode, OverlayPosition
from patterns.singleton import Singleton

class OverlayModel(metaclass=Singleton):
    """
    """
    def __init__(self):
        self.__config_manager = ReloadableConfigManager()
        self.all_overlay_layouts = OverlayModel.__enum_to_list(OverlayLayout)
        self.all_overlay_modes = OverlayModel.__enum_to_list(OverlayMode)
        self.all_overlay_positions = OverlayModel.__enum_to_list(
            OverlayPosition
        )

        overlay_theme_dir = 'themes/overlay'
        overlay_theme_path = os.path.join(
            self.__config_manager.data_folder, overlay_theme_dir
        )
        self.overlay_themes = {}
        for theme_dir in Path(overlay_theme_path).iterdir():
            try:
                overlay_mode = OverlayMode[theme_dir.name.upper()].name
                self.overlay_themes[overlay_mode] = {}
                self.overlay_themes[overlay_mode]['dir'] = theme_dir
                self.overlay_themes[overlay_mode]['themes'] = (
                    self.__config_manager.add_config_group(
                        '{}_overlay_themes'.format(theme_dir.name),
                        lambda mode=overlay_mode:
                        self.__get_all_overlay_theme_config_paths(mode)
                    )
                )
            except KeyError:
                pass

    def get_all_overlay_theme_names(self):
        return {
            overlay_mode:
            [
                theme_mode['theme']['printable_name']
                for theme_mode in theme_dict['themes']
            ]
            for overlay_mode, theme_dict in self.overlay_themes.items()
        }

    def get_overlay_themes_names(self, overlay_mode):
        try:
            return [
                theme['theme']['printable_name']
                for theme in self.overlay_themes[overlay_mode]['themes']
            ]
        except KeyError:
            return []

    def get_theme(self, theme_index, overlay_mode):
        try:
            return (
                self.overlay_themes[overlay_mode]['themes'][theme_index].config[
                    'theme'
                ]
            )
        except TypeError:
            return {}

    def get_index_by_filename(self, overlay_mode_name, theme_filename):
        for index, theme_config in enumerate(
                self.overlay_themes[overlay_mode_name]['themes']
        ):
            if(
                    theme_filename
                    == str(os.path.basename(theme_config.path)).split('.theme')
                    [0]
            ):
                return index
        return None

    @staticmethod
    def __enum_to_list(printable_enum_class):
        return [
            (printable_enum.name, printable_enum.printable_name)
            for printable_enum in printable_enum_class
        ]

    @staticmethod
    def get_overlay_layout_enum(overlay_layout_name):
        return OverlayLayout[overlay_layout_name]

    @staticmethod
    def get_overlay_mode_enum(overlay_mode_name):
        return OverlayMode[overlay_mode_name]

    @staticmethod
    def get_overlay_position_enum(overlay_position_name):
        return OverlayPosition[overlay_position_name]

    def reload(self):
        for key in self.overlay_themes:
            self.overlay_themes[key]['themes'] = (
                self.__config_manager.get_config_group(
                    '{}_overlay_themes'.format(key.lower())
                )
            )

    def __get_all_overlay_theme_config_paths(self, overlay_mode_name):
        theme_dir = self.overlay_themes[overlay_mode_name]['dir']
        return [
            theme for theme in theme_dir.iterdir()
            if theme.name.endswith('.theme')
        ]
