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
import math
import re
import tkinter as tk
import tkinter.font as tkfont

from constants.printable_enum import PrintableEnum, PrintableValue
from constants.battle import FrameAdvantage
from constants.overlay import OverlayMode

from .writable_overlay import WritableOverlay
from .frame_data_widgets import AttackTextbox, FrameAdvantagePanel

class FrameDataOverlay(WritableOverlay):
    """
    """
    class GUIColumns(PrintableEnum):
        INPUT_COMMAND = PrintableValue(0, 'input command')
        MOVE_ID = PrintableValue(1, 'internal move id number')
        MOVE_NAME = PrintableValue(2, 'internal move name')
        ATTACK_TYPE = PrintableValue(3, 'attack type')
        STARTUP_FRAMES = PrintableValue(4, 'startup frames')
        ON_BLOCK_FRAMES = PrintableValue(5, 'frame advantage on block')
        ON_HIT_FRAMES = PrintableValue(6, 'frame advantage on hit')
        COUNTER_HIT_FRAMES = PrintableValue(7, 'frame advantage on counter hit')
        ACTIVE_FRAMES = PrintableValue(
            8, 'active frame connected on/total active frames'
        )
        TRACKING = PrintableValue(9, 'how well move tracks during startup')
        TOTAL_FRAMES = PrintableValue(10, 'total number of frames in move')
        REACTION_FRAMES = PrintableValue(11, 'frames before attacker can act')
        OPPONET_FRAMES = PrintableValue(12, 'frames before defender can act')
        NOTES = PrintableValue(13, 'additional move properties')

    class Columns(PrintableEnum):
        INPUT_COMMAND = PrintableValue(0, 'command')
        MOVE_ID = PrintableValue(1, 'id')
        MOVE_NAME = PrintableValue(2, 'name')
        ATTACK_TYPE = PrintableValue(3, 'type')
        STARTUP_FRAMES = PrintableValue(4, 'startup')
        ON_BLOCK_FRAMES = PrintableValue(5, 'block')
        ON_HIT_FRAMES = PrintableValue(6, 'hit')
        COUNTER_HIT_FRAMES = PrintableValue(7, 'counter')
        ACTIVE_FRAMES = PrintableValue(8, 'active')
        TRACKING = PrintableValue(9, 'track')
        TOTAL_FRAMES = PrintableValue(10, 'total')
        RECOVERY_FRAMES = PrintableValue(11, 'recovery')
        OPPONET_FRAMES = PrintableValue(12, 'opponent')
        NOTES = PrintableValue(13, 'notes')

        @staticmethod
        def max_column_lenght():
            return max(
                [
                    len(column.printable_name)
                    for column in FrameDataOverlay.Columns
                ]
            )

    CLASS_ID = OverlayMode.FRAMEDATA.value

    def __init__(self, launcher):
        super().__init__(launcher)

        self.p1_tag = 'p1: '
        self.p2_tag = 'p2: '
        self.frame_advantage_tag = 'NOW:'

        self.max_attack_log_length = 5
        self.attack_log = list()

        # TODO Initialize this variable from default config.
        # pylint: disable=no-member
        display_columns_settings = [
            FrameDataOverlay.Columns.INPUT_COMMAND.name,
            # FrameDataOverlay.Columns.MOVE_ID.name,
            # FrameDataOverlay.Columns.MOVE_NAME.name,
            FrameDataOverlay.Columns.ATTACK_TYPE.name,
            FrameDataOverlay.Columns.STARTUP_FRAMES.name,
            FrameDataOverlay.Columns.ON_BLOCK_FRAMES.name,
            FrameDataOverlay.Columns.ON_HIT_FRAMES.name,
            FrameDataOverlay.Columns.ACTIVE_FRAMES.name,
            FrameDataOverlay.Columns.TRACKING.name,
            FrameDataOverlay.Columns.TOTAL_FRAMES.name,
            FrameDataOverlay.Columns.RECOVERY_FRAMES.name,
            FrameDataOverlay.Columns.OPPONET_FRAMES.name,
            FrameDataOverlay.Columns.NOTES.name
        ]
        self.set_display_columns(display_columns_settings)

        # TODO load this dict dynamically
        self.frame_advantage_backgrounds = {
            FrameAdvantage.VERY_PUNISHABLE.value: 'deep pink',
            FrameAdvantage.PUNISHABLE.value: 'orchid2',
            FrameAdvantage.SAFE_MINUS.value: 'ivory2',
            FrameAdvantage.SAFE_SLIGHT_MINUS.value: 'ivory2',
            'plus': 'DodgerBlue2'
        }

        self.overlay.configure(background=self.transparent_color)

        self.p1_frame_panel = FrameAdvantagePanel(
            self.overlay, self.transparent_color
        )
        self.p2_frame_panel = FrameAdvantagePanel(
            self.overlay, self.transparent_color
        )

        self.initial_textbox_font = ['Consolas', -16]
        self.textbox = AttackTextbox(
            self.overlay,
            self.max_attack_log_length,
            font=self.initial_textbox_font,
            background='gray10',
            foreground='lawn green'
        )

        all_title_columns = (
            [column.printable_name for column in FrameDataOverlay.Columns]
        )

        self.insert_columns_to_log(all_title_columns)
        column_titles = self.__generate_visible_column_string(all_title_columns)
        self.textbox.insert('1.0', '{}\n'.format(column_titles))
        self.textbox.fit_to_content()

        self.__create_padding(self.transparent_color).grid(column=0, row=0)
        self.__create_padding(self.transparent_color).grid(column=2, row=0)

        self.p1_frame_panel.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W)
        self.textbox.grid(column=1, row=0, rowspan=2, sticky=tk.N + tk.E + tk.W)
        self.p2_frame_panel.grid(column=2, row=1, sticky=tk.N + tk.S + tk.E)

        self.overlay.update_idletasks()

        self._set_dimensions(
            self.overlay.winfo_width(), self.overlay.winfo_height()
        )

        self.initial_font_size = WritableOverlay._get_font_text_dimensions(
            tkfont.Font(
                family=self.initial_textbox_font[0],
                size=self.initial_textbox_font[1]
            ),
            self.__generate_visible_column_string(self.attack_log[0])
        )

    def set_display_columns(self, display_columns_settings):
        self.display_columns = [
            column_enum.value for item in display_columns_settings
            for column_enum in FrameDataOverlay.Columns
            if column_enum.name == item
        ]

    def set_theme(self, theme_dict):
        super().set_theme(theme_dict)
        self.textbox.configure(background=theme_dict.get('background'))
        self.textbox.configure(foreground=theme_dict.get('system_text'))

        frame_advantage_backgrounds = dict()
        for frame_advantage_enum in FrameAdvantage:
            frame_advantage_backgrounds[frame_advantage_enum.value] = (
                theme_dict.get(
                    ''.join(['advantage_', frame_advantage_enum.name.lower()])
                )
            )

        advantage_text_color = theme_dict.get('advantage_text')

        self.p1_frame_panel.set_theme(
            frame_advantage_backgrounds, advantage_text_color
            )
        self.p2_frame_panel.set_theme(
            frame_advantage_backgrounds, advantage_text_color
        )

    def write(self, string):
        if self.frame_advantage_tag in string:
            display_string, player_tag = self.__process_string(string)
            if display_string:
                self.textbox.insert(tk.END, display_string, player_tag)

    def __clear(self):
        if not self.textbox.is_clear():
            self.textbox.clear()

    def __create_padding(self, color):
        padding = tk.Frame(
            self.overlay,
            height=int(
                round(
                    (
                        self.textbox.winfo_height()
                        - self.p1_frame_panel.frame_advantage_canvas
                        .winfo_height()
                    ) / 2
                )
            ),
            background=color
        )
        padding.grid(sticky='NSEW')
        return padding

    def __process_string(self, string):
        player_tag = None
        if self.p1_tag in string:
            player_tag = self.p1_tag
            display_string = string.replace(self.p1_tag, '')
        else:
            player_tag = self.p2_tag
            display_string = string.replace(self.p2_tag, '')

        display_string, frame_advantage = re.split(
            self.frame_advantage_tag, display_string
        )
        if display_string:
            all_columns_values = FrameDataOverlay.__generate_columns(
                display_string
            )
            self.insert_columns_to_log(all_columns_values)
            display_string = self.__generate_visible_column_string(
                all_columns_values
            )
            display_string = ''.join([display_string, '\n'])
        else:
            display_string = None
        self.__update_frame_advantage(
            frame_advantage, player_1=(player_tag == self.p1_tag)
        )
        return display_string, player_tag

    @staticmethod
    def __generate_columns(string):
        return [column.strip() for column in string.split('|')]

    @staticmethod
    def __generate_column_string(*column_tuples):
        display_columns = []
        for index, column in column_tuples:
            column_lenght = len(column)
            column_title_length = (
                len(
                    FrameDataOverlay.Columns(index).printable_name
                )
                + 2
            )
            if column_lenght <= column_title_length:
                spaces_needed = (column_title_length - column_lenght) / 2
                column = ''.join(
                    [
                        (' ' * math.ceil(spaces_needed)),
                        column,
                        (' ' * int(spaces_needed))
                    ]
                )
            display_columns.append(''.join(['|', column]))
        return  ''.join([*display_columns, '|'])

    def __generate_visible_column_string(self, column_values):
        visible_columns = [
            (index, column_values[index])
            for index in self.display_columns
        ]
        return FrameDataOverlay.__generate_column_string(*visible_columns)

    def insert_columns_to_log(self, columns):
        if len(self.attack_log) >= self.max_attack_log_length:
            self.attack_log.pop(1)
        self.attack_log.append(columns)

    def __update_frame_advantage(self, frame_advantage, player_1=True):
        if '?' not in frame_advantage:
            frame_advantage = int(frame_advantage)
            current_frame_advantage_enum = None
            for frame_advantage_enum in FrameAdvantage:
                if frame_advantage <= frame_advantage_enum.value:
                    current_frame_advantage_enum = frame_advantage_enum
                    break
            if frame_advantage >= 0:
                frame_advantage = ''.join(['+', str(frame_advantage)])
            if player_1:
                self.p1_frame_panel.str_frame_advantage.set(frame_advantage)
                self.p1_frame_panel.set_frame_advantage(
                    current_frame_advantage_enum
                )
            else:
                self.p2_frame_panel.str_frame_advantage.set(frame_advantage)
                self.p2_frame_panel.set_frame_advantage(
                    current_frame_advantage_enum
                )

    def _resize_overlay_widgets(self, overlay_scale=None):
        if overlay_scale:
            scale = [
                overlay_scale_size * tekken_scale_size
                for overlay_scale_size, tekken_scale_size in zip(
                    overlay_scale, self._tekken_scale
                    )
            ]
        else:
            scale = self._tekken_scale

        scaled_frame_panel_width, _ = self.p1_frame_panel.resize_to_scale(scale)
        self.p2_frame_panel.resize_to_scale(scale)
    
        scaled_textbot_font, font_width, _ = WritableOverlay._get_fitting_font(
            scale,
            self.initial_textbox_font,
            self.__generate_visible_column_string(self.attack_log[0]),
            self.initial_font_size[0] * scale[0],
            self.initial_font_size[1] * scale[1]
            )

        self.textbox.configure(font=scaled_textbot_font)
        self.overlay.update_idletasks()

        return (
            scaled_frame_panel_width * 2 + font_width,
            self.textbox.winfo_height()
        )

    def _update_dimensions(self):
        self.overlay.update_idletasks()
        self.coordinates['width'] = (
            self.p1_frame_panel.winfo_width()
            + self.textbox.winfo_width()
            + self.p2_frame_panel.winfo_width()
        )
        self.coordinates['height'] = self.textbox.winfo_height()
        self.window_proportion = (
            self.coordinates['width'] / self.coordinates['height']
        )

    def _update_visible_state(self):
        previous_visible_state = self.visible
        self.visible = self.launcher.game_state.is_in_battle()
        if previous_visible_state != self.visible and not self.visible:
            self.__clear()
            self.textbox.insert(tk.END, '\n')
            self.textbox.update()

    def _update_state(self):
        game_state = self.launcher.game_state
        if len(game_state.state_log) > 1:
            p1_frames = game_state.get_opp_frames_till_next_move()
            p2_frames = game_state.get_bot_frames_till_next_move()

            p1_recovery = p1_frames - p2_frames
            str_p1_recovery = str(p1_recovery)
            str_p2_recovery = str(p1_recovery * -1)

            if p1_recovery > 0:
                str_p1_recovery = ''.join(['+', str_p1_recovery])
            elif p1_recovery == 0:
                str_p1_recovery = ''.join(['+', str_p1_recovery])
                str_p2_recovery = ''.join(['+', str_p2_recovery])
            else:
                str_p2_recovery = ''.join(['+', str_p2_recovery])

            self.p1_frame_panel.str_live_recovery.set(str_p1_recovery)
            self.p2_frame_panel.str_live_recovery.set(str_p2_recovery)
