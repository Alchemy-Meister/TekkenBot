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

from constants.printable_enum import PrintableEnum, PrintableValue

class InputAttack(PrintableEnum):
    NULL = PrintableValue(0, '')
    ONE = PrintableValue(512, '1')
    TWO = PrintableValue(1024, '2')
    THREE = PrintableValue(2048, '3')
    FOUR = PrintableValue(4096, '4')
    ONE_PLUS_TWO = PrintableValue(1536, '1+2')
    ONE_PLUS_THREE = PrintableValue(2560, '1+3')
    ONE_PLUS_FOUR = PrintableValue(4608, '1+4')
    TWO_PLUS_THREE = PrintableValue(3072, '2+3')
    TWO_PLUS_FOUR = PrintableValue(5120, '2+4')
    THREE_PLUS_FOUR = PrintableValue(6144, '3+4')
    ONE_PLUS_TWO_PLUSTHREE = PrintableValue(3584, '1+2+3')
    ONE_PLUS_TWO_PLUS_FOUR = PrintableValue(5632, '1+2+4')
    ONE_PLUS_THREE_PLUS_FOUR = PrintableValue(6656, '1+3+4')
    TWO_PLUS_THREE_PLUS_FOUR = PrintableValue(7168, '2+3+4')
    ONE_PLUS_TWO_PLUS_THREE_PLUS_FOUR = PrintableValue(7680, '1+2+3+4')
    RAGE = PrintableValue(8192, 'rage')
