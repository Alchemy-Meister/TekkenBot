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

from constants.complex_enum import ComplexEnum, ComplexEnumMember

class MovelistButtonInput(ComplexEnum):
    NULL = ComplexEnumMember(0)
    B_1 = ComplexEnumMember(1, printable_name='1')
    B_2 = ComplexEnumMember(2, printable_name='2')
    B_1_PLUS_2 = ComplexEnumMember(3, printable_name='1+2')
    B_3 = ComplexEnumMember(4, printable_name='3')
    B_1_PLUS_3 = ComplexEnumMember(5, printable_name='1+3')
    B_2_PLUS_3 = ComplexEnumMember(6, printable_name='2+3')
    B_1_PLUS_2_PLUS_3 = ComplexEnumMember(7, printable_name='1+2+3')
    B_4 = ComplexEnumMember(8, printable_name='4')
    B_1_PLUS_4 = ComplexEnumMember(9, printable_name='1+4')
    B_2_PLUS_4 = ComplexEnumMember(10, printable_name='2+4')
    B_1_PLUS_2_PLUS_4 = ComplexEnumMember(11, printable_name='1+2+4')
    B_3_PLUS_4 = ComplexEnumMember(12, printable_name='3+4')
    B_1_PLUS_3_PLUS_4 = ComplexEnumMember(13, printable_name='1+3+4')
    B_2_PLUS_3_PLUS_4 = ComplexEnumMember(14, printable_name='2+3+4')
    B_1_PLUS_2_PLUS_3_PLUS_4 = ComplexEnumMember(15, printable_name='1+2+3+4')
    B_RAGE = ComplexEnumMember(16, printable_name='Rage')
    #1+2 only maybe? on hwoarangs b2, not HOLD
    UNK_600 = ComplexEnumMember(0x600)
