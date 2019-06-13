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
import tkinter.ttk as ttk

from gui.my_tkinter import EnumLabel, Combobox

class MemoryOverwritePanel(ttk.Frame):
    """
    """
    def __init__(self, master, controller):
        super().__init__(master=master)
        self.controller = controller
        self.p1_frame = None
        self.p2_frame = None

        battle_settings_frame = ttk.LabelFrame(self, text='Battle Settings')

        # Stage
        stage_frame = ttk.Frame(battle_settings_frame)

        enable_stage_overwrite = tk.BooleanVar(False)
        stage_checkbutton = ttk.Checkbutton(
            stage_frame,
            text='Overwrite Stage to:',
            variable=enable_stage_overwrite,
            command=lambda: self.controller
            .checkbox_stage_overwrite_change(
                enable_stage_overwrite.get()
            )
        )
        stage_checkbutton.grid(column=0, row=0)

        stage_combobox = Combobox(
            *self.controller.populate_stage_combobox(),
            master=stage_frame,
            state='readonly'
        )
        stage_combobox.set(
            self.controller.default_overwrite_stage()
        )
        stage_combobox.bind(
            '<<ComboboxSelected>>',
            self.controller.combobox_overwrite_stage_change,
        )
        stage_combobox.grid(column=1, row=0, padx=(10, 0))

        stage_frame.grid(column=0, row=0)

        # Rounds
        rounds_frame = ttk.Frame(battle_settings_frame)

        enable_num_rounds_overwrite = tk.BooleanVar(False)
        num_rounds_checkbutton = ttk.Checkbutton(
            rounds_frame,
            text='Overwrite Number of Rounds to:',
            variable=enable_num_rounds_overwrite,
            command=lambda: self.controller
            .checkbox_num_rounds_overwrite_change(
                enable_num_rounds_overwrite.get()
            )
        )
        num_rounds_checkbutton.grid(column=0, row=0)

        self.str_round_number = tk.StringVar()
        self.num_rounds_label = ttk.Label(
            rounds_frame, textvariable=self.str_round_number
        )
        self.num_rounds_label.grid(column=1, row=0)

        self.round_number = tk.IntVar()
        round_scale = ttk.Scale(
            rounds_frame, variable=self.round_number, from_=1, to=5,
            command=self.controller.scale_round_number_overwrite_change
        )
        round_scale.grid(column=2, row=0, padx=(10, 0))

        rounds_frame.grid(column=0, row=1)

        #Time limit
        time_limit_frame = ttk.Frame(battle_settings_frame)

        enable_time_limit_overwrite = tk.BooleanVar(False)
        time_limit_checkbutton = ttk.Checkbutton(
            time_limit_frame,
            text='Overwrite Time Limit to:',
            variable=enable_time_limit_overwrite,
            command=lambda: self.controller
            .checkbox_time_limit_overwrite_change(
                enable_time_limit_overwrite.get()
            )
        )
        time_limit_checkbutton.grid(column=0, row=0, sticky='w')

        self.str_time_limit = tk.StringVar()
        self.time_limit_label = EnumLabel(
            time_limit_frame, textvariable=self.str_time_limit
        )
        self.time_limit_label.grid(column=1, row=0)

        self.time_limit_index = tk.IntVar()
        time_limit_scale = ttk.Scale(
            time_limit_frame, variable=self.time_limit_index, from_=0, to=4,
            command=lambda _: self.controller.scale_time_limit_overwrite_change(
                self.time_limit_index.get()
            )
        )
        time_limit_scale.grid(column=2, row=0, padx=(10, 0))

        time_limit_frame.grid(column=0, row=2)

        battle_settings_frame.grid(column=1, row=0, padx=(20, 0), pady=(25, 0))

    def get_rounds_number(self):
        return self.round_number

    def get_rounds_number_name(self):
        return self.str_round_number

    def get_time_limit_index(self):
        return self.time_limit_index

    def get_time_limit_name(self):
        return self.str_time_limit

    def get_time_limit_label(self):
        return self.time_limit_label
