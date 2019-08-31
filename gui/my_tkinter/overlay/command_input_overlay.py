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
import tkinter as tk

from PIL import Image, ImageTk
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

from constants.battle import MoveProperty
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
        'frame_index_min_y_margin': 0,
        'frame_image_min_margin': 1,
        'frame_rect_min_margin': 4,
        'step_length': 32,
        'font': ['TkDefaultFont', -14],
        'font_pixel_height': 16
    }

    __CANCEL_PROPERTY_COLORS = {
        MoveProperty.STARTING: 'green4',
        MoveProperty.RECOVERING: 'red4',
        MoveProperty.PARRY_1: 'orange',
        MoveProperty.PARRY_2: 'yellow',
        MoveProperty.BUFFERABLE: 'MediumOrchid1',
        MoveProperty.CANCELABLE: 'SteelBlue1',
        'other': 'snow'
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
        self.frame_move_property = list()
        self.last_frame_inputs = list()
        self.last_frame_cancels = list()

        self.svg_arrow_images = dict()
        self.svg_button_images = dict()
        self.arrow_images = dict()
        self.button_images = dict()

        self.__initialize_frame_indexes()
        self._load_resources()
        self.__initialize_input_coordinates()
        self.__initialize_frame_lines()
        self.__initialize_canvas()

        self.command_input_canvas.pack(fill=tk.BOTH, expand=tk.YES)

        self._set_dimensions(self.canvas_width, self.canvas_height)

        self.overlay.minsize(width=240, height=12)

    def __initialize_frame_indexes(self, scale=(1, 1,), expand=False):
        if expand:
            self.step_length = (
                (
                    self.window_dimensions[0]
                    - self.canvas_step_number
                )
                / self.canvas_step_number
            )
        else:
            self.step_length = (
                CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG['step_length']
                * scale[0]
            )

        self.font, _, height = Overlay._get_fitting_font(
            scale,
            CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG['font'],
            str(self.canvas_step_number),
            self.step_length
            - 2
            * CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG[
                'frame_index_min_margin'
            ]
            * scale[0],
            CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG[
                'font_pixel_height'
            ]
            * scale[1]
        )

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
            + 3 * height / 2
            + scaled_frame_index_min_margin
        )

        for index in range(self.canvas_step_number):
            str_frame_intex = str(self.canvas_step_number - index)
            self.command_input_canvas.create_text(
                index * self.step_length + index + self.step_length / 2,
                scaled_frame_index_y,
                font=self.font,
                text=str_frame_intex,
                fill='snow',
                tag=self.index_tag
            )

    def __initialize_input_coordinates(self, scale=(1, 1,)):
        arrow_image_height = next(iter(self.arrow_images.values())).height()
        self.button_image_coordinate_y0 = (
            self.arrow_image_coordinate_y0
            + arrow_image_height
            )

        button_image_height = next(iter(self.button_images.values())).height()

        self.cancel_rect_coordinate_y0 = (
            self.button_image_coordinate_y0
            + (button_image_height / 2)
        )

        scaled_frame_rect_min_margin = (
            CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG[
                'frame_rect_min_margin'
            ]
            * scale[0]
        )
        if scaled_frame_rect_min_margin < 1:
            scaled_frame_rect_min_margin = 1

        self.cancel_rect_coordinate_y1 = (
            self.cancel_rect_coordinate_y0
            + self.step_length
            - 2
            * scaled_frame_rect_min_margin
        )

        self.cancel_rect_size = (
            self.cancel_rect_coordinate_y1 - self.cancel_rect_coordinate_y0
        )

        self.canvas_height = int(self.cancel_rect_coordinate_y1 + 2)

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
        self.canvas_width = int(last_line_cords[0] + self.step_length)

        self.command_input_canvas.configure(
            width=self.canvas_width, height=self.canvas_height
        )

    def __get_canvas_item_dimensions(self, item_id):
        bounds = self.command_input_canvas.bbox(item_id)
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        return width, height

    def _resize_overlay_widgets(self, overlay_scale=None):
        expand_canvas = False
        if overlay_scale:
            scale = [
                overlay_scale_size * tekken_scale_size
                for overlay_scale_size, tekken_scale_size in zip(
                    overlay_scale, self._tekken_scale
                    )
            ]
            expand_canvas = True
        else:
            scale = self._tekken_scale

        self.command_input_canvas.delete('all')
        self.__initialize_frame_indexes(scale, expand_canvas)
        self.arrow_images = self.scale_svg_images(
            self.svg_arrow_images, scale
        )
        self.button_images = self.scale_svg_images(
            self.svg_button_images, scale
        )
        self.__initialize_input_coordinates(scale)
        self.__initialize_frame_lines()
        self.__initialize_canvas()
        self.__paint_input(restore=True)

        return self.canvas_width, self.canvas_height

    def _update_dimensions(self):
        self.coordinates['width'] = int(self.canvas_width)
        self.coordinates['height'] = int(self.canvas_height)
        self.window_proportion = self.canvas_width / self.canvas_height

    def _update_state(self):
        last_game_state_log = self.launcher.game_state.state_log[-1]
        player = None
        if last_game_state_log.is_player_player_one:
            player = last_game_state_log.bot
        else:
            player = last_game_state_log.opp

        input_state = player.get_input_state()

        move_properties = [
            [MoveProperty.PARRY_1, player.is_parry1],
            [MoveProperty.PARRY_2, player.is_parry2],
            [MoveProperty.BUFFERABLE, player.is_bufferable],
            [MoveProperty.CANCELABLE, player.is_cancelable],
            [MoveProperty.STARTING, player.is_starting],
            [MoveProperty.RECOVERING, player.is_recovering]
        ]

        move_color = None
        for cancel_property in move_properties:
            if cancel_property[1]:
                move_color = CommandInputOverlay.__CANCEL_PROPERTY_COLORS[
                    cancel_property[0]
                ]
                break
        if move_color is None:
            move_color = CommandInputOverlay.__CANCEL_PROPERTY_COLORS['other']

        self._update_input(input_state, move_color)

    def _update_visible_state(self):
        previous_visible_state = self.visible
        self.visible = self.launcher.game_state.is_in_battle()
        if previous_visible_state != self.visible and not self.visible:
            self.command_input_canvas.delete(self.input_tag)
            self.frame_inputs.clear()
            self.frame_move_property.clear()

    def _load_resources(self):
        for enum_member in InputDirection:
            if(
                    InputDirection.NULL
                    != enum_member
                    != InputDirection.NEUTRAL
            ):
                svg_drawing = svg2rlg(
                    'data/images/arrows/{}.svg'.format(
                        enum_member.symbol
                    )
                )
                self.svg_arrow_images[enum_member.symbol] = svg_drawing

        for enum_member in InputAttack:
            str_button = enum_member.printable_name
            if str_button:
                svg_drawing = svg2rlg(
                    'data/images/buttons/steam_arcade/{}.svg'.format(
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
                scaled_frame_min_margin = (
                    CommandInputOverlay.__COMMAND_INPUT_CANVAS_CONFIG[
                        'frame_image_min_margin'
                    ]
                    * scale[0]
                )
                if scaled_frame_min_margin < 1:
                    scaled_frame_min_margin = 1

                svg_width_scale = (
                    (
                        self.step_length
                        - 2
                        * scaled_frame_min_margin
                    )
                    / svg_drawing.width
                )
                svg_drawing.scale(
                    svg_width_scale, svg_width_scale
                )

                svg_drawing.width *= svg_width_scale
                svg_drawing.height *= svg_width_scale

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

    def _update_input(self, input_state, move_color):
        self.frame_inputs.append(input_state)
        self.frame_move_property.append(move_color)

        if len(self.frame_inputs) >= self.canvas_step_number:
            self.frame_inputs = self.frame_inputs[-self.canvas_step_number:]
            self.frame_move_property = self.frame_move_property[
                -self.canvas_step_number:
            ]

            if input_state != self.frame_inputs[-2]:
                self.last_frame_inputs = self.frame_inputs.copy()
                self.last_frame_cancels = self.frame_move_property.copy()

                self.command_input_canvas.delete(self.input_tag)
                self.__paint_input()

    def __paint_input(self, restore=False):
        if restore:
            frame_inputs = self.last_frame_inputs
            frame_cancels = self.last_frame_cancels
        else:
            frame_inputs = self.frame_inputs
            frame_cancels = self.frame_move_property

        for index, (direction_code, input_code, _) in enumerate(frame_inputs):
            coordinate_x = (
                (
                    index
                    * self.step_length
                    + index
                )
            )
            direction_code = InputDirection(direction_code)
            if(
                    InputDirection.NEUTRAL
                    != direction_code
                    != InputDirection.NULL
            ):
                self.command_input_canvas.create_image(
                    coordinate_x
                    + self.step_length / 2,
                    self.arrow_image_coordinate_y0,
                    image=self.arrow_images[direction_code.symbol],
                    tag=self.input_tag
                )

            input_code = InputAttack(input_code)
            if input_code != InputAttack.NULL:
                self.command_input_canvas.create_image(
                    coordinate_x
                    + self.step_length / 2,
                    self.button_image_coordinate_y0,
                    image=self.button_images[input_code.printable_name],
                    tag=self.input_tag
                )

            coordinate_x += self.step_length / 2 - self.cancel_rect_size / 2
            rect_coordinate_x1 = coordinate_x + self.cancel_rect_size
            self.command_input_canvas.create_rectangle(
                coordinate_x,
                self.cancel_rect_coordinate_y0,
                rect_coordinate_x1,
                self.cancel_rect_coordinate_y1,
                fill=frame_cancels[index],
                tag=self.input_tag
            )
