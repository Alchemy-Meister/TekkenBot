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
import uuid

from constants.battle import FrameAdvantage

class FrameAdvantagePanel(tk.Frame):
    """
    """

    def __init__(self, master, transparent_color, **kwargs):
        super().__init__(master=master, **kwargs)
        self.style_name = '{}.TLabel'.format(uuid.uuid4())
        self.style = ttk.Style()
        self.style.configure(self.style_name, background='DodgerBlue2')

        self.frame_advantage_backgrounds = None
        self.text_color = None
        self.frame_advantage = FrameAdvantage.SAFE_MINUS

        left_padding = self.__create_padding(transparent_color)

        self.configure(background=transparent_color)

        self.str_frame_advantage = tk.StringVar()
        self.str_frame_advantage.set('?')
        self.frame_advantage_label = ttk.Label(
            self,
            textvariable=self.str_frame_advantage,
            font=('Consolas', 44),
            width=4,
            anchor='c',
            borderwidth=1,
            relief='ridge',
            style=self.style_name
        )

        self.str_live_recovery = tk.StringVar()
        self.str_live_recovery.set('??')
        self.live_recovery_label = tk.Label(
            self.frame_advantage_label,
            textvariable=self.str_live_recovery,
            font=('Segoe UI', 12),
            width=4,
            anchor=tk.N + tk.W,
            background='DodgerBlue2'
        )
        self.live_recovery_label.place(
            rely=0.0, relx=0.0, x=2, y=2, anchor=tk.NW
        )

        right_padding = self.__create_padding(transparent_color)

        left_padding.grid(column=0)
        self.frame_advantage_label.grid(column=1, row=0, ipady=5)
        right_padding.grid(column=2)

    def set_frame_advantage(self, frame_advantage):
        self.frame_advantage = frame_advantage
        self.__configure_style()

    def set_theme(self, background_colors, text_color):
        self.frame_advantage_backgrounds = background_colors
        self.text_color = text_color

        self.__configure_style(foreground=text_color)

    def __configure_style(self, **kwargs):
        background = self.frame_advantage_backgrounds[
            self.frame_advantage.value
        ]
        self.style.configure(self.style_name, background=background, **kwargs)
        self.live_recovery_label.configure(background=background)

    def __create_padding(self, transparent_color):
        padding = tk.Frame(self, width=10, background=transparent_color)
        padding.grid(row=0, sticky='NSEW')
        return padding
