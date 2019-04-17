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
from ConfigReader import ReloadableConfig
import MovelistParser

import module_enumerator
import pid_searcher
# pylint: disable=unused-wildcard-import,wildcard-import
from win32.defines import *  #NOQA
import win32.kernel32 as kernel32
import win32.user32 as user32

from tekken.bot_snapshot import BotSnapshot
from tekken.game_snapshot import GameSnapshot

class TekkenGameReader:
    """

    """
    PROCESS_NAME = 'TekkenGame-Win64-Shipping.exe'

    def __init__(self):
        self.pid = -1
        self.reacquire_game_state = True
        self.reacquire_module_base_address = True
        self.reacquire_names = True
        self.module_address = 0
        self.original_facing = None
        self.opponent_name = None
        self.opponent_side = None
        self.is_player_player_one = None
        self.config = ReloadableConfig('memory_address', parse_nums=True)
        # , #lambda x: int(x, 16))
        self.player_data_pointer_offset = (
            self.config['MemoryAddressOffsets']['player_data_pointer_offset']
        )
        self.p1_movelist = []
        self.p2_movelist = []
        self.p1_movelist_to_use = None
        self.p2_movelist_to_use = None
        self.p1_movelist_parser = None
        self.p2_movelist_parser = None

    def reacquire_everything(self):
        """

        """
        self.reacquire_module_base_address = True
        self.reacquire_game_state = True
        self.reacquire_names = True
        self.pid = -1

    def get_value_from_address(
            self, process_handle, address, is_float=False,
            is_64bit=False, is_string=False
    ):
        """

        """
        t_size = None
        if is_string:
            t_size = 16
        elif is_64bit:
            t_size = SIZE_OF(ULONGLONG)
        else:
            t_size = SIZE_OF(ULONG)

        try:
            data = kernel32.read_process_memory(
                process_handle, address, t_size
            )
            if is_string:
                try:
                    return data.decode('utf-8')
                except UnicodeError:
                    print("ERROR: Couldn't decode string from memory")
                    return 'ERROR'
            elif is_float:
                return struct.unpack('<f', data)[0]
            else:
                return int.from_bytes(data, byteorder='little')
        except OSError:
            print(
                'Read process memory. Error: Code {}'.format(
                    kernel32.get_last_error()
                )
            )
            self.reacquire_everything()

    def get_block_data(self, process_handle, address, size_of_block):
        """

        """
        try:
            data = kernel32.read_process_memory(
                process_handle, address, size_of_block
            )
        except OSError:
            print(
                'Getting Block of Data Error: Code {}'.format(
                    kernel32.get_last_error()
                )
            )
        return data

    def get_value_from_data_block(
            self, frame, offset, player_2_offset=0x0, is_float=False
    ):
        """

        """
        address = offset
        address += player_2_offset
        t_bytes = frame[address: address + 4]
        if not is_float:
            return struct.unpack('<I', t_bytes)[0]
        return struct.unpack('<f', t_bytes)[0]

    def get_value_at_end_of_pointer_trail(
            self, process_handle, data_type, is_string
    ):
        """

        """
        addresses_str = self.config['NonPlayerDataAddresses'][data_type]
        # The pointer trail is stored as a string of addresses in hex in the
        # config. Split them up and convert.
        addresses = list(map(hex2int, addresses_str.split()))
        value = self.module_address
        for i, offset in enumerate(addresses):
            if i + 1 < len(addresses):
                value = self.get_value_from_address(
                    process_handle, value + offset, is_64bit=True)
            else:
                value = self.get_value_from_address(
                    process_handle, value + offset, is_string=is_string)
        return value

    def is_tekken_foreground_wnd(self):
        """

        """
        try:
            foreground_window = user32.get_foreground_window()
            _, pid = user32.get_window_thread_process_id(foreground_window)
            return pid == self.pid
        except OSError:
            # The foreground window can be NULL in certain circumstances,
            # such as when a window is losing activation.
            return False

    def get_tekken_window_rect(self):
        """

        """
        # see (https://stackoverflow.com/questions/21175922/enumerating
        # -windows-trough-ctypes-in-python) for clues for doing this without
        # needing focus using WindowsEnum
        if self.is_tekken_foreground_wnd():
            return user32.get_window_rect(user32.get_foreground_window())
        return None

    def is_pid_valid(self):
        """

        """
        return self.pid > -1

    def is_data_a_float(self, data):
        """

        """
        return data in (
            'x', 'y', 'z', 'activebox_x', 'activebox_y', 'activebox_z'
        )

    def get_updated_state(self, rollback_frame=0):
        """

        """
        game_snapshot = None

        if not self.is_pid_valid():
            self.pid = pid_searcher.get_pid_by_unique_process_name(
                TekkenGameReader.PROCESS_NAME
            )
            if self.is_pid_valid():
                print('Tekken PID acquired: {}'.format(self.pid))
            else:
                print('Tekken PID not acquired. Trying to acquire...')
            return game_snapshot

        if self.reacquire_module_base_address:
            print(
                'Trying to acquire Tekken library in PID: {}'.format(self.pid)
            )
            self.module_address = module_enumerator.get_module_base_address(
                self.pid, TekkenGameReader.PROCESS_NAME
            )
            if self.module_address is None:
                print(
                    '{} not found. Likely wrong process ID.'.format(
                        TekkenGameReader.PROCESS_NAME
                    ) + 'Reacquiring PID.'
                )
                self.reacquire_everything()
            elif(
                    self.module_address != (
                        self.config
                        ['MemoryAddressOffsets']['expected_module_address']
                    )
            ):
                print(
                    'Unrecognized location for {} module.'.format(
                        TekkenGameReader.PROCESS_NAME
                    ) + 'Tekken.exe Patch? Wrong process id?'
                )
            else:
                print('Found {}'.format(TekkenGameReader.PROCESS_NAME))
                self.reacquire_module_base_address = False

        if self.module_address is not None:
            process_handle = kernel32.open_process(
                kernel32.PROCESS_VM_READ, False, self.pid
            )
            try:
                player_data_base_address = self.get_value_from_address(
                    process_handle,
                    self.module_address + self.player_data_pointer_offset,
                    is_64bit=True
                )
                if player_data_base_address == 0:
                    if not self.reacquire_game_state:
                        print('No fight detected. Gamestate not updated.')
                    self.reacquire_game_state = True
                    self.reacquire_names = True
                else:
                    last_eight_frames = []
                    second_address_base = self.get_value_from_address(
                        process_handle, player_data_base_address, is_64bit=True)
                    # for rollback purposes, there are 8 copies of the
                    # game state, each one updatating once every 8 frames
                    for i in range(8):
                        potential_second_address = (
                            second_address_base
                            + i
                            * self.config
                            ['MemoryAddressOffsets']
                            ['rollback_frame_offset']
                        )
                        potential_frame_count = self.get_value_from_address(
                            process_handle,
                            potential_second_address
                            + self.config['GameDataAddress']['frame_count']
                        )
                        last_eight_frames.append(
                            (potential_frame_count, potential_second_address))

                    if rollback_frame >= len(last_eight_frames):
                        print(
                            'ERROR: requesting {} frame of {} '.format(
                                rollback_frame, len(last_eight_frames)
                            ) + 'long rollback frame'
                        )
                        rollback_frame = len(last_eight_frames) - 1

                    best_frame_count, player_data_second_address = sorted(
                        last_eight_frames, key=lambda x: -x[0]
                    )[rollback_frame]

                    player_data_frame = self.get_block_data(
                        process_handle, player_data_second_address,
                        self.config
                        ['MemoryAddressOffsets']['rollback_frame_offset']
                    )

                    bot_facing = self.get_value_from_data_block(
                        player_data_frame,
                        self.config['GameDataAddress']['facing']
                    )
                    p1_bot, p2_bot = self.initialize_bots(
                        player_data_frame, bot_facing, best_frame_count
                    )

                    if self.reacquire_names:
                        if(
                                p1_bot.is_character_name_loaded()
                                and p2_bot.is_character_name_loaded()
                        ):
                            self.opponent_name = (
                                self.get_value_at_end_of_pointer_trail(
                                    process_handle, "OPPONENT_NAME", True
                                )
                            )
                            self.opponent_side = (
                                self.get_value_at_end_of_pointer_trail(
                                    process_handle, "OPPONENT_SIDE", False
                                )
                            )
                            self.is_player_player_one = (
                                self.opponent_side == 1
                            )
                            # print(self.opponent_char_id)
                            # print(self.is_player_player_one)

                            self.p1_movelist_to_use = (
                                p1_bot.get_movelist_to_use()
                            )
                            self.p2_movelist_to_use = (
                                p2_bot.get_movelist_to_use()
                            )

                            self.p1_movelist_block, p1_movelist_address = (
                                self.populate_movelists(
                                    process_handle, 'P1_Movelist'
                                )
                            )
                            self.p2_movelist_block, p2_movelist_address = (
                                self.populate_movelists(
                                    process_handle, 'P2_Movelist'
                                    )
                            )

                            self.p1_movelist_parser = (
                                MovelistParser.MovelistParser(
                                    self.p1_movelist_block, p1_movelist_address
                                )
                            )
                            self.p2_movelist_parser = (
                                MovelistParser.MovelistParser(
                                    self.p2_movelist_block, p2_movelist_address
                                )
                            )

                            # self.write_movelists_to_file(
                            #    self.p1_movelist_block, p1_bot.character_name
                            # )
                            # self.write_movelists_to_file(
                            #    self.p2_movelist_block, p2_bot.character_name
                            # )

                            # TODO: figure out the actual size of the name
                            # movelist
                            self.p1_movelist_names = self.p1_movelist_block[
                                0x2E8:200000
                            ].split(b'\00')
                            self.p2_movelist_names = self.p2_movelist_block[
                                0x2E8:200000
                            ].split(b'\00')
                            #print(self.p1_movelist_names[(1572 * 2)])

                            self.reacquire_names = False

                    timer_in_frames = self.get_value_from_data_block(
                        player_data_frame,
                        self.config['GameDataAddress']['timer_in_frames']
                    )

                    game_snapshot = GameSnapshot(
                        p1_bot, p2_bot, best_frame_count, timer_in_frames,
                        bot_facing, self.opponent_name,
                        self.is_player_player_one
                    )

            finally:
                kernel32.close_handle(process_handle)

        return game_snapshot

    def initialize_bots(self, player_data_frame, bot_facing, best_frame_count):
        """

        """
        p1_bot_data_dict = {}
        p2_bot_data_dict = {}
        for data_type, value in self.config['PlayerDataAddress'].items():
            p1_value = self.get_value_from_data_block(
                player_data_frame, value,
                0, self.is_data_a_float(data_type)
            )
            p2_value = self.get_value_from_data_block(
                player_data_frame, value,
                self.config
                ['MemoryAddressOffsets']
                ['p2_data_offset'],
                self.is_data_a_float(data_type)
            )
            p1_bot_data_dict['PlayerDataAddress.' + data_type] = p1_value
            p2_bot_data_dict['PlayerDataAddress.' + data_type] = p2_value

        for data_type, value in (
                self.config['EndBlockPlayerDataAddress'].items()
        ):
            p1_value = self.get_value_from_data_block(player_data_frame, value)
            p2_value = self.get_value_from_data_block(
                player_data_frame, value,
                self.config
                ['MemoryAddressOffsets']
                ['p2_end_block_offset']
            )
            p1_bot_data_dict[
                'EndBlockPlayerDataAddress.' + data_type
            ] = p1_value
            p2_bot_data_dict[
                'EndBlockPlayerDataAddress.' + data_type
            ] = p2_value

        # pda = self.config['PlayerDataAddress']
        # This is ugly and hacky
        for axis, starting_address in (
                (k, v) for k, v in
                self.config['PlayerDataAddress'].items()
                if k in ('x', 'y', 'z')
        ):
            # Our xyz coordinate is 32 bytes, a 4 byte x, y, and z value
            # followed by five 4 byte values that don't change
            position_offset = 32
            p1_coord_array = []
            p2_coord_array = []
            for i in range(23):
                p1_coord_array.append(
                    self.get_value_from_data_block(
                        player_data_frame,
                        starting_address + i * position_offset,
                        0, is_float=True
                    )
                )
                p2_coord_array.append(
                    self.get_value_from_data_block(
                        player_data_frame,
                        starting_address + i * position_offset,
                        self.config
                        ['MemoryAddressOffsets']
                        ['p2_data_offset'],
                        is_float=True
                    )
                )
            p1_bot_data_dict['PlayerDataAddress.' + axis] = p1_coord_array
            p2_bot_data_dict['PlayerDataAddress.' + axis] = p2_coord_array
            # print("numpy.array(" + str(p1_coord_array) + ")")
        # list = p1_bot_data_dict[self.config['PlayerDataAddress']['y']]
        # print('{} [{}]'.format(max(list), list.index(max(list))))
        # print("--------------------")

        # FIXME: This seems like it would always be true.
        # The old code seems to be doing the same, so I don't know.
        p1_bot_data_dict['use_opponent_movelist'] = (
            p1_bot_data_dict[
                'PlayerDataAddress.movelist_to_use'
            ] == self.p2_movelist_to_use
        )
        p2_bot_data_dict['use_opponent_movelist'] = (
            p2_bot_data_dict[
                'PlayerDataAddress.movelist_to_use'
            ] == self.p1_movelist_to_use
        )
        p1_bot_data_dict['movelist_parser'] = (
            self.p1_movelist_parser
        )
        p2_bot_data_dict['movelist_parser'] = (
            self.p2_movelist_parser
        )

        if self.original_facing is None and best_frame_count > 0:
            self.original_facing = bot_facing > 0

        if self.reacquire_game_state:
            print('Fight detected. Updating gamestate.')
        self.reacquire_game_state = False

        p1_bot = BotSnapshot(p1_bot_data_dict)
        p2_bot = BotSnapshot(p2_bot_data_dict)

        return p1_bot, p2_bot

    def write_movelists_to_file(self, movelist, name):
        """
        
        """
        with open('RawData/' + name + ".dat", 'wb') as file:
            file.write(movelist)

    def populate_movelists(self, process_handle, data_type):
        """

        """
        movelist_str = self.config["NonPlayerDataAddresses"][data_type]
        movelist_trail = list(map(hex2int, movelist_str.split()))

        movelist_address = self.get_value_from_address(
            process_handle, self.module_address + movelist_trail[0],
            is_64bit=True
        )
        movelist_block = self.get_block_data(
            process_handle, movelist_address,
            self.config["MemoryAddressOffsets"]["movelist_size"]
        )
        return movelist_block, movelist_address

    def is_state_reacquisition_required(self):
        """
        """
        return self.reacquire_game_state

def hex2int(number):
    """
    """
    return int(number, 16)
