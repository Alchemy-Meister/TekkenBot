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
Helper to find process identifiers by their names
"""

import os
import traceback

import win32.psapi as psapi
import win32.kernel32 as kernel32

def get_pids_by_process_name(process_name):
    """
    Return the process identifier for each process object in the system that
    matches the given process name as a list.

    @type  process_name: str
    @param process_name: string by which the enum. of processes is filtered.
    """
    pids = []
    try:
        process_ids = psapi.enum_processes()
        for process_id in process_ids:
            try:
                h_process = kernel32.open_process(
                    kernel32.PROCESS_QUERY_INFORMATION, False, process_id
                )
                if h_process:
                    process_path = psapi.GET_PROCESS_IMAGE_FILE_NAME(h_process)
                    filename = os.path.basename(process_path)
                    if filename == process_name:
                        pids.append(process_id)
                    kernel32.close_handle(h_process)
            except OSError:
                pass
    except OSError:
        traceback.print_exc()

    return pids

def get_pid_by_unique_process_name(unique_process_name):
    """
    Return the process identifier of a process object known to have a
    unique process name. If not found, returns -1.
    @type  unique_process_name: str
    @param unique_process_name: unique string identifier by which the enum. of
    processes is filtered.
    """
    pids = get_pids_by_process_name(unique_process_name)
    return pids[0] if pids else -1
