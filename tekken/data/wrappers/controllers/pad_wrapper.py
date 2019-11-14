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

from constants.controllers import PadController

from tekken.data.structures.controllers import PadControllerStruct
from tekken.data.wrappers import StructWrapper

class PadControllerWrapper(StructWrapper):
    """
    """
    def __init__(self, block_bytes=None):
        super().__init__(PadControllerStruct, block_bytes)

    def __get_left_stick(self):
        return (
            getattr(self, 'left_stick_horizontal_axis'),
            getattr(self, 'left_stick_vertical_axis')
        )

    def __set_left_stick(self, left_stick_tuple):
        setattr(self, 'left_stick_horizontal_axis', left_stick_tuple[0])
        setattr(self, 'left_stick_vertical_axis', left_stick_tuple[1])

    left_stick = property(__get_left_stick, __set_left_stick)

    def __get_right_stick(self):
        return (
            getattr(self, 'right_stick_horizontal_axis'),
            getattr(self, 'right_stick_vertical_axis')
        )

    def __set_right_stick(self, right_stick_tuple):
        setattr(self, 'right_stick_horizontal_axis', right_stick_tuple[0])
        setattr(self, 'right_stick_vertical_axis', right_stick_tuple[1])

    right_stick = property(__get_right_stick, __set_right_stick)

    def difference(self, pad_controller):
        diff_buttons = (
            getattr(self, 'pressed_buttons') ^ pad_controller.pressed_buttons
        )
        diff_buttons = [
            button for button in PadController if button & diff_buttons
        ]
        for index, diff_button in enumerate(diff_buttons):
            if getattr(self, 'pressed_buttons') & diff_button.value:
                diff_buttons[index] = (diff_button, True)
            else:
                diff_buttons[index] = (diff_button, False)

        return {
            'buttons': diff_buttons,
            'left_stick': PadControllerWrapper.__tuple_difference(
                self.left_stick, pad_controller.left_stick
            ),
            'right_stick': PadControllerWrapper.__tuple_difference(
                self.right_stick, pad_controller.right_stick
            )
        }

    def is_pressed(self, pad_button: PadController):
        if getattr(self, 'pressed_buttons') & pad_button:
            return True
        return False

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            'pressed_buttons: [{}], left_stick: {}, right_stick: {}'.format(
                ', '.join(
                    button.name
                    for button in PadController
                    if button & getattr(self, 'pressed_buttons')
                ),
                self.left_stick,
                self.right_stick
            )
        )

    @staticmethod
    def __tuple_difference(tuple_a, tuple_b):
        return tuple(
            (max(tuple_a_item, tuple_b_item) - min(tuple_a_item, tuple_b_item))
            * (-1 if tuple_a_item > tuple_b_item else 1)
            for tuple_a_item, tuple_b_item in zip(
                tuple_a, tuple_b
            )
        )
