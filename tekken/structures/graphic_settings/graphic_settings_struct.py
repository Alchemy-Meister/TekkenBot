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
import struct
from win32.defines import SIZE_OF, Structure, DWORD
from win32.utils import type_limits

class GraphicSettingsStruct(Structure):
    """
    """
    _fields_ = [
        ('horizontal_resolution', DWORD),
        ('vertial_resolution', DWORD),
        ('screen_mode', DWORD),
    ]

    def __init__(self, block_bytes):
        super().__init__()
        offset = 0
        for field in self._fields_:
            size = offset + SIZE_OF(field[1])
            t_bytes = block_bytes[offset:size]
            struct_format = type_limits.C_ALL_TYPES_FORMAT[field[1]]
            setattr(
                self,
                field[0],
                struct.unpack(struct_format, t_bytes)[0]
            )
            offset = size

    def __repr__(self):
        return 'resolution: ({}, {}), screen_mode: {}'.format(
            self.horizontal_resolution,
            self.vertial_resolution,
            self.screen_mode
        )
