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

from collections import OrderedDict
from itertools import chain

from win32.defines import (
    BYTE, DOUBLE, DWORD, FLOAT, LONG, LONGLONG, QWORD, SBYTE, SHORT, SIZE_OF,
    WORD
)

C_UNSIGNED_INT_TYPES_FORMAT = OrderedDict(
    [
        (BYTE, '<B'), (WORD, '<H'), (DWORD, '<I'), (QWORD, '<Q')
    ]
)
C_SIGNED_INT_TYPES_FORMAT = OrderedDict(
    [
        (SBYTE, '<b'), (SHORT, '<h'), (LONG, '<i'), (LONGLONG, '<q')
    ]
)
C_FLOAT_TYPES_FORMAT = OrderedDict(
    [
        (FLOAT, '<f'), (DOUBLE, '<d')
    ]
)

C_ALL_TYPES_FORMAT = OrderedDict(
    chain(
        C_UNSIGNED_INT_TYPES_FORMAT.items(),
        C_SIGNED_INT_TYPES_FORMAT.items(),
        C_FLOAT_TYPES_FORMAT.items()
    )
)

def __init_limits():
    signed_int_limits = [
        (c_type, struct_format, __limits(c_type))
        for c_type, struct_format in C_SIGNED_INT_TYPES_FORMAT.items()
    ]

    unsigned_int_limits = [
        (c_type, struct_format, __limits(c_type))
        for c_type, struct_format in C_UNSIGNED_INT_TYPES_FORMAT.items()
    ]

    float_limits = [
        (c_type, struct_format, __limits(c_type))
        for c_type, struct_format in C_FLOAT_TYPES_FORMAT.items()
    ]

    return (signed_int_limits, unsigned_int_limits, float_limits)

def __limits(c_int_type):
    signed = c_int_type(-1).value < c_int_type(0).value
    bit_size = SIZE_OF(c_int_type) * 8
    signed_limit = 2 ** (bit_size - 1)
    if signed:
        return (-signed_limit, signed_limit - 1)
    return (0, 2 * signed_limit - 1)

__C_SIGNED_INT_LIMITS, __C_UNSIGNED_INT_LIMITS, __C_FLOAT_LIMITS = (
    __init_limits()
)

def get_size(value, signed=False):
    return __get_size_format(value, signed=signed)[0]

def get_struct_format(value, signed=False):
    return __get_size_format(value, signed=signed)[1]

def __get_size_format(value, signed=False):
    def find_size_format(value, type_limits):
        size_format = None
        for limit in type_limits:
            if(
                    limit[2][0] <= value <= limit[2][1]
            ):
                size_format = (
                    SIZE_OF(limit[0]), limit[1]
                )
                break
        return size_format

    size_format = None
    if isinstance(value, int):
        if not signed:
            signed = value < 0

        if signed:
            size_format = find_size_format(value, __C_SIGNED_INT_LIMITS)
        else:
            size_format = find_size_format(value, __C_UNSIGNED_INT_LIMITS)
    elif isinstance(value, float):
        size_format = find_size_format(value, __C_FLOAT_LIMITS)
    elif isinstance(value, str):
        raise NotImplementedError
    else:
        raise NotImplementedError

    return size_format
