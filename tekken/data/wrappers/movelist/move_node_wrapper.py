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

from constants.movelist import (
    MovelistActive, MovelistInput, MovelistButtonInput, MovelistButtonState
)
from tekken.data.structures.movelist import MoveNodeStruct
from tekken.data.wrappers import StructWrapper

class MoveNodeWrapper(StructWrapper):
    def __init__(self, block_bytes=None, names=None):
        super().__init__(MoveNodeStruct, block_bytes)

        if names and len(names) > getattr(self, 'move_id'):
            self.name = names[getattr(self, 'move_id')]
        else:
            self.name = 'unknown'

        try:
            setattr(
                self,
                'direction',
                MovelistInput(getattr(self, 'direction'))
            )
        except ValueError:
            pass

        try:
            setattr(
                self,
                'button_input',
                MovelistButtonInput(getattr(self, 'button_input'))
            )
        except ValueError:
            pass

        try:
            setattr(
                self,
                'button_state',
                MovelistButtonState(getattr(self, 'button_state'))
            )
        except ValueError:
            pass

        try:
            setattr(
                self,
                'active',
                MovelistActive(getattr(self, 'active'))
            )
        except ValueError:
            pass

    def __eq__(self, move_node):
        if isinstance(move_node, MoveNodeWrapper):
            return (
                getattr(self, 'move_id') == move_node.move_id
                and getattr(self, 'direction') == move_node.direction
                and getattr(self, 'button_input') == move_node.button_input
                and getattr(self, 'button_state') == move_node.button_state
            )
        return NotImplementedError

    def __ne__(self, move_node):
        return not self == move_node
