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
import configparser
import re

from constants.overlay import OverlayMode, OverlayPosition
from constants.overlay.frame_data import Columns

class DefaultSettings():
    """
    """
    PATH = 'data/settings.ini'
    SETTINGS = {
        'DEFAULT': {
            'alarm_enable': str(False),
            'alarm_sound_folder': 'original',
            'alarm_voice_folder': 'original',
            'overlay_enable': str(True),
            'overlay_mode': getattr(OverlayMode.FRAMEDATA, 'name'),
            'overlay_position': getattr(OverlayPosition.TOP, 'name'),
            'overlay_theme': 'classic',
            'framedata_overlay_columns': [
                getattr(Columns.INPUT_COMMAND, 'name'),
                getattr(Columns.ATTACK_TYPE, 'name'),
                getattr(Columns.STARTUP_FRAMES, 'name'),
                getattr(Columns.ON_BLOCK_FRAMES, 'name'),
                getattr(Columns.ON_HIT_FRAMES, 'name'),
                getattr(Columns.ACTIVE_FRAMES, 'name'),
                getattr(Columns.TRACKING, 'name'),
                getattr(Columns.TOTAL_FRAMES, 'name'),
                getattr(Columns.RECOVERY_FRAMES, 'name'),
                getattr(Columns.OPPONENT_FRAMES, 'name'),
                getattr(Columns.NOTES, 'name')
            ]
        }
    }

    def __init__(self, file_settings=None):
        self.update_required = True
        self.settings = configparser.ConfigParser(allow_no_value=True)
        str_updated_settings_dict = DefaultSettings.__values_to_string(
            DefaultSettings.SETTINGS
        )
        if file_settings:
            str_settings_dict = DefaultSettings.__values_to_string(
                file_settings
            )
            for key in str_updated_settings_dict:
                try:
                    str_updated_settings_dict[key] = str_settings_dict[key]
                except KeyError:
                    pass

            if str_updated_settings_dict == str_settings_dict:
                self.update_required = False

        self.settings['DEFAULT'] = str_updated_settings_dict

    def write(self):
        with open(DefaultSettings.PATH, 'w') as settings_file:
            self.settings.write(settings_file)

    @staticmethod
    def parse(str_settings_dict):
        settings = {'DEFAULT': {}}
        for key, value in str_settings_dict['DEFAULT'].items():
            if re.search(r'[,|\[|\]]', value):
                settings['DEFAULT'][key] = (
                    re.sub(r'[^a-zA-Z_,]+', '', value).split(',')
                )
            else:
                settings['DEFAULT'][key] = value
        return settings

    @staticmethod
    def __values_to_string(parsed_settings):
        settings = dict(parsed_settings['DEFAULT'])
        for key, value in settings.items():
            if isinstance(value, list):
                settings[key] = ','.join(map(str, value))
                settings[key] = '[{}]'.format(settings[key])
            else:
                settings[key] = str(value)
        return settings
