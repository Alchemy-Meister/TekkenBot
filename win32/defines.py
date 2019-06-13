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
Common definitions.
"""

import ctypes

# =============================================================================
# This is used later on to calculate the list of exported symbols.
_ALL = None
_ALL = set(vars().keys())
# =============================================================================

# -----------------------------------------------------------------------------

# Some stuff from ctypes we'll be using very frequently.
BY_REF = ctypes.byref
SIZE_OF = ctypes.sizeof
POINTER = ctypes.POINTER
WINDLL = ctypes.windll

class Structure(ctypes.Structure):
    """
    Automatically disable padding of structs and unions on 32 bits.
    """
    if SIZE_OF(ctypes.c_void_p) == 4:
        _pack_ = 1

# -----------------------------------------------------------------------------

def raise_if_zero(result, _func=None, _arguments=()):
    """
    Error checking for most Win32 API calls.
    The function is assumed to return an integer, which is C{0} on error.
    In that case the C{WindowsError} exception is raised.
    """
    if not result:
        raise ctypes.WinError()
    return result

class GuessStringType():
    """
    Decorator that guesses the correct version (A or W) to call
    based on the types of the strings passed as parameters.
    Calls the B{ANSI} version if the only string types are ANSI.
    Calls the B{Unicode} version if Unicode or mixed string types are passed.
    The default if no string arguments are passed depends on the value of the
    L{t_default} class variable.
    @type fn_ansi: function
    @ivar fn_ansi: ANSI version of the API function to call.
    @type fn_unicode: function
    @ivar fn_unicode: Unicode (wide) version of the API function to call.
    @type t_default: type
    @cvar t_default: Default string type to use.
        Possible values are:
         - type(b'') for ANSI
         - type('') for Unicode
    """

    # ANSI and Unicode types
    t_ansi = type(b'')
    t_unicode = type('')

    # Default is Unicode for Python 3.x
    t_default = t_unicode

    def __init__(self, fn_ansi, fn_unicode):
        """
        @type  fn_ansi: function
        @param fn_ansi: ANSI version of the API function to call.
        @type  fn_unicode: function
        @param fn_unicode: Unicode (wide) version of the API function to call.
        """
        self.fn_ansi = fn_ansi
        self.fn_unicode = fn_unicode

        # Copy the wrapped function attributes.
        try:
            self.__name__ = self.fn_ansi.__name__[:-1]  # remove the A or W
        except AttributeError:
            pass
        try:
            self.__module__ = self.fn_ansi.__module__
        except AttributeError:
            pass
        try:
            self.__doc__ = self.fn_ansi.__doc__
        except AttributeError:
            pass

    def __call__(self, *argv, **argd):
        # Get the types of all arguments for the function
        v_types = [type(item) for item in argv]
        v_types.extend([type(value) for (key, value) in argd.items()])

        # Get the appropriate function for the default type
        if self.t_default == self.t_unicode:
            function = self.fn_unicode
        else:
            function = self.fn_ansi

        # If at least one argument is a Unicode string...
        if self.t_unicode in v_types:

            # If al least one argument is an ANSI string,
            # convert all ANSI strings to Unicode
            if self.t_ansi in v_types:
                argv = list(argv)
                for index, argument in enumerate(argv):
                    if v_types[index] == self.t_ansi:
                        argv[index] = str(argument)
                for (key, value) in argd.items():
                    if isinstance(value, self.t_ansi):
                        argd[key] = str(value)

            # Use the W version
            function = self.fn_unicode

        # If at least one argument is an ANSI string,
        # but there are no Unicode strings...
        elif self.t_ansi in v_types:

            # Use the A version
            function = self.fn_ansi

        # Call the function and return the result
        return function(*argv, **argd)

class DefaultStringType():
    """
    Decorator that uses the default version (A or W) to call
    based on the configuration of the L{GuessStringType} decorator.
    @see: L{GuessStringType.t_default}
    @type fn_ansi: function
    @ivar fn_ansi: ANSI version of the API function to call.
    @type fn_unicode: function
    @ivar fn_unicode: Unicode (wide) version of the API function to call.
    """

    def __init__(self, fn_ansi, fn_unicode):
        """
        @type  fn_ansi: function
        @param fn_ansi: ANSI version of the API function to call.
        @type  fn_unicode: function
        @param fn_unicode: Unicode (wide) version of the API function to call.
        """
        self.fn_ansi = fn_ansi
        self.fn_unicode = fn_unicode

        # Copy the wrapped function attributes.
        try:
            self.__name__ = self.fn_ansi.__name__[:-1]  # remove the A or W
        except AttributeError:
            pass
        try:
            self.__module__ = self.fn_ansi.__module__
        except AttributeError:
            pass
        try:
            self.__doc__ = self.fn_ansi.__doc__
        except AttributeError:
            pass

    def __call__(self, *argv, **argd):

        # Get the appropriate function based on the default.
        if GuessStringType.t_default == GuessStringType.t_ansi:
            function = self.fn_ansi
        else:
            function = self.fn_unicode

        # Call the function and return the result
        return function(*argv, **argd)

# --- Types -------------------------------------------------------------------
# http://msdn.microsoft.com/en-us/library/aa383751(v=vs.85).aspx

# Map of basic C types to Win32 types
BOOL = ctypes.c_int32
BYTE = ctypes.c_ubyte
CHAR = ctypes.c_char
DOUBLE = ctypes.c_double
DWORD = ctypes.c_uint32
FLOAT = ctypes.c_float
LONG = ctypes.c_int32
LONGLONG = ctypes.c_int64
LPSTR = ctypes.c_char_p
LPWSTR = ctypes.c_wchar_p
LPVOID = ctypes.c_void_p
QWORD = ctypes.c_uint64
SBYTE = ctypes.c_byte
SHORT = ctypes.c_int16
UINT = ctypes.c_uint32
ULONG = ctypes.c_uint32
ULONGLONG = ctypes.c_uint64  # c_ulonglong
USHORT = ctypes.c_uint16
WCHAR = ctypes.c_wchar
WORD = ctypes.c_uint16

# Map size_t to SIZE_T
try:
    SIZE_T = ctypes.c_size_t
    SSIZE_T = ctypes.c_ssize_t
except AttributeError:
    # Size of a pointer
    SIZE_T = {1:BYTE, 2:WORD, 4:DWORD, 8:QWORD}[SIZE_OF(LPVOID)]

# Other Win32 types, more may be added as needed
PVOID = LPVOID
HANDLE = LPVOID
HMODULE = HANDLE
HWND = HANDLE
PHANDLE = POINTER(HANDLE)
LPHANDLE = PHANDLE
LPDWORD = POINTER(DWORD)
PDWORD = LPDWORD
# XXX ANSI by default?
TCHAR = CHAR

# --- Constants ---------------------------------------------------------------

INFINITE = -1
NULL = None

# Invalid handle value is -1 casted to void pointer.
try:
    INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value #-1 #0xFFFFFFFF
except TypeError:
    if SIZE_OF(ctypes.c_void_p) == 4:
        INVALID_HANDLE_VALUE = 0xFFFFFFFF
    elif SIZE_OF(ctypes.c_void_p) == 8:
        INVALID_HANDLE_VALUE = 0xFFFFFFFFFFFFFFFF
    else:
        raise

MAX_MODULE_NAME32 = 255
MAX_PATH = 260

# Error codes
ERROR_SUCCESS = 0
ERROR_NO_MORE_FILES = 18
ERROR_BAD_LENGTH = 24
ERROR_PARTIAL_COPY = 299
ERROR_IO_PENDING = 997

# =============================================================================
# This calculates the list of exported symbols.
_ALL = set(vars().keys()).difference(_ALL)
__all__ = [_x for _x in _ALL if not _x.startswith('_')]
__all__.sort()
# =============================================================================
