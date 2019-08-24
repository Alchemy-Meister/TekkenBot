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

from constants.graphic_settings import ScreenMode

class GraphicSettings():
    """
    """
    def __init__(self, struct=None):
        self.horizontal_resolution = 0
        self.vertial_resolution = 0
        self.screen_mode = ScreenMode.FULLSCREEN
        self.position = (0, 0)

        if struct:
            self.horizontal_resolution = struct.horizontal_resolution
            self.vertial_resolution = struct.vertial_resolution
            self.screen_mode = ScreenMode(struct.screen_mode)

    def __get_resolution(self):
        return (self.horizontal_resolution, self.vertial_resolution)

    def __set_resolution(self, horizontal_lines, vertial_lines):
        self.horizontal_resolution = horizontal_lines
        self.vertial_resolution = vertial_lines

    resolution = property(__get_resolution, __set_resolution)


    def equal_resolution(self, graphic_settings):
        if not isinstance(graphic_settings, GraphicSettings):
            return False
        return (
            self.horizontal_resolution == graphic_settings.horizontal_resolution
            and self.vertial_resolution == graphic_settings.vertial_resolution
        )

    def equal_screen_mode(self, graphic_settings):
        if not isinstance(graphic_settings, GraphicSettings):
            return False
        return self.screen_mode == graphic_settings.screen_mode

    def equal_position(self, graphic_settings):
        if not isinstance(graphic_settings, GraphicSettings):
            return False
        return self.position == graphic_settings.position

    def __eq__(self, graphic_settings):
        if not isinstance(graphic_settings, GraphicSettings):
            return NotImplemented
        return (
            self.horizontal_resolution == graphic_settings.horizontal_resolution
            and self.vertial_resolution == graphic_settings.vertial_resolution
            and self.screen_mode == graphic_settings.screen_mode
        )

    def __ne__(self, graphic_settings):
        return not self == graphic_settings

    def __repr__(self):
        return 'resolution: ({}, {}), screen_mode: {}'.format(
            self.horizontal_resolution,
            self.vertial_resolution,
            self.screen_mode.name
        )
