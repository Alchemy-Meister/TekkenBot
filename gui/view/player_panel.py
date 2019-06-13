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
from gui.my_tkinter import Combobox

class PlayerOverwritePanel(ttk.LabelFrame):
    """
    """
    def __init__(
            self, master, controller, format_string='P1', max_health=0, **kw
    ):
        super().__init__(master=master, **kw)
        self.controller = controller

        # Character Frame
        character_frame = ttk.Frame(self)

        enable_character_overwrite = tk.BooleanVar(False)
        p1_character_checkbutton = ttk.Checkbutton(
            character_frame,
            text='Overwrite {} Character to:'.format(format_string),
            variable=enable_character_overwrite,
            command=lambda: self.controller
            .checkbox_character_overwrite_change(
                enable_character_overwrite.get()
            )
        )
        p1_character_checkbutton.grid(column=0, row=0)

        character_combobox = Combobox(
            *self.controller.populate_character_combobox(),
            master=character_frame,
            state='readonly'
        )
        character_combobox.set(
            self.controller.default_overwrite_character()
        )
        character_combobox.bind(
            '<<ComboboxSelected>>',
            self.controller.combobox_overwrite_character_change,
        )
        character_combobox.grid(column=1, row=0, padx=(10, 0))

        character_frame.grid(column=0, row=0)

        # Health Frame
        health_frame = tk.Frame(self)

        enable_health_overwrite = tk.BooleanVar(False)
        health_checkbutton = ttk.Checkbutton(
            health_frame,
            text='Overwrite {} Health to:'.format(format_string),
            variable=enable_health_overwrite,
            command=lambda: self.controller
            .checkbox_health_overwrite_change(
                enable_health_overwrite.get()
            )
        )

        self.health_value = tk.IntVar(value=max_health)

        health_checkbutton.grid(column=0, row=0)
        self.str_health = tk.StringVar(value=max_health)
        self.health_label = ttk.Label(
            health_frame, textvariable=self.str_health
        )
        self.health_label.grid(column=1, row=0)

        self.health_scale = ttk.Scale(
            health_frame,
            variable=self.health_value,
            from_=0,
            to=max_health,
            command=lambda _: self.controller.scale_health_overwrite_change(
                self.health_value.get()
            )
        )
        self.health_scale.grid(column=2, row=0, padx=(10, 2))

        health_frame.grid(column=0, row=1)

    def set_player_max_health(self, max_health):
        if self.health_scale.cget('to') == self.health_value.get():
            self.health_value.set(max_health)
        self.health_scale.configure(to=max_health)
