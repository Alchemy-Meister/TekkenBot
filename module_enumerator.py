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
Helper to obtain the base adress of a module
"""

import win32.kernel32 as kernel32

def get_module_base_address(pid, module_name):
    """
    Return the base address of a module given its name and process identifier.
    @type  pid: int
    @param pid: the identifier of the process in which the module is loaded.
    @type  process_name: str
    @param process_name: string by which the modules is identified.
    """
    address_to_return = None
    h_module_snap = None
    try:
        h_module_snap = kernel32.create_tool_help32snapshot(
            kernel32.TH32CS_SNAPMODULE, pid
        )
        try:
            me32 = kernel32.module32first(h_module_snap)
            while me32:
                if module_name.encode('ascii') == me32.sz_module:
                    address_to_return = me32.mod_base_addr
                    break
                me32 = kernel32.module32next(h_module_snap, me32)
            kernel32.close_handle(h_module_snap)
            return address_to_return
        except OSError:
            kernel32.close_handle(h_module_snap)
    except:
        print(
            'This error is for using 32-bit Python. Try the 64-bit version.'
        )
        raise
