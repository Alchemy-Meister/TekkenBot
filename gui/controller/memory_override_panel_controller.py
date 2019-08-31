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
import tkinter as tk
from gui.model import RoundModel, StageModel, TimerModel
from gui.view import MemoryOverwritePanel
from tekken import Launcher

from .player_override_panel_controller import (
    PlayerOverwritePanelController
)

class MemoryOverwritePanelController():
    """
    """
    def __init__(self, master, launcher: Launcher):
        self.launcher = launcher
        self.tekken_writer = self.launcher.game_state.get_writer()

        self.stage_model = StageModel()
        self.timer_model = TimerModel()

        self.view = MemoryOverwritePanel(master, self)

        self.__initialize_player_panels()
        self.__initialize_round_number()
        self.__initialize_time_limit()

    def checkbox_stage_overwrite_change(self, enable):
        self.tekken_writer.enable_stage_overwrite = enable

    def checkbox_num_rounds_overwrite_change(self, enable):
        self.tekken_writer.enable_round_number_overwrite = enable

    def checkbox_time_limit_overwrite_change(self, enable):
        self.tekken_writer.enable_time_limit_overwrite = enable

    def populate_stage_combobox(self):
        return self.stage_model.get_name_values(sort=True)

    def default_overwrite_stage(self):
        return StageModel.get_default_stage()

    def combobox_overwrite_stage_change(self, event):
        self.tekken_writer.stage_overwrite = event.widget.get_selected()

    def scale_round_number_overwrite_change(self, _):
        num_rounds = self.view.get_rounds_number().get()
        self.view.get_rounds_number().set(num_rounds)
        if self.view.get_rounds_number_name().get() != str(num_rounds):
            self.view.get_rounds_number_name().set(num_rounds)
            self.tekken_writer.round_number_overwrite = num_rounds

    def scale_time_limit_overwrite_change(self, time_limit_index):
        previous_time_limit_index = self.timer_model.timer_name_to_index(
            self.view.get_time_limit_name().get()
        )
        self.view.get_time_limit_index().set(time_limit_index)
        if time_limit_index != previous_time_limit_index:
            printable_enum = (
                self.timer_model.timer_index_to_printable_enum(time_limit_index)
            )
            self.view.get_time_limit_name().set(printable_enum.printable_name)
            self.tekken_writer.time_limit_overwrite = printable_enum.value

    def __initialize_player_panels(self):
        p1_override_controller = PlayerOverwritePanelController(
            self.view, self.launcher, player_num=1
        )
        p2_override_controller = PlayerOverwritePanelController(
            self.view, self.launcher, player_num=2
        )

        self.view.p1_frame = p1_override_controller.view
        self.view.p1_frame.grid(column=0, row=0)

        self.view.p2_frame = p2_override_controller.view
        self.view.p2_frame.grid(column=0, row=1)

    def __initialize_round_number(self):
        default_round_number = RoundModel.get_default_round_number()
        self.view.get_rounds_number().set(default_round_number.value)
        self.view.get_rounds_number_name().set(default_round_number.value)

    def __initialize_time_limit(self):
        default_time_limit = TimerModel.get_default_time_limit()
        self.view.get_time_limit_index().set(
            self.timer_model.timer_name_to_index(
                getattr(default_time_limit, 'printable_name', None)
            )
        )
        self.view.get_time_limit_name().set(
            getattr(default_time_limit, 'printable_name', None)
        )
        time_limit_label = self.view.get_time_limit_label()
        time_limit_label.set_enum_class(TimerModel.get_time_limit_enum())
        self.view.columnconfigure(
            3, minsize=time_limit_label.get_max_width()
        )

    def __enable_all_widgets(self, enable):
        def enable_all_widgets(frame, state):
            for child in frame.winfo_children():
                try:
                    child.configure(state=state)
                except tk.TclError:
                    enable_all_widgets(child, state)

        if enable:
            state = 'normal'
        else:
            state = 'disabled'
        enable_all_widgets(self.view, state)

    def __initialize_tekken_writter(self):
        self.__enable_all_widgets(True)
