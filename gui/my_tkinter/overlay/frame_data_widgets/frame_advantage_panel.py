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
import tkinter as tk

from constants.battle import FrameAdvantage

class FrameAdvantagePanel(tk.Frame):
    """
    """

    __CANVAS_CONFIG = {
        'width': 132,
        'height': 82,
        'initial_frame_advantage': FrameAdvantage.SAFE_MINUS
    }
    __FRAME_ADVANTAGE_CONFIG = {'font': ['Consolas', 44], 'initial_text': '?'}
    __LIVE_RECOVERY_CONFIG = {
        'font': ['Segoe UI', 12], 'x': 8, 'y': 4, 'initial_text': '??'
    }
    __PADDING_WIDTH = 10

    def __init__(self, master, transparent_color, **kwargs):
        super().__init__(master=master, **kwargs)

        self.frame_advantage_backgrounds = None
        self.frame_advantage = FrameAdvantagePanel.__CANVAS_CONFIG[
            'initial_frame_advantage'
        ]

        self.left_padding = self.__create_padding(transparent_color)

        self.configure(background=transparent_color)

        self.str_frame_advantage = tk.StringVar()
        self.str_frame_advantage.set(
            FrameAdvantagePanel.__FRAME_ADVANTAGE_CONFIG['initial_text']
        )

        self.str_live_recovery = tk.StringVar()
        self.str_live_recovery.set(
            FrameAdvantagePanel.__LIVE_RECOVERY_CONFIG['initial_text']
        )

        self.frame_advantage_canvas = tk.Canvas(
            self,
            width=FrameAdvantagePanel.__CANVAS_CONFIG['width'],
            height=FrameAdvantagePanel.__CANVAS_CONFIG['height'],
            borderwidth=0,
            background='DodgerBlue2',
            highlightthickness=0
        )

        self.frame_advantage_text = self.frame_advantage_canvas.create_text(
            0, 0,
            font=tuple(FrameAdvantagePanel.__FRAME_ADVANTAGE_CONFIG['font']),
            text=self.str_frame_advantage.get(),
            anchor=tk.CENTER
        )
        self.__center_frame_advantage()

        self.str_frame_advantage.trace_variable(
            'w', self.__frame_advantage_update
        )

        self.live_recovery_text = self.frame_advantage_canvas.create_text(
            FrameAdvantagePanel.__LIVE_RECOVERY_CONFIG['x'],
            FrameAdvantagePanel.__LIVE_RECOVERY_CONFIG['y'],
            font=tuple(FrameAdvantagePanel.__LIVE_RECOVERY_CONFIG['font']),
            text=self.str_live_recovery.get(),
            anchor=tk.NW
        )
        self.str_live_recovery.trace_variable('w', self.__live_recovery_update)

        self.right_padding = self.__create_padding(transparent_color)

        self.left_padding.grid(column=0)
        self.frame_advantage_canvas.grid(column=1)
        self.right_padding.grid(column=2)

    def clear(self):
        self.str_frame_advantage.set(
            FrameAdvantagePanel.__FRAME_ADVANTAGE_CONFIG['initial_text']
        )
        self.str_live_recovery.set(
            FrameAdvantagePanel.__LIVE_RECOVERY_CONFIG['initial_text']
        )
        self.set_frame_advantage(
            FrameAdvantagePanel.__CANVAS_CONFIG[
                'initial_frame_advantage'
            ]
        )

    def is_clear(self):
        return (
            self.str_frame_advantage.get()
            == FrameAdvantagePanel.__FRAME_ADVANTAGE_CONFIG['initial_text']
            and self.str_live_recovery.get()
            == FrameAdvantagePanel.__LIVE_RECOVERY_CONFIG['initial_text']
            and self.frame_advantage
            == FrameAdvantagePanel.__CANVAS_CONFIG['initial_frame_advantage']
        )

    def set_frame_advantage(self, frame_advantage):
        self.frame_advantage = frame_advantage
        self.__configure_style()

    def set_theme(self, background_colors, text_color):
        self.frame_advantage_backgrounds = background_colors
        self.__configure_style(fill=text_color)

    def resize_to_scale(self, scale):
        padding_width = int(FrameAdvantagePanel.__PADDING_WIDTH * scale[0])
        self.left_padding.configure(width=padding_width)

        canvas_width = int(
            FrameAdvantagePanel.__CANVAS_CONFIG['width'] * scale[0]
        )
        canvas_height = int(
            FrameAdvantagePanel.__CANVAS_CONFIG['height'] * scale[1]
        )

        self.frame_advantage_canvas.configure(
            width=canvas_width,
            height=canvas_height,
        )

        self.__resize_canvas_text(
            self.frame_advantage_text,
            FrameAdvantagePanel.__FRAME_ADVANTAGE_CONFIG,
            scale
        )
        self.__center_frame_advantage(scale)
        self.__resize_canvas_text(
            self.live_recovery_text,
            FrameAdvantagePanel.__LIVE_RECOVERY_CONFIG,
            scale
        )
        self.frame_advantage_canvas.coords(
            self.live_recovery_text,
            int(FrameAdvantagePanel.__LIVE_RECOVERY_CONFIG['x'] * scale[0]),
            int(FrameAdvantagePanel.__LIVE_RECOVERY_CONFIG['y'] * scale[1])
        )
        self.right_padding.configure(width=padding_width)

        return canvas_width + 2 * padding_width, canvas_height

    def __center_frame_advantage(self, scale=(1, 1,)):
        self.frame_advantage_canvas.coords(
            self.frame_advantage_text,
            FrameAdvantagePanel.__CANVAS_CONFIG['width'] / 2 * scale[0],
            FrameAdvantagePanel.__CANVAS_CONFIG['height'] / 2 * scale[1]
        )

    def __frame_advantage_update(self, _varname, _index, _mode):
        self.frame_advantage_canvas.itemconfigure(
            self.frame_advantage_text, text=self.str_frame_advantage.get()
        )

    def __live_recovery_update(self, _varname, _index, _mode):
        self.frame_advantage_canvas.itemconfigure(
            self.live_recovery_text, text=self.str_live_recovery.get()
        )

    def __resize_canvas_text(self, canvas_item, config, scale):
        self.frame_advantage_canvas.itemconfigure(
            canvas_item,
            font=(
                config['font'][0],
                math.ceil(config['font'][1] * scale[0])
            )
        )

    def __get_canvas_item_dimensions(self, canvas_item):
        bounds = self.frame_advantage_canvas.bbox(canvas_item)
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        return width, height

    def __configure_style(self, **kwargs):
        background = self.frame_advantage_backgrounds[
            self.frame_advantage.value
        ]
        self.frame_advantage_canvas.configure(background=background)
        self.frame_advantage_canvas.itemconfigure(
            self.frame_advantage_text, **kwargs
        )
        self.frame_advantage_canvas.itemconfigure(
            self.live_recovery_text, **kwargs
        )

    def __create_padding(self, transparent_color):
        padding = tk.Frame(
            self,
            width=FrameAdvantagePanel.__PADDING_WIDTH,
            background=transparent_color
        )
        padding.grid()
        return padding
