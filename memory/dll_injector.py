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

import win32.kernel32 as kernel32

class DLLInjector():
    def __init__(self, pid):
        self.h_process = kernel32.open_process(
            kernel32.PROCESS_ALL_ACCESS, False, pid
        )

    def inject(self, absolute_path):
        if not isinstance(absolute_path, str):
            absolute_path = str(absolute_path)
        load_library_address = kernel32.get_proc_address(
            kernel32.get_module_handle('kernel32.dll'),
            'LoadLibraryA'
        )
        return self.__create_remote_thread(
            load_library_address, absolute_path.encode('ascii')
        )

    def __create_remote_thread(self, function_address, args):
        args_size = len(args)
        args_address = kernel32.virtual_alloc_ex(
            self.h_process, dw_size=args_size
        )
        kernel32.write_process_memory(self.h_process, args_address, args)
        h_thread, _ = kernel32.create_remote_thread(
            self.h_process, function_address, args_address
        )
        h_thread.wait()
        kernel32.virtual_free_ex(self.h_process, args_address)
        return args_address
