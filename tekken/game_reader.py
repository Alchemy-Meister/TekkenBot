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
import traceback
import sys
import struct

# pylint: disable=unused-wildcard-import,wildcard-import
from win32.defines import *  #NOQA
import win32.kernel32 as kernel32
import win32.user32 as user32
import win32.utils.actual_rect as actual_rect

from .data.structures.graphic_settings import (
    GraphicSettingsStruct, ResolutionStruct
)
from .data.wrappers.graphic_settings import (
    GraphicSettingsWrapper, ResolutionWrapper
)
from .bot_snapshot import BotSnapshot
from .game_snapshot import GameSnapshot
from .parsers import MovelistParser
from .process_identifier import ProcessIO

class TekkenGameReader(ProcessIO):
    """
    """

    def __init__(self, config, pid, module_address=None):
        super().__init__(config, pid, module_address)
        self.reacquire_game_state = True
        self.reacquire_names = True
        self.original_facing = None
        self.opponent_name = None
        self.opponent_side = None
        self.is_player_player_one = None
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
        self.p1_movelist_names = None
        self.p2_movelist_names = None

        self.is_in_battle = False

        self.window_handler = 0

    def reacquire_everything(self):
        """
        """
        ProcessIO.reacquire_everything(self)
        self.reacquire_game_state = True
        self.reacquire_names = True
        self.window_handler = 0

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
                    sys.stdout.write(
                        "ERROR: Couldn't decode string from memory"
                    )
                    return 'ERROR'
            elif is_float:
                return struct.unpack('<f', data)[0]
            else:
                return int.from_bytes(data, byteorder='little')
        except Exception:
            sys.stdout.write(
                'Read process memory. Error: Code {}'.format(
                    kernel32.get_last_error()
                )
            )
            self.reacquire_everything()
            raise

    def get_block_data(self, process_handle, address, size_of_block):
        """
        """
        try:
            data = kernel32.read_process_memory(
                process_handle, address, size_of_block
            )
        except OSError:
            sys.stdout.write(
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
        addresses = self.config['NonPlayerDataAddresses'][data_type]
        value = self.module_address
        for i, offset in enumerate(addresses):
            if i + 1 < len(addresses):
                value = self.get_value_from_address(
                    process_handle, value + offset, is_64bit=True)
            else:
                value = self.get_value_from_address(
                    process_handle, value + offset, is_string=is_string)
        return value

    def get_graphic_settings(self, process_handle):
        graphic_settings = None
        try:
            graphic_setting_address = (
                self.module_address
                + self.config['GraphicSettingsAddress']['graphic_settings']
            )
            graphic_settings = GraphicSettingsWrapper(
                self.get_block_data(
                    process_handle,
                    graphic_setting_address,
                    SIZE_OF(GraphicSettingsStruct)
                )
            )
            startup_stable_resolution_address = (
                self.module_address
                + self.config['GraphicSettingsAddress']['window_resolution']
            )
            graphic_settings.resolution = (
                ResolutionWrapper(
                    self.get_block_data(
                        process_handle,
                        startup_stable_resolution_address,
                        SIZE_OF(ResolutionStruct)
                    )
                ).resolution
            )
            if(
                    graphic_settings.resolution != (0, 0)
                    and graphic_settings.resolution[0]
                    != graphic_settings.resolution[1]
            ):
                graphic_settings.position = self.get_tekken_window_position()
            else:
                graphic_settings = None
        except OSError:
            pass
        return graphic_settings

    def get_tekken_window_position(self):
        tekken_rect = user32.get_window_placement(
            self.window_handler
        ).rc_normal_position
        return (tekken_rect.left, tekken_rect.top)

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

    def is_tekken_fullscreen(self):
        monitor_info = user32.get_monitor_info(
            user32.monitor_from_window(
                self.window_handler, user32.MONITOR_DEFAULTTOPRIMARY
            )
        )
        return (
            user32.get_window_rect(self.window_handler)
            == monitor_info.rc_monitor
        )

    def is_tekken_borderless(self, h_wnd):
        style = user32.get_window_long_ptr(h_wnd, user32.GWL_STYLE)
        return not bool(style & user32.WS_CAPTION)

    def is_tekken_minimized(self):
        try:
            return user32.is_iconic(self.window_handler)
        except OSError:
            return False

    def get_titlebar_height(self):
        return (
            user32.get_system_metrics(user32.SM_CYFRAME)
            + user32.get_system_metrics(user32.SM_CYCAPTION)
            + user32.get_system_metrics(user32.SM_CXPADDEDBORDER)
        )

    def adapt_window_rect_to_title_bar(self, rect):
        rect.top += (
            user32.get_system_metrics(user32.SM_CYFRAME)
            + user32.get_system_metrics(user32.SM_CYCAPTION)
            + user32.get_system_metrics(user32.SM_CXPADDEDBORDER)
        )
        rect.bottom -= user32.get_system_metrics(user32.SM_CXBORDER)

    def get_tekken_window_rect(self, foreground_only=False):
        """
        """
        window_rect = None
        try:
            window_handler = None
            if foreground_only:
                if self.is_tekken_foreground_wnd():
                    window_handler = user32.get_foreground_window()
            else:
                window_handler = user32.find_window(
                    lp_class_name='UnrealWindow', lp_window_name='TEKKEN 7 '
                )
            if window_handler:
                if not self.is_tekken_fullscreen():
                    # Unstyled window + titlebar rect
                    window_rect = actual_rect.get_actual_rect(window_handler)
                    self.adapt_window_rect_to_title_bar(window_rect)
                else:
                    window_rect = user32.get_window_placement(
                        window_handler
                    ).rc_normal_position
        except OSError:
            pass
        return window_rect

    def is_data_a_float(self, data):
        """
        """
        return data in (
            'x', 'y', 'z', 'activebox_x', 'activebox_y', 'activebox_z'
        )

    def get_updated_state(self, rollback_frame=0):
        """
        """
        if self.is_pid_valid() and self.module_address is not None:
            game_state = [None, None]
            process_handle = kernel32.open_process(
                kernel32.PROCESS_VM_READ, False, self.pid
            )
            try:
                if not self.window_handler:
                    try:
                        self.window_handler = user32.find_window(
                            lp_class_name='UnrealWindow',
                            lp_window_name='TEKKEN 7 '
                        )
                    except OSError:
                        pass
                else:
                    game_state[0] = self.get_graphic_settings(process_handle)

                player_data_base_address = self.module_address
                for i, offset in enumerate(self.player_data_pointer_offset):
                    player_data_base_address = self.get_pointer_value(
                        process_handle, player_data_base_address + offset
                    )
                    if not player_data_base_address:
                        break

                if player_data_base_address == 0:
                    if not self.reacquire_game_state:
                        sys.stdout.write(
                            'No fight detected. Gamestate not updated.'
                        )
                        self.is_in_battle = False
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
                        sys.stdout.write(
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
                    timer_in_frames = self.get_value_from_data_block(
                        player_data_frame,
                        self.config['GameDataAddress']['timer_in_frames']
                    )
                    p1_bot, p2_bot = self.initialize_bots(
                        player_data_frame, bot_facing, best_frame_count
                    )

                    if self.reacquire_game_state:
                        self.reacquire_game_state = False
                        sys.stdout.write('Fight detected. Updating gamestate.')
                        self.is_in_battle = True

                    if self.reacquire_names:
                        if(
                                p1_bot.is_character_name_loaded()
                                and p2_bot.is_character_name_loaded()
                        ):
                            self.opponent_name = (
                                self.get_value_at_end_of_pointer_trail(
                                    process_handle, 'opponent_name', True
                                )
                            )
                            self.opponent_side = (
                                self.get_value_at_end_of_pointer_trail(
                                    process_handle, 'opponent_side', False
                                )
                            )
                            self.is_player_player_one = (
                                self.opponent_side == 1
                            )
                            # sys.stdout.write(self.opponent_char_id)
                            # sys.stdout.write(self.is_player_player_one)

                            self.p1_movelist_to_use = (
                                p1_bot.get_movelist_to_use()
                            )
                            self.p2_movelist_to_use = (
                                p2_bot.get_movelist_to_use()
                            )

                            p1_movelist_block, p1_movelist_address = (
                                self.populate_movelists(
                                    process_handle, 'p1_movelist'
                                )
                            )
                            p2_movelist_block, p2_movelist_address = (
                                self.populate_movelists(
                                    process_handle, 'p2_movelist'
                                    )
                            )

                            self.p1_movelist_parser = (
                                MovelistParser(
                                    p1_movelist_block, p1_movelist_address
                                )
                            )
                            self.p2_movelist_parser = (
                                MovelistParser(
                                    p2_movelist_block, p2_movelist_address
                                )
                            )

                            # self.write_movelists_to_file(
                            #    p1_movelist_block, p1_bot.character_name
                            # )
                            # self.write_movelists_to_file(
                            #    p2_movelist_block, p2_bot.character_name
                            # )
                            # TODO: figure out the actual size of the name
                            # movelist
                            self.p1_movelist_names = p1_movelist_block[
                                0x2E8:200000
                            ].split(b'\00')
                            self.p2_movelist_names = p2_movelist_block[
                                0x2E8:200000
                            ].split(b'\00')
                            #sys.stdout.write(p1_movelist_names[(1572 * 2)])

                            self.reacquire_names = False

                    game_state[1] = GameSnapshot(
                        p1_bot, p2_bot, best_frame_count, timer_in_frames,
                        bot_facing, self.opponent_name,
                        self.is_player_player_one
                    )
            except (OSError, struct.error, TypeError):
                traceback.print_exc()
                self.reacquire_everything()
                raise OSError
            finally:
                kernel32.close_handle(process_handle)
            return game_state
        raise OSError('invalid PID or module address')

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
            # sys.stdout.write("numpy.array(" + str(p1_coord_array) + ")")
        # list = p1_bot_data_dict[self.config['PlayerDataAddress']['y']]
        # sys.stdout.write('{} [{}]'.format(max(list), list.index(max(list))))
        # sys.stdout.write("--------------------")

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
        movelist_trail = self.config["NonPlayerDataAddresses"][data_type]
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
