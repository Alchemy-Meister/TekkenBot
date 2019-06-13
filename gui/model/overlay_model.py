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
from config import ReloadableConfigManager
from constants.overlay import OverlayMode, OverlayPosition

class OverlayModel():
    """
    """
    def __init__(self):
        self.__config_manager = ReloadableConfigManager()
        self.all_overlay_modes = OverlayModel.__enum_to_list(OverlayMode)
        self.all_overlay_positions = OverlayModel.__enum_to_list(
            OverlayPosition
        )
        self.overlay_themes = self.__config_manager.add_config_group(
            'overlay_themes', self.__get_all_overlay_theme_config_paths
        )

    def get_overlay_themes_names(self):
        return [
            theme['theme']['printable_name']
            for theme in self.overlay_themes
        ]

    def get_theme(self, theme_index):
        return self.overlay_themes[theme_index].config['theme']

    def get_theme_tuple_by_filename(self, theme_filename):
        for index, theme_config in enumerate(self.overlay_themes):
            if(
                    theme_filename
                    == str(os.path.basename(theme_config.path)).split('.theme')
                    [0]
            ):
                return index, theme_config.config['theme']
        return None, None

    @staticmethod
    def __enum_to_list(printable_enum_class):
        return_list = list()
        for printable_enum in printable_enum_class:
            return_list.append(
                (printable_enum.name, printable_enum.printable_name)
            )
        return return_list

    @staticmethod
    def get_overlay_mode_enum(overlay_mode_name):
        return OverlayMode[overlay_mode_name]

    @staticmethod
    def get_overlay_position_enum(overlay_position_name):
        return OverlayPosition[overlay_position_name]

    def __get_all_overlay_theme_config_paths(self):
        overlay_theme_dir = 'themes/overlay'
        overlay_theme_path = os.path.join(
            self.__config_manager.data_folder, overlay_theme_dir
        )
        return [
            os.path.join(overlay_theme_path, theme)
            for theme in os.listdir(overlay_theme_path)
            if theme.endswith('.theme')
        ]

    def reload(self):
        self.__config_manager.reload_all()
        self.overlay_themes = self.__config_manager.get_config_group(
            'overlay_themes'
        )
