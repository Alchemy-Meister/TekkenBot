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
Wrapper for winmm.dll in ctypes.
"""
import ctypes

# pylint: disable=unused-wildcard-import,wildcard-import
from .defines import *  #NOQA

MAX_ERROR_LENGTH = 128

def __mci_get_error_string(
        function, fdw_error, lpsz_error_text, cch_error_text
):
    known_error = function(fdw_error, lpsz_error_text, cch_error_text)
    if not known_error:
        return ''
    return lpsz_error_text.value


def mci_get_error_string_a(
        fdw_error, lpsz_error_text=None, cch_error_text=MAX_ERROR_LENGTH
):
    """
    BOOL mciGetErrorStringA(
        DWORD  fdwError,
        LPTSTR lpszErrorText,
        UINT   cchErrorText
    );
    """
    _mci_get_error_string_a = WINDLL.winmm.mciGetErrorStringA
    _mci_get_error_string_a.argtypes = [DWORD, LPSTR, UINT]

    if lpsz_error_text is None:
        lpsz_error_text = ctypes.create_string_buffer(b'', MAX_ERROR_LENGTH)

    return __mci_get_error_string(
        _mci_get_error_string_a, fdw_error, lpsz_error_text, cch_error_text
    )

def mci_get_error_string_w(
        fdw_error, lpsz_error_text=None, cch_error_text=MAX_ERROR_LENGTH
):
    """
    BOOL mciGetErrorStringW(
        DWORD  fdwError,
        LPTWSTR lpszErrorText,
        UINT   cchErrorText
    );
    """
    _mci_get_error_string_w = WINDLL.winmm.mciGetErrorStringW
    _mci_get_error_string_w.argtypes = [DWORD, LPWSTR, UINT]
    _mci_get_error_string_w.restype = bool

    if lpsz_error_text is None:
        lpsz_error_text = ctypes.create_unicode_buffer('', MAX_ERROR_LENGTH)

    return __mci_get_error_string(
        _mci_get_error_string_w, fdw_error, lpsz_error_text, cch_error_text
    )

def mci_get_error_string(
        fwd_error, lpsz_error_text=None, cch_error_text=MAX_ERROR_LENGTH
):
    return GuessStringType(mci_get_error_string_a, mci_get_error_string_w)(
        fwd_error, lpsz_error_text, cch_error_text
    )

def __mci_string_string(
        function, lpsz_command, lpsz_return_string, cch_return, hwnd_callback
):
    error = function(
        lpsz_command, lpsz_return_string, cch_return, hwnd_callback
    )
    if error:
        raise ctypes.WinError(
            error, mci_get_error_string(error)
        )

def mci_send_string_a(lpsz_command, cch_return, hwnd_callback):
    """
    MCIERROR mciSendStringA(
        LPCSTR lpszCommand,
        LPSTR  lpszReturnString,
        UINT    cchReturn,
        HANDLE  hwndCallback
    );
    """
    _mci_send_string_a = WINDLL.winmm.mciSendStringA
    _mci_send_string_a.argtypes = [LPSTR, LPSTR, UINT, HANDLE]
    _mci_send_string_a.restype = int

    if cch_return:
        lpsz_return_string = ctypes.create_string_buffer(b'', cch_return)
    else:
        lpsz_return_string = NULL
    return __mci_string_string(
        _mci_send_string_a,
        lpsz_command,
        lpsz_return_string,
        cch_return,
        hwnd_callback
    )

def mci_send_string_w(lpsz_command, cch_return, hwnd_callback):
    """
    MCIERROR mciSendStringA(
        LPCSTR lpszCommand,
        LPSTR  lpszReturnString,
        UINT    cchReturn,
        HANDLE  hwndCallback
    );
    """
    _mci_send_string_w = WINDLL.winmm.mciSendStringW
    _mci_send_string_w.argtypes = [LPWSTR, LPWSTR, UINT, HANDLE]
    _mci_send_string_w.restype = int

    if cch_return:
        lpsz_return_string = ctypes.create_unicode_buffer('', cch_return)
    else:
        lpsz_return_string = NULL
    return __mci_string_string(
        _mci_send_string_w,
        lpsz_command,
        lpsz_return_string,
        cch_return,
        hwnd_callback
    )

def mci_send_string(lpsz_command, cch_return=0, hwnd_callback=NULL):
    return GuessStringType(mci_send_string_a, mci_send_string_w)(
        lpsz_command, cch_return, hwnd_callback
    )
