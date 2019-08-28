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

class Columns(PrintableEnum):
    """
    """
    INPUT_COMMAND = PrintableValue(0, 'command')
    MOVE_ID = PrintableValue(1, 'id')
    MOVE_NAME = PrintableValue(2, 'name')
    ATTACK_TYPE = PrintableValue(3, 'type')
    STARTUP_FRAMES = PrintableValue(4, 'startup')
    ON_BLOCK_FRAMES = PrintableValue(5, 'block')
    ON_HIT_FRAMES = PrintableValue(6, 'hit')
    COUNTER_HIT_FRAMES = PrintableValue(7, 'counter')
    ACTIVE_FRAMES = PrintableValue(8, 'active')
    TRACKING = PrintableValue(9, 'track')
    TOTAL_FRAMES = PrintableValue(10, 'total')
    RECOVERY_FRAMES = PrintableValue(11, 'recovery')
    OPPONET_FRAMES = PrintableValue(12, 'opponent')
    NOTES = PrintableValue(13, 'notes')

    @staticmethod
    def max_column_lenght():
        return max(
            [
                len(column.printable_name)
                for column in Columns
            ]
        )
