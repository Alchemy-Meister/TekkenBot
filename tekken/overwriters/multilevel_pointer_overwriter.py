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
from tekken.overwriters import Overwriter
from win32.defines import SIZE_OF, ULONGLONG
import win32.kernel32 as kernel32
import win32.utils.type_limits as type_limits

class MultilevelPointerOverwriter(Overwriter):
    """
    """
    def write(self):
        process_handle = kernel32.open_process(
            kernel32.PROCESS_ALL_ACCESS, False, self.process_memory.pid
        )
        if isinstance(self.process_memory.address[0], list):
            for offsets in self.process_memory.address:
                self.__write_on_multilevel_pointer(process_handle, offsets)
        else:
            self.__write_on_multilevel_pointer(
                process_handle, self.process_memory.address
            )

    def __write_on_multilevel_pointer(self, process_handle, offsets):
        address = self.__get_address_of_multilevel_pointer(
            process_handle, offsets
        )
        if address:
            try:
                if self.value != self._read_address(process_handle, address):
                    kernel32.write_process_memory(
                        process_handle, address, struct.pack(
                            type_limits.get_struct_format(self.value),
                            self.value
                        )
                    )
            except OSError:
                kernel32.close_handle(process_handle)
                raise

    def __get_address_of_multilevel_pointer(self, process_handle, addresses):
        address = self.process_memory.module_address
        for i, offset in enumerate(addresses):
            if i + 1 < len(addresses):
                address = self.__get_pointer_value(
                    process_handle, address + offset
                )
                if not address:
                    address = None
                    break
            else:
                address += offset
        return address

    @staticmethod
    def __get_pointer_value(process_handle, address):
        try:
            address = kernel32.read_process_memory(
                process_handle, address, SIZE_OF(ULONGLONG)
            )
            return struct.unpack('<Q', address)[0]
        except (OSError, struct.error):
            return None
