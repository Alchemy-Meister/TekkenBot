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
from tekken.data.structures.graphic_settings import ScreenModeStruct
from tekken.data.wrappers import StructWrapper

class ScreenModeWrapper(StructWrapper):
    """
    """
    def __init__(self, block_bytes=None):
        super().__init__(ScreenModeStruct, block_bytes)
        setattr(self, 'screen_mode', ScreenMode(getattr(self, 'screen_mode')))

    def equal_screen_mode(self, screen_mode):
        try:
            return getattr(self, 'screen_mode') == screen_mode.screen_mode
        except AttributeError:
            return False

    def __eq__(self, screen_mode):
        if isinstance(screen_mode, ScreenModeWrapper):
            return getattr(self, 'screen_mode') == screen_mode.screen_mode
        return NotImplementedError

    def __ne__(self, screen_mode):
        return not self == screen_mode

    def __repr__(self):
        return 'screen_mode: {}'.format(
            getattr(self, 'screen_mode').name
        )
