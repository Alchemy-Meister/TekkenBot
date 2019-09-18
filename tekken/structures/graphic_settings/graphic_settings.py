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

from .resolution import ResolutionWrapper
from .screen_mode import ScreenModeWrapper

class GraphicSettingsWrapper():
    """
    """
    def __init__(self, block_bytes=None):
        self.resolution_wrapper = ResolutionWrapper(block_bytes)
        if block_bytes:
            self.screen_mode_wrapper = ScreenModeWrapper(
                block_bytes[self.resolution_wrapper.get_structure_size():]
            )
        else:
            self.screen_mode_wrapper = ScreenModeWrapper()
        self.position = (0, 0)

    def __get_resolution(self):
        return self.resolution_wrapper.resolution

    def __set_resolution(self, resolution_tuple):
        self.resolution_wrapper.resolution = resolution_tuple

    resolution = property(__get_resolution, __set_resolution)

    def __get_screen_mode(self):
        return getattr(self.screen_mode_wrapper, 'screen_mode')

    def __set_screen_mode(self, screen_mode):
        setattr(self.screen_mode_wrapper, 'screen_mode', screen_mode)

    screen_mode = property(__get_screen_mode, __set_screen_mode)

    def equal_resolution(self, graphic_settings):
        if isinstance(graphic_settings, GraphicSettingsWrapper):
            return (
                self.resolution_wrapper.equal_resolution(graphic_settings)
            )
        return False

    def equal_screen_mode(self, graphic_settings):
        if isinstance(graphic_settings, GraphicSettingsWrapper):
            return self.screen_mode_wrapper.equal_screen_mode(graphic_settings)
        return False

    def equal_position(self, graphic_settings):
        if isinstance(graphic_settings, GraphicSettingsWrapper):
            return self.position == graphic_settings.position
        return False

    def __eq__(self, graphic_settings):
        if isinstance(graphic_settings, GraphicSettingsWrapper):
            return (
                self.resolution_wrapper.equal_resolution(graphic_settings)
                and self.screen_mode_wrapper.equal_screen_mode(graphic_settings)
                and self.position == graphic_settings.position
            )
        return NotImplemented

    def __ne__(self, graphic_settings):
        return not self == graphic_settings

    def __repr__(self):
        return '{}, {}, position {}'.format(
            self.resolution_wrapper, self.screen_mode_wrapper, self.position
        )
