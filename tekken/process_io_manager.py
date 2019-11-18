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

from collections import defaultdict
import sys

import module_enumerator
import pid_searcher
from config.reloadable_config_manager import ReloadableConfigManager
import win32.kernel32 as kernel32

from .game_reader import TekkenGameReader
from .process_writer import TekkenGameWritter

class ProcessIOManager():
    """
    """
    PROCESS_NAME = 'TekkenGame-Win64-Shipping.exe'

    def __init__(self):
        self.__config_manager = ReloadableConfigManager()
        self.memory_config = self.__config_manager.add_config(
            'memory_address.ini', parse=True
        )
        default_overwrite_config = self.__config_manager.add_config(
            'overwrite_default.ini', parse=True
        )

        self.__callback = kernel32.wait_or_timer_callback(
            self.__tekken_process_terminated
        )
        self.__process_info_update_required = False
        self.__print_pid_message = True
        self.__wait_handle = None

        pid = ProcessIOManager.__get_process_pid()

        self.process_reader = TekkenGameReader(self.memory_config, pid)
        self.process_writer = TekkenGameWritter(
            {
                'overwrite': self.memory_config['overwrite'],
                'default': default_overwrite_config['overwrite_default']
            },
            pid
        )
        if self.is_pid_valid():
            sys.stdout.write('Tekken PID acquired: {}'.format(pid))
            self.__register_for_tekken_terminated_state(pid)
            module_address = ProcessIOManager.__get_process_module_address(pid)
            self.process_reader.module_address = module_address
            self.process_writer.module_address = module_address
            self.process_writer.update_overwriters()

    def is_pid_valid(self):
        return (
            self.process_reader.is_pid_valid()
            and self.process_writer.is_pid_valid()
        )

    def update(self, rollback_frame=0):
        if self.__process_info_update_required:
            self.__update_process_info()

        try:
            self.process_writer.update()
            return self.process_reader.get_updated_state(
                rollback_frame=rollback_frame
            )
        except OSError:
            self.__process_info_update_required = True
            return defaultdict(lambda: None)

    def read_update(self, rollback_frame=0):
        try:
            return self.process_reader.get_updated_state(
                rollback_frame=rollback_frame
            )
        except OSError:
            self.__process_info_update_required = True
            return None

    @staticmethod
    def __get_process_pid():
        return pid_searcher.get_pid_by_unique_process_name(
            ProcessIOManager.PROCESS_NAME
        )

    @staticmethod
    def __get_process_module_address(pid):
        sys.stdout.write(
            'Trying to acquire Tekken library in PID: {}'.format(pid)
        )
        return module_enumerator.get_module_base_address(
            pid, ProcessIOManager.PROCESS_NAME
        )

    def __update_process_info(self):
        self.__process_info_update_required = False

        pid = ProcessIOManager.__get_process_pid()
        self.process_reader.pid = pid
        self.process_writer.pid = pid

        if self.is_pid_valid():
            self.__print_pid_message = True
            sys.stdout.write('Tekken PID acquired: {}'.format(pid))

            module_address = ProcessIOManager.__get_process_module_address(pid)
            self.process_reader.module_address = module_address
            self.process_writer.module_address = module_address

            if module_address is None:
                sys.stdout.write(
                    '{} not found. Most likely wrong process ID.'.format(
                        ProcessIOManager.PROCESS_NAME
                    ) + 'Reacquiring PID.'
                )
            elif(
                    module_address != (
                        self.memory_config
                        ['MemoryAddressOffsets']
                        ['expected_module_address']
                    )
            ):
                sys.stdout.write(
                    'Unrecognized location for {} module.'.format(
                        ProcessIOManager.PROCESS_NAME
                    ) + 'Tekken.exe Patch? Wrong process id?'
                )
            else:
                sys.stdout.write(
                    'Found {}'.format(ProcessIOManager.PROCESS_NAME)
                )
                self.__register_for_tekken_terminated_state(pid)
                self.process_writer.update_overwriters()
        else:
            if self.__print_pid_message:
                sys.stdout.write(
                    'Tekken PID not acquired. Trying to acquire...'
                )
                self.__print_pid_message = False

    def __register_for_tekken_terminated_state(self, pid):
        handle = kernel32.open_process(kernel32.SYNCHRONIZE, False, pid)
        self.__wait_handle = kernel32.register_wait_for_single_object(
            handle,
            self.__callback,
            None,
            dw_flags=kernel32.WT_EXECUTEONLYONCE
        )

    def __tekken_process_terminated(self, _lp_paramenter, _time_or_wait_fired):
        self.process_writer.reacquire_everything()
        self.process_reader.reacquire_everything()
        sys.stdout.write(
            '{} process terminated'.format(ProcessIOManager.PROCESS_NAME)
        )
        try:
            kernel32.unregister_wait(self.__wait_handle)
        except OSError:
            pass
