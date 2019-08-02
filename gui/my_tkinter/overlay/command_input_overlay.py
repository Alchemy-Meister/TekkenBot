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
import io
from PIL import Image, ImageTk
import sys
import tkinter as tk
import tkinter.font as tkfont

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Drawing

from constants.battle import MoveCancel
from constants.input import InputAttack, InputDirection
from constants.overlay import OverlayMode

from .overlay import Overlay

class CommandInputOverlay(Overlay):
    """
    """

    CLASS_ID = OverlayMode.COMMAND_INPUT.value

    __COMMAND_INPUT_CANVAS_CONFIG = {
        'background': 0x0,
        'frame_index_y': 8,
        'frame_index_min_margin': 6,
        'frame_index_min_y_margin': 9,
        'frame_image_min_margin': 1,
        'frame_rect_min_margin': 4,
        'font': ['TkDefaultFont', -16]
    }

    __CANCEL_PROPERTY_COLORS = {
        MoveCancel.PARRY_1: 'orange',
        MoveCancel.PARRY_2: 'yellow',
        MoveCancel.BUFFERABLE: 'MediumOrchid1',
        MoveCancel.CANCELABLE: 'SteelBlue1',
        'other': 'firebrick'
    }

    def __init__(self, launcher):
        super().__init__(launcher)

        self.index_tag = 'index'
        self.line_tag = 'line'
        self.input_tag = 'input'
        self.canvas_step_number = 60

        self.command_input_canvas = tk.Canvas(
            self.overlay,
            bg='#{0:06X}'.format(
                CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG['background']
            ),
            highlightthickness=0,
            borderwidth=0,
            relief='flat'
        )

        self.step_length = None
        self.max_frame_width = None
        self.arrow_image_coordinate_y0 = None
        self.button_image_coordinate_y0 = None
        self.cancel_rect_coordinate_y0 = None

        self.frame_inputs = list()
        self.frame_cancels = list()

        self.svg_arrow_images = dict()
        self.svg_button_images = dict()
        self.arrow_images = dict()
        self.button_images = dict()

        self.__initialize_frame_indexes()
        self._load_resources()
        self.__initialize_input_coordinates()
        self.__initialize_frame_lines()
        self.__initialize_canvas()

        self.command_input_canvas.pack()

        self._set_dimensions(self.canvas_width, self.canvas_height)

    def __initialize_frame_indexes(self, scale=(1, 1,)):
        font_height = int(
            CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG['font'][1]
            * scale[1]
        )
        font = tkfont.Font(
            family=CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG['font'][0],
            size=font_height
        )

        for index in range(self.canvas_step_number):
            str_frame_intex = str(self.canvas_step_number - index)
            frame_index_text = self.command_input_canvas.create_text(
                0,
                0,
                font=font,
                text=str_frame_intex,
                fill='snow',
                tag=self.index_tag
            )

            width, height = CommandInputOverlay.__get_font_text_dimensions(
                font, str_frame_intex
            )

            if not index:
                self.max_frame_width = width

                scaled_frame_index_y = (
                    CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG[
                        'frame_index_y'
                    ]
                    * scale[1]
                )

                scaled_frame_index_min_margin = (
                    CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG[
                        'frame_index_min_y_margin'
                    ]
                    * scale[1]
                )

                self.arrow_image_coordinate_y0 = math.ceil(
                    scaled_frame_index_y
                    + font_height * -1
                    + scaled_frame_index_min_margin
                )

                self.step_length = (
                    width
                    + 2
                    * scaled_frame_index_y
                )

            self.command_input_canvas.coords(
                frame_index_text,
                index * self.step_length + index + self.step_length / 2,
                scaled_frame_index_y
            )

    def __initialize_input_coordinates(self, scale=(1, 1,)):
        self.button_image_coordinate_y0 = (
            self.arrow_image_coordinate_y0
            + next(iter(self.arrow_images.values())).height()
            )

        button_image_height = next(iter(self.button_images.values())).height()

        self.cancel_rect_coordinate_y0 = (
            self.button_image_coordinate_y0
            + (button_image_height / 2)
        )
        self.cancel_rect_coordinate_y1 = (
            self.cancel_rect_coordinate_y0
            + self.step_length
            - CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG[
                'frame_rect_min_margin'
            ] * 2
            * scale[0]
        )

        self.cancel_rect_size = (
            self.cancel_rect_coordinate_y1 - self.cancel_rect_coordinate_y0
        )

        self.canvas_height = self.cancel_rect_coordinate_y1 + 2

    def __initialize_frame_lines(self):
        for index in range(1, self.canvas_step_number):
            coordinate_x = index * self.step_length + index
            self.command_input_canvas.create_line(
                coordinate_x - 1,
                0,
                coordinate_x - 1,
                self.canvas_height,
                fill='red',
                tag=self.line_tag
            )

    def __initialize_canvas(self):
        last_line_cords = self.command_input_canvas.coords(
            self.command_input_canvas.find_withtag(self.line_tag)[-1]
        )
        self.canvas_width = last_line_cords[0] + self.step_length + 1

        self.command_input_canvas.configure(
            width=self.canvas_width, height=self.canvas_height
        )

    @staticmethod
    def __get_font_text_dimensions(font, text):
        width = font.measure(text)
        height = font.metrics('linespace')
        return width, height

    def __get_canvas_item_dimensions(self, item_id):
        bounds = self.command_input_canvas.bbox(item_id)
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        return width, height

    def _resize_overlay_widgets(self):
        self.command_input_canvas.delete('all')

        self.__initialize_frame_indexes(self._scale)
        self.arrow_images = self.scale_svg_images(
            self.svg_arrow_images, self._scale
        )
        self.button_images = self.scale_svg_images(
            self.svg_button_images, self._scale
        )
        self.__initialize_input_coordinates(self._scale)
        self.__initialize_frame_lines()
        self.__initialize_canvas()

    def _update_dimensions(self):
        self.coordinates['width'] = int(self.canvas_width)
        self.coordinates['height'] = int(self.canvas_height)

    def _update_state(self):
        last_game_state_log = self.launcher.game_state.state_log[-1]
        player = None
        if last_game_state_log.is_player_player_one:
            player = last_game_state_log.bot
        else:
            player = last_game_state_log.opp

        input_state = player.get_input_state()

        cancel_properties = [
            [MoveCancel.PARRY_1, player.is_parry1],
            [MoveCancel.PARRY_2, player.is_parry2],
            [MoveCancel.BUFFERABLE, player.is_bufferable],
            [MoveCancel.CANCELABLE, player.is_cancelable]
        ]

        cancel_color = None
        for cancel_property in cancel_properties:
            if cancel_property[1]:
                cancel_color = CommandInputOverlay.__CANCEL_PROPERTY_COLORS[
                    cancel_property[0]
                ]
                break
        if cancel_color is None:
            cancel_color = CommandInputOverlay.__CANCEL_PROPERTY_COLORS['other']

        self._update_input(input_state, cancel_color)

    def _update_visible_state(self):
        previous_visible_state = self.visible
        self.visible = self.launcher.game_state.is_in_battle()
        if previous_visible_state != self.visible and not self.visible:
            self.command_input_canvas.delete(self.input_tag)

    def _load_resources(self):
        for printable_value in InputDirection:
            if(
                    printable_value != InputDirection.NULL
                    and printable_value != InputDirection.NEUTRAL
            ):
                str_arrow = printable_value.printable_name['symbol']
                svg_drawing = svg2rlg(
                    'data/resources/arrows/{}.svg'.format(
                        str_arrow
                    )
                )
                self.svg_arrow_images[str_arrow] = svg_drawing

        for printable_value in InputAttack:
            str_button = printable_value.printable_name
            if str_button:
                svg_drawing = svg2rlg(
                    'data/resources/buttons/steam_arcade/{}.svg'.format(
                        str_button
                    )
                )
                self.svg_button_images[str_button] = svg_drawing
        self.arrow_images = self.scale_svg_images(
            self.svg_arrow_images, (1, 1,)
        )
        self.button_images = self.scale_svg_images(
            self.svg_button_images, (1, 1,)
        )

    def scale_svg_images(self, svg_image_dict, scale):
        image_dict = svg_image_dict.copy()
        for key, svg_drawing in image_dict.items():
            if svg_drawing:
                svg_width_scale = (
                    (
                        self.step_length
                        - 2
                        * CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG[
                            'frame_image_min_margin'
                        ]
                        * scale[0]
                    )
                    / svg_drawing.width
                )
                svg_height_scale = (
                    (
                        self.step_length
                        - 2
                        * CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG[
                            'frame_image_min_margin'
                        ]
                        * scale[0]
                    )
                    / svg_drawing.width
                )
                svg_drawing.scale(
                    svg_width_scale, svg_height_scale
                )

                svg_drawing.width *= svg_width_scale
                svg_drawing.height *= svg_height_scale

                image_stream = io.BytesIO()
                renderPM.drawToFile(
                    svg_drawing,
                    image_stream,
                    bg=CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG[
                        'background'
                    ],
                    fmt='PNG'
                )
                image_dict[key] = ImageTk.PhotoImage(Image.open(image_stream))
        return image_dict

    def _update_input(self, input_state, cancel_color):
        self.frame_inputs.append(input_state)
        self.frame_cancels.append(cancel_color)

        if len(self.frame_inputs) >= self.canvas_step_number:
            self.frame_inputs = self.frame_inputs[-self.canvas_step_number:]
            self.frame_cancels = self.frame_cancels[-self.canvas_step_number:]

            if input_state != self.frame_inputs[-2]:
                self.command_input_canvas.delete(self.input_tag)

                for index, (direction_code, input_code, rage_flag) in enumerate(
                        self.frame_inputs
                ):
                    coordinate_x = (
                        (
                            index
                            * self.step_length
                            + index
                            + (self.step_length / 2)
                        )
                    )

                    direction_code = InputDirection(direction_code)
                    if(
                        direction_code != InputDirection.NULL 
                        and direction_code != InputDirection.NEUTRAL
                    ):
                        canvas_arrow_image = (
                            self.command_input_canvas.create_image(
                                coordinate_x,
                                self.arrow_image_coordinate_y0,
                                image=self.arrow_images[
                                    direction_code.printable_name['symbol']
                                ],
                                tag=self.input_tag
                            )
                        )

                    input_code = InputAttack(input_code)
                    if input_code != InputAttack.NULL:
                        canvas_input_image =  (
                            self.command_input_canvas.create_image(
                                coordinate_x,
                                self.button_image_coordinate_y0,
                                image=self.button_images[
                                    input_code.printable_name
                                ],
                                tag=self.input_tag
                            )
                        )

                    coordinate_x = (
                        index
                        * self.step_length
                        + index
                        + CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG[
                            'frame_rect_min_margin'
                        ] * self._scale[0]
                    )
                    rect_coordinate_x1 = coordinate_x + self.cancel_rect_size
                    self.command_input_canvas.create_rectangle(
                        coordinate_x,
                        self.cancel_rect_coordinate_y0,
                        rect_coordinate_x1,
                        self.cancel_rect_coordinate_y1,
                        fill=self.frame_cancels[index],
                        tag=self.input_tag
                    )
