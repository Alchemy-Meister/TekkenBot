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

from constants.complex_enum import ComplexEnum, ComplexEnumMember

class InputDirection(ComplexEnum):
    """
    """
    NULL = ComplexEnumMember(0x0, abbreviation='', symbol='!')
    DOWN_BACK = ComplexEnumMember(
        0x2, abbreviation='d/b', symbol='↙', flipped_symbol='↘'
    )
    DOWN = ComplexEnumMember(0x4, abbreviation='d', symbol='↓')
    DOWN_FORWARD = ComplexEnumMember(
        0x8, abbreviation='d/f', symbol='↘', flipped_symbol='↙'
    )
    BACK = ComplexEnumMember(
        0x10, abbreviation='b', symbol='←', flipped_symbol='→'
    )
    NEUTRAL = ComplexEnumMember(0x20, abbreviation='N', symbol='★')
    FORWARD = ComplexEnumMember(
        0x40, abbreviation='f', symbol='→', flipped_symbol='←'
    )
    UP_BACK = ComplexEnumMember(
        0x80, abbreviation='u/b', symbol='↖', flipped_symbol='↗'
    )
    UP = ComplexEnumMember(0x100, abbreviation='u', symbol='↑')
    UP_FORWARD = ComplexEnumMember(
        0x200, abbreviation='u/f', symbol='↗', flipped_symbol='↖'
    )
