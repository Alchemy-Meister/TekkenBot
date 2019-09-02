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

class Columns(ComplexEnum):
    """
    """
    INPUT_COMMAND = ComplexEnumMember(printable_name='command')
    MOVE_ID = ComplexEnumMember(printable_name='id')
    MOVE_NAME = ComplexEnumMember(printable_name='name')
    ATTACK_TYPE = ComplexEnumMember(printable_name='type')
    STARTUP_FRAMES = ComplexEnumMember(printable_name='startup')
    ON_BLOCK_FRAMES = ComplexEnumMember(printable_name='block')
    ON_HIT_FRAMES = ComplexEnumMember(printable_name='hit')
    COUNTER_HIT_FRAMES = ComplexEnumMember(printable_name='counter')
    ACTIVE_FRAMES = ComplexEnumMember(printable_name='active')
    TRACKING = ComplexEnumMember(printable_name='track')
    TOTAL_FRAMES = ComplexEnumMember(printable_name='total')
    RECOVERY_FRAMES = ComplexEnumMember(printable_name='recovery')
    OPPONENT_FRAMES = ComplexEnumMember(printable_name='opponent')
    NOTES = ComplexEnumMember(printable_name='notes')

    @staticmethod
    def max_column_lenght():
        return max(
            [
                len(column.printable_name)
                for column in Columns
            ]
        )
