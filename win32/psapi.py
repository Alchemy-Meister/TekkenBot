#!/usr/bin/env python3

# Copyright (c) 2009-2018, Mario Vilas
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
Wrapper for psapi.dll in ctypes.
"""
import ctypes
# pylint: disable=unused-wildcard-import,wildcard-import
from .defines import *  #NOQA

#==============================================================================
# This is used later on to calculate the list of exported symbols.
_ALL = None
_ALL = set(vars().keys())
#==============================================================================

#--- psapi.dll ----------------------------------------------------------------

def enum_processes():
    """
    Return the process identifier for each process object in the system
    as a list.

    BOOL WINAPI EnumProcesses(
        __out  DWORD *pProcessIds,
        __in   DWORD cb,
        __out  DWORD *pBytesReturned
    );
    """
    _enum_processes = WINDLL.psapi.EnumProcesses
    _enum_processes.argtypes = [LPVOID, DWORD, LPVOID]
    _enum_processes.restype = bool
    _enum_processes.errcheck = raise_if_zero

    size = 0x1000
    cb_bytes_returned = DWORD()
    unit = SIZE_OF(DWORD)
    while 1:
        process_ids = (DWORD * (size // unit))()
        cb_bytes_returned.value = size
        _enum_processes(
            BY_REF(process_ids), cb_bytes_returned, BY_REF(cb_bytes_returned)
        )
        returned = cb_bytes_returned.value
        if returned < size:
            break
        size += 0x1000

    return list(process_ids[:(cb_bytes_returned.value // unit)])

def get_process_image_file_name_a(h_process):
    """
    DWORD WINAPI GetProcessImageFileName(
        __in   HANDLE hProcess,
        __out  LPSTR lpImageFileName,
        __in   DWORD nSize
    );
    """

    _get_process_image_filename_a = WINDLL.psapi.GetProcessImageFileNameA
    _get_process_image_filename_a.argtypes = [HANDLE, LPSTR, DWORD]
    _get_process_image_filename_a.restype = DWORD

    n_size = MAX_PATH
    while 1:
        lp_filename = ctypes.create_string_buffer(b'', n_size)
        n_copied = _get_process_image_filename_a(h_process, lp_filename, n_size)
        if not n_copied:
            raise ctypes.WinError()
        if n_copied <= n_size:
            break
        n_size += MAX_PATH
    return lp_filename.value

def get_process_image_file_name_w(h_process):
    """
    DWORD WINAPI GetProcessImageFileName(
        __in   HANDLE hProcess,
        __out  LPWSTR lpImageFileName,
        __in   DWORD nSize
    );
    """

    _get_process_image_filename_w = WINDLL.psapi.GetProcessImageFileNameW
    _get_process_image_filename_w.argtypes = [HANDLE, LPWSTR, DWORD]
    _get_process_image_filename_w.restype = DWORD

    n_size = MAX_PATH
    while 1:
        lp_filename = ctypes.create_unicode_buffer('', n_size)
        n_copied = _get_process_image_filename_w(h_process, lp_filename, n_size)
        if not n_copied:
            raise ctypes.WinError()
        if n_copied <= n_size:
            break
        n_size += MAX_PATH
    return lp_filename.value

GET_PROCESS_IMAGE_FILE_NAME = GuessStringType(
    get_process_image_file_name_a, get_process_image_file_name_w
)

#==============================================================================
# This calculates the list of exported symbols.
_ALL = set(vars().keys()).difference(_ALL)
__all__ = [_x for _x in _ALL if not _x.startswith('_')]
__all__.sort()
#==============================================================================
