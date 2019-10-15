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

from collections import Counter, defaultdict, OrderedDict
from pprint import pformat
import struct

from constants.movelist import (
    MovelistButtonInput, MovelistButtonState, MovelistInput
)
from log import LogUtils
from tekken.data.structures.movelist import MoveNodeStruct
from tekken.data.wrappers.movelist import MoveNodeWrapper
from win32.defines import SIZE_OF

class MovelistParser:

    MOVE_NODE_SIZE = SIZE_OF(MoveNodeStruct)
    EMPTY_CANCEL_STRINGS = ['b', '_B', '_R_D', 'y', 'Rv', '_R', '_D', 'Y']
    __logger = None

    def __init__(self, movelist_bytes, movelist_pointer):
        self.bytes = movelist_bytes
        self.pointer = movelist_pointer

        if MovelistParser.__logger is None:
            MovelistParser.__logger = LogUtils.initialize_module_logger(
                __name__
            )

        self.parse_header()

    def parse_header(self):
        header_length = 0x2e8
        header_bytes = self.bytes[0:header_length]
        identifier = self.header_line(0)
        char_name_address = self.header_line(1)
        developer_name_address = self.header_line(2)
        date_address = self.header_line(3)
        timestamp_address = self.header_line(4)

        #print ('{:x}'.format(date_address - self.pointer))
        self.char_name = self.bytes[
            char_name_address:developer_name_address
        ].strip(b'\00').decode('utf-8')
        self.__logger.info('Parsing movelist for %s', self.char_name)

        unknown_regions = {}
        for i in range(42, 91, 2):
            unknown_regions[i] = self.header_line(i)
            #print(unknown_regions[i])

        #self.names = self.bytes[timestamp_address:unknown_regions[42]]
        self.names_double = self.bytes[
            header_length:unknown_regions[42]
        ].split(b'\00')[4:]
        self.names = []
        for i in range(0, len(self.names_double) - 1, 2):
            self.names.append(self.names_double[i].decode('utf-8'))
            # + '/' + self.names_double[i+1].decode('utf-8'))

        #there's two regions of move nodes, first one might be blocks????
        move_nodes_raw = self.bytes[unknown_regions[54]:unknown_regions[58]]
        self.move_nodes = [
            MoveNodeWrapper(
                move_nodes_raw[
                    index:index + MovelistParser.MOVE_NODE_SIZE
                ],
                self.names
            )
            for index in range(
                0, len(move_nodes_raw), MovelistParser.MOVE_NODE_SIZE
            )
        ]
        self.__logger.debug('movelist nodes: %s', pformat(self.move_nodes))

        self.linked_nodes_raw = self.bytes[
            unknown_regions[46]:unknown_regions[48]
        ]
        self.linked_nodes = []
        #for i in range(0, len(self.linked_nodes_raw), 24):

        #for node in self.move_nodes:
            #if node.move_id == 324:
                #print(node.move_id)


        #self.print_nodes(0x180)

        #print('{:x}'.format(unknown_regions[54] + self.pointer))
        #print(self.bytes[date_address:timestamp_address])
        #uniques = []
        #for node in self.move_nodes:
            #uniques.append(node.button_press)
        #counter = Counter(uniques)
        #for key, value in sorted(counter.items()):
            #print('{} | {}'.format(key, value))

        #with open('movelist' + self.char_name + '.txt', 'w') as fw:
            #for node in self.move_nodes:
                #fw.write(str(node) + '\n')
            #for name in self.names:
                #fw.write(name + '\n')

        #for node in self.move_nodes:
            #if node.unknown_buton_press == 4:
                #print(node)
        self.can_move_be_done_from_neutral = {}

        for node in self.move_nodes:
            move_id = node.move_id
            if not move_id in self.can_move_be_done_from_neutral:
                self.can_move_be_done_from_neutral[move_id] = False
            if node.cancel_window_1 >= 0x7FFF:
                self.can_move_be_done_from_neutral[move_id] = True

        self.democratically_chosen_input = {}
        for node in self.move_nodes:
            if not node.move_id in self.democratically_chosen_input:
                self.democratically_chosen_input[node.move_id] = []
            self.democratically_chosen_input[node.move_id].append(
                (node.direction, node.button_input, node.button_state)
            )

        sort_directions = defaultdict(lambda: 0, {})
        sort_attacks = defaultdict(lambda: 0, {})
        sort_presses = defaultdict(lambda: 0, {})

        sort_directions[MovelistInput.FULL_CROUCH] = 110
        sort_directions[MovelistInput.UP_FORWARD] = 103
        sort_directions[MovelistInput.UP] = 102
        sort_directions[MovelistInput.UP_BACK] = 101
        sort_directions[MovelistInput.NEUTRAL] = 100
        sort_directions[MovelistInput.WHILE_STANDING] = 90
        sort_directions[MovelistInput.UP_FORWARD] = 80
        sort_directions[MovelistInput.NULL] = -1

        sort_attacks[MovelistButtonInput.B_1] = 100
        sort_attacks[MovelistButtonInput.B_2] = 99
        sort_attacks[MovelistButtonInput.B_3] = 98
        sort_attacks[MovelistButtonInput.B_4] = 97

        sort_presses[MovelistButtonState.PRESS] = 100
        sort_presses[MovelistButtonState.NULL] = -2

        self.move_id_to_input = {}
        for move_id, candidates in self.democratically_chosen_input.items():
            candidates = list(OrderedDict.fromkeys(candidates))

            directions = sorted(
                candidates,
                key=lambda candidate_tuple: (
                    sort_directions[candidate_tuple[0]],
                    sort_presses[candidate_tuple[2]]
                ),
                reverse=True
            )[0]
            inputs = sorted(
                candidates,
                key=lambda candidate_tuple, values=candidates: (
                    sort_presses[candidate_tuple[2]],
                    Counter(values)[candidate_tuple],
                    sort_attacks[candidate_tuple[1]]
                ),
                reverse=True
            )[0]
            button_states = sorted(
                candidates,
                key=lambda candidate_tuple: sort_presses[candidate_tuple[2]],
                reverse=True
            )[0]

            self.move_id_to_input[move_id] = (
                directions[0], inputs[1], button_states[2]
            )
        # self.logger.debug('move_id_to_input: %s', self.move_id_to_input)

    def header_line(self, line):
        line_bytes = self.bytes[line * 8:(line+1) * 8]
        return struct.unpack('<Q', line_bytes)[0] - self.pointer

    def can_be_done_from_neutral(self, move_id):
        if move_id in self.can_move_be_done_from_neutral:
            return self.can_move_be_done_from_neutral[move_id]
        return True #blocking and damage moves

    def input_for_move(self, move_id, previous_move_id):
        if move_id in self.move_id_to_input:
            str_input = ''
            last_move_was_empty_cancel = False

            move_tuple = self.move_id_to_input[move_id]
            if not move_tuple[0] in (MovelistInput.NULL, MovelistInput.NEUTRAL):
                if(
                        -1 < move_id < len(self.names)
                        and '66' in self.names[move_id]
                        and not '666' in self.names[move_id]
                ):
                # and (
                # '66' in self.names[previous_move_id]
                # or 'DASH' in self.names[previous_move_id]
                # ):
                    str_input += 'ff'
                else:
                    try:
                        str_input += move_tuple[0].printable_name
                    except AttributeError:
                        str_input += str(move_tuple[0])

            if(
                    isinstance(move_tuple[2], MovelistButtonState)
                    and MovelistButtonState.RELEASE.name in move_tuple[2].name
            ):
                str_input += '*'
            #input += move_tuple[2]

            if not move_tuple[1] in (MovelistButtonInput.NULL,):
                try:
                    str_input += move_tuple[1].printable_name
                except AttributeError:
                    pass

            if(
                    -1 < previous_move_id < len(self.names)
                    and -1 < move_id < len(self.names)
            ):
                if self.names[previous_move_id] in (
                        [
                            self.names[move_id] + s
                            for s in MovelistParser.EMPTY_CANCEL_STRINGS
                        ]
                ):
                    # print(
                    # '{} : {}'.format(
                    #     self.names[previous_move_id], self.names[move_id])
                    # )
                    last_move_was_empty_cancel = True

            return str_input, last_move_was_empty_cancel
        return 'N/A', False

    def print_nodes(self, node_id):
        for node in self.move_nodes:
            if node_id == node.move_id:
                print(node)
