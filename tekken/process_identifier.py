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

from win32.defines import SIZE_OF, ULONGLONG
import win32.kernel32 as kernel32

class ProcessIO():
    """
    """
    def __init__(self, config, pid, module_address):
        self.pid = pid
        self.module_address = module_address
        self.config = config
        self.reacquire_module_address = True

    def set_process_info(self, pid, module_address):
        """
        """
        self.pid = pid
        self.module_address = module_address

    def is_pid_valid(self):
        """
        """
        return (
            self.pid > -1
            # and self.pid == pid_searcher.get_pid_by_unique_process_name(
            #     self.process_name
            # )
        )

    def get_pointer_value(self, process_handle, address):
        """
        """
        try:
            address = kernel32.read_process_memory(
                process_handle, address, SIZE_OF(ULONGLONG)
            )
            return int.from_bytes(address, byteorder='little')
        except OSError:
            return None

    def get_address_of_multilevel_pointer(self, process_handle, dict_key):
        """
        """
        addresses_str = self.config['NonPlayerDataAddresses'][dict_key]
        # The pointer trail is stored as a string of addresses in hex in the
        # config. Split them up and convert.
        addresses = list(map(lambda x: int(x, 16), addresses_str.split()))
        address = self.module_address
        for i, offset in enumerate(addresses):
            if i + 1 < len(addresses):
                address = self.get_pointer_value(
                    process_handle, address + offset
                )
                if not address:
                    address = None
                    break
            else:
                address += offset
        return address

    def _reacquire_everything(self):
        """
        """
        self.pid = -1
        self.reacquire_module_address = True
        self.module_address = 0
