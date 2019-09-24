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

class InputAttack(ComplexEnum):
    NULL = ComplexEnumMember(0)
    B_1 = ComplexEnumMember(512, printable_name='1')
    B_2 = ComplexEnumMember(1024, printable_name='2')
    B_3 = ComplexEnumMember(2048, printable_name='3')
    B_4 = ComplexEnumMember(4096, printable_name='4')
    B_1_PLUS_2 = ComplexEnumMember(1536, printable_name='1+2')
    B_1_PLUS_3 = ComplexEnumMember(2560, printable_name='1+3')
    B_1_PLUS_4 = ComplexEnumMember(4608, printable_name='1+4')
    B_2_PLUS_3 = ComplexEnumMember(3072, printable_name='2+3')
    B_2_PLUS_4 = ComplexEnumMember(5120, printable_name='2+4')
    B_3_PLUS_4 = ComplexEnumMember(6144, printable_name='3+4')
    B_1_PLUS_2_PLUS_3 = ComplexEnumMember(3584, printable_name='1+2+3')
    B_1_PLUS_2_PLUS_4 = ComplexEnumMember(5632, printable_name='1+2+4')
    B_1_PLUS_3_PLUS_4 = ComplexEnumMember(6656, printable_name='1+3+4')
    B_2_PLUS_3_PLUS_4 = ComplexEnumMember(7168, printable_name='2+3+4')
    B_1_PLUS_2_PLUS_3_PLUS_4 = ComplexEnumMember(
        7680, printable_name='1+2+3+4'
    )
    B_RAGE = ComplexEnumMember(8192, printable_name='rage')
