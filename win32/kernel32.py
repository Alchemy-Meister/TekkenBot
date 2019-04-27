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
Wrapper for kernel32.dll in ctypes.
"""

import ctypes
# pylint: disable=unused-wildcard-import,wildcard-import
from .defines import *  # NOQA
from .version import *  # NOQA

# =============================================================================
# This is used later on to calculate the list of exported symbols.
_ALL = None
_ALL = set(vars().keys())
_ALL.add('version')
# =============================================================================

# --- Constants ---------------------------------------------------------------
WAIT_FAILED = -1
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 0x102

# Standard access rights
SYNCHRONIZE = 0x00100000
STANDARD_RIGHTS_ALL = 0x001F0000
STANDARD_RIGHTS_REQUIRED = 0x000F0000

# Process access rights for OpenProcess
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020

# The values of PROCESS_ALL_ACCESS and THREAD_ALL_ACCESS were changed in
# Vista/2008
PROCESS_ALL_ACCESS_NT = (STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0xFFF)
PROCESS_ALL_ACCESS_VISTA = (STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0xFFFF)
THREAD_ALL_ACCESS_NT = (STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0x3FF)
THREAD_ALL_ACCESS_VISTA = (STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0xFFFF)
if NTDDI_VERSION < NTDDI_VISTA:
    PROCESS_ALL_ACCESS = PROCESS_ALL_ACCESS_NT
    THREAD_ALL_ACCESS = THREAD_ALL_ACCESS_NT
else:
    PROCESS_ALL_ACCESS = PROCESS_ALL_ACCESS_VISTA
    THREAD_ALL_ACCESS = THREAD_ALL_ACCESS_VISTA

# DuplicateHandle constants
DUPLICATE_SAME_ACCESS = 0x00000002

# GetHandleInformation / SetHandleInformation
HANDLE_FLAG_INHERIT = 0x00000001
HANDLE_FLAG_PROTECT_FROM_CLOSE = 0x00000002

# --- Handle wrappers ---------------------------------------------------------

class Handle(object):
    """
    Encapsulates Win32 handles to avoid leaking them.
    @type inherit: bool
    @ivar inherit: C{True} if the handle is to be inherited by child processes,
        C{False} otherwise.
    @type protectFromClose: bool
    @ivar protectFromClose: Set to C{True} to prevent the handle from being
        closed. Must be set to C{False} before you're done using the handle,
        or it will be left open until the debugger exits. Use with care!
    @see:
        L{ProcessHandle}, L{ThreadHandle}, L{FileHandle}, L{SnapshotHandle}
    """

    # XXX DEBUG
    # When this private flag is True each Handle will print a message to
    # standard output when it's created and destroyed. This is useful for
    # detecting handle leaks within WinAppDbg itself.
    __b_leak_detection = False

    def __init__(self, a_handle=None, b_ownership=True):
        """
        @type  a_handle: int
        @param a_handle: Win32 handle value.
        @type  b_ownership: bool
        @param b_ownership:
           C{True} if we own the handle and we need to close it.
           C{False} if someone else will be calling L{CloseHandle}.
        """
        super(Handle, self).__init__()
        self._value = self._normalize(a_handle)
        self.b_ownership = b_ownership
        if Handle.__b_leak_detection:  # XXX DEBUG
            print('INIT HANDLE ({0!r}) {1!r}'.format(self.value, self))

    @property
    def value(self):
        """
        value getter
        """
        return self._value

    def __del__(self):
        """
        Closes the Win32 handle when the Python object is destroyed.
        """
        try:
            if Handle.__b_leak_detection:  # XXX DEBUG
                print('DEL HANDLE {0!r}'.format(self))
            self.close()
        except Exception:
            pass

    def __enter__(self):
        """
        Compatibility with the "C{with}" Python statement.
        """
        if Handle.__b_leak_detection:  # XXX DEBUG
            print('ENTER HANDLE {0!r}'.format(self))
        return self

    def __exit__(self, t_type, value, traceback):
        """
        Compatibility with the "C{with}" Python statement.
        """
        if Handle.__b_leak_detection:  # XXX DEBUG
            print('EXIT HANDLE {0!r}'.format(self))
        try:
            self.close()
        except Exception:
            pass

    def __copy__(self):
        """
        Duplicates the Win32 handle when copying the Python object.
        @rtype:  L{Handle}
        @return: A new handle to the same Win32 object.
        """
        return self.dup()

    def __deepcopy__(self, memo):
        """
        Duplicates the Win32 handle when copying the Python object.
        @rtype:  L{Handle}
        @return: A new handle to the same win32 object.
        """
        return self.dup()

    @property
    def _as_parameter_(self):
        """
        Compatibility with ctypes.
        Allows passing transparently a Handle object to an API call.
        """
        return HANDLE(self.value)

    @staticmethod
    def from_param(value):
        """
        Compatibility with ctypes.
        Allows passing transparently a Handle object to an API call.
        @type  value: int
        @param value: Numeric handle value.
        """
        return HANDLE(value)

    def close(self):
        """
        Closes the Win32 handle.
        """
        if self.b_ownership and self.value not in (None, INVALID_HANDLE_VALUE):
            if Handle.__b_leak_detection:     # XXX DEBUG
                print('CLOSE HANDLE ({0:d}) {1:r}'.format(self.value, self))
            try:
                self._close()
            finally:
                self._value = None

    def _close(self):
        """
        Low-level close method.
        This is a private method, do not call it.
        """
        close_handle(self.value)

    def dup(self):
        """
        @rtype:  L{Handle}
        @return: A new handle to the same Win32 object.
        """
        if self.value is None:
            raise ValueError("Closed handles can't be duplicated!")
        new_handle = duplicate_handle(self.value)
        # XXX DEBUG
        if Handle.__b_leak_detection:
            print(
                'DUP HANDLE ({0:d} -> {1:d}) {2!r} {3!r}'.format(
                    self.value, new_handle.value, self, new_handle
                )
            )
        return new_handle

    @staticmethod
    def _normalize(value):
        """
        Normalize handle values.
        """
        if hasattr(value, 'value'):
            value = value.value
        if value is not None:
            value = int(value)
        return value

    def wait(self, dw_milliseconds=None):
        """
        Wait for the Win32 object to be signaled.
        @type  dwMilliseconds: int
        @param dwMilliseconds: (Optional) Timeout value in milliseconds.
            Use C{INFINITE} or C{None} for no timeout.
        """
        if self.value is None:
            raise ValueError('Handle is already closed!')
        if dw_milliseconds is None:
            dw_milliseconds = INFINITE
        result = wait_for_single_object(self.value, dw_milliseconds)
        if result != WAIT_OBJECT_0:
            raise ctypes.WinError(result)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.value)

    def __get_inherit(self):
        if self.value is None:
            raise ValueError('Handle is already closed!')
        return bool(get_handle_information(self.value) & HANDLE_FLAG_INHERIT)

    def __set_inherit(self, value):
        if self.value is None:
            raise ValueError('Handle is already closed!')
        flag = (0, HANDLE_FLAG_INHERIT)[bool(value)]
        set_handle_information(self.value, flag, flag)

    inherit = property(__get_inherit, __set_inherit)

    def __get_protect_from_close(self):
        if self.value is None:
            raise ValueError('Handle is already closed!')
        return bool(
            get_handle_information(self.value) & HANDLE_FLAG_PROTECT_FROM_CLOSE
        )

    def __set_protect_from_close(self, value):
        if self.value is None:
            raise ValueError('Handle is already closed!')
        flag = (0, HANDLE_FLAG_PROTECT_FROM_CLOSE)[bool(value)]
        set_handle_information(self.value, flag, flag)

    protect_from_close = property(
        __get_protect_from_close, __set_protect_from_close
    )

class ProcessHandle(Handle):
    """
    Win32 process handle.
    @type dw_access: int
    @ivar dw_access: Current access flags to this handle.
            This is the same value passed to L{OpenProcess}.
            Can only be C{None} if C{a_handle} is also C{None}.
            Defaults to L{PROCESS_ALL_ACCESS}.
    @see: L{Handle}
    """

    def __init__(
            self, a_handle=None, b_ownership=True, dw_access=PROCESS_ALL_ACCESS
    ):
        """
        @type  a_handle: int
        @param a_handle: Win32 handle value.
        @type  b_ownership: bool
        @param b_ownership:
           C{True} if we own the handle and we need to close it.
           C{False} if someone else will be calling L{CloseHandle}.
        @type  dw_access: int
        @param dw_access: Current access flags to this handle.
            This is the same value passed to L{OpenProcess}.
            Can only be C{None} if C{a_handle} is also C{None}.
            Defaults to L{PROCESS_ALL_ACCESS}.
        """
        super(ProcessHandle, self).__init__(a_handle, b_ownership)
        self.dw_access = dw_access
        if a_handle is not None and dw_access is None:
            msg = 'Missing access flags for process handle: {0:x}'.format(
                a_handle
            )
            raise TypeError(msg)

    def get_pid(self):
        """
        @rtype:  int
        @return: Process global ID.
        """
        return get_process_id(self.value)

# XXX maybe add functions related to the toolhelp snapshots here?
class SnapshotHandle(Handle):
    """
    Toolhelp32 snapshot handle.
    @see: L{Handle}
    """

# pylint: disable=too-many-arguments
def duplicate_handle(
        h_source_handle, h_source_process_handle=None,
        h_target_process_handle=None, dw_desired_access=STANDARD_RIGHTS_ALL,
        b_inherit_handle=False, dw_options=DUPLICATE_SAME_ACCESS
):
    """
    BOOL WINAPI DuplicateHandle(
        __in   HANDLE hSourceProcessHandle,
        __in   HANDLE hSourceHandle,
        __in   HANDLE hTargetProcessHandle,
        __out  LPHANDLE lpTargetHandle,
        __in   DWORD dwDesiredAccess,
        __in   BOOL bInheritHandle,
        __in   DWORD dwOptions
    ;
    """

    _duplicate_handle = WINDLL.kernel32.DuplicateHandle
    _duplicate_handle.argtypes = [
        HANDLE, HANDLE, HANDLE, LPHANDLE, DWORD, BOOL, DWORD
    ]
    _duplicate_handle.restype = bool
    _duplicate_handle.errcheck = raise_if_zero

    # NOTE: the arguments to this function are in a different order,
    # so we can set default values for all of them but one (hSourceHandle).

    if h_source_process_handle is None:
        h_source_process_handle = get_current_process()
    if h_target_process_handle is None:
        h_target_process_handle = h_source_process_handle
    lp_target_handle = HANDLE(INVALID_HANDLE_VALUE)
    _duplicate_handle(
        h_source_process_handle, h_source_handle, h_target_process_handle,
        BY_REF(lp_target_handle), dw_desired_access, bool(b_inherit_handle),
        dw_options
    )
    if isinstance(h_source_handle, Handle):
        handle_class = h_source_handle.__class__
    else:
        handle_class = Handle
    if hasattr(h_source_handle, 'dw_access'):
        return handle_class(
            lp_target_handle.value, dw_access=h_source_handle.dw_access
        )
    else:
        return handle_class(lp_target_handle.value)

def close_handle(h_handle):
    """
    BOOL WINAPI CloseHandle(
        __in  HANDLE hObject
    );
    """
    if isinstance(h_handle, Handle):
        # Prevents the handle from being closed without notifying
        # the Handle object.
        h_handle.close()
    else:
        _close_handle = WINDLL.kernel32.CloseHandle
        _close_handle.argtypes = [HANDLE]
        _close_handle.restype = bool
        _close_handle.errcheck = raise_if_zero
        _close_handle(h_handle)

# --- Toolhelp library defines and structures ---------------------------------

TH32CS_SNAPHEAPLIST = 0x00000001
TH32CS_SNAPPROCESS = 0x00000002
TH32CS_SNAPTHREAD = 0x00000004
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPALL = (
    TH32CS_SNAPHEAPLIST | TH32CS_SNAPPROCESS
    | TH32CS_SNAPTHREAD | TH32CS_SNAPMODULE
)

# pylint: disable=too-few-public-methods
class MODULEENTRY32(Structure):
    """
    typedef struct tagMODULEENTRY32 {
        DWORD   dwSize;
        DWORD   th32ModuleID;
        DWORD   th32ProcessID;
        DWORD   GlblcntUsage;
        DWORD   ProccntUsage;
        BYTE    *modBaseAddr;
        DWORD   modBaseSize;
        HMODULE hModule;
        char    szModule[MAX_MODULE_NAME32 + 1];
        char    szExePath[MAX_PATH];
    } MODULEENTRY32;
    """

    _fields_ = [
        ("dw_size", DWORD),
        ("th_32_module_id", DWORD),
        ("th_32_process_id", DWORD),
        ("glbl_cnt_usage", DWORD),
        ("proc_cnt_usage", DWORD),
        ("mod_base_addr", LPVOID),  # BYTE*
        ("mod_base_size", DWORD),
        ("h_module", HMODULE),
        ("sz_module", TCHAR * (MAX_MODULE_NAME32 + 1)),
        ("sz_exe_path", TCHAR * MAX_PATH),
    ]
    def __init__(self, *args, **kwds):
        super(MODULEENTRY32, self).__init__(*args, **kwds)
        self.dw_size = SIZE_OF(self)

LPMODULEENTRY32 = POINTER(MODULEENTRY32)

#--- kernel32.dll -------------------------------------------------------------

def get_last_error():
    """
    DWORD WINAPI GetLastError(void);
    """
    _get_last_error = WINDLL.kernel32.GetLastError
    _get_last_error.argtypes = []
    _get_last_error.restype = DWORD
    return _get_last_error()

def set_last_error(dw_err_code):
    """
    void WINAPI SetLastError(
        __in  DWORD dwErrCode
    );
    """
    _set_last_error = WINDLL.kernel32.SetLastError
    _set_last_error.argtypes = [DWORD]
    _set_last_error.restype = None
    _set_last_error(dw_err_code)

# -----------------------------------------------------------------------------
# Debug API

def read_process_memory(h_process, lp_base_address, n_size):
    """
    BOOL WINAPI ReadProcessMemory(
        __in   HANDLE hProcess,
        __in   LPCVOID lpBaseAddress,
        __out  LPVOID lpBuffer,
        __in   SIZE_T nSize,
        __out  SIZE_T* lpNumberOfBytesRead
    );
    """

    _read_process_memory = WINDLL.kernel32.ReadProcessMemory
    _read_process_memory.argtypes = [
        HANDLE, LPVOID, LPVOID, SIZE_T, POINTER(SIZE_T)
    ]
    _read_process_memory.restype = bool

    lp_buffer = ctypes.create_string_buffer(b'', n_size)
    lp_number_of_bytes_read = SIZE_T(0)
    success = _read_process_memory(
        h_process, lp_base_address, lp_buffer,
        n_size, BY_REF(lp_number_of_bytes_read)
    )
    if not success and get_last_error() != ERROR_PARTIAL_COPY:
        raise ctypes.WinError()
    return bytes(lp_buffer.raw)[:lp_number_of_bytes_read.value]

def write_process_memory(h_process, lp_base_address, lp_buffer):
    """
    BOOL WINAPI WriteProcessMemory(
        __in   HANDLE hProcess,
        __in   LPCVOID lpBaseAddress,
        __in   LPVOID lpBuffer,
        __in   SIZE_T nSize,
        __out  SIZE_T* lpNumberOfBytesWritten
    );
    """
    _write_process_memory = WINDLL.kernel32.WriteProcessMemory
    _write_process_memory.argtypes = [
        HANDLE, LPVOID, LPVOID, SIZE_T, POINTER(SIZE_T)
    ]
    _write_process_memory.restype = bool

    n_size = len(lp_buffer)
    lp_buffer = ctypes.create_string_buffer(lp_buffer)
    lp_number_of_bytes_written = SIZE_T(0)
    success = _write_process_memory(
        h_process, lp_base_address, lp_buffer, n_size,
        BY_REF(lp_number_of_bytes_written)
    )
    if not success and get_last_error() != ERROR_PARTIAL_COPY:
        raise ctypes.WinError()
    return lp_number_of_bytes_written.value

# -----------------------------------------------------------------------------
# Process API

def get_process_id(h_process):
    """
    DWORD WINAPI GetProcessId(
        __in  HANDLE hProcess
    );
    """
    _get_process_id = WINDLL.kernel32.GetProcessId
    _get_process_id.argtypes = [HANDLE]
    _get_process_id.restype = DWORD
    _get_process_id.errcheck = raise_if_zero
    return _get_process_id(h_process)

def open_process(dw_desired_access, b_inherit_handle, dw_process_id):
    """
    HANDLE WINAPI OpenProcess(
        __in  DWORD dwDesiredAccess,
        __in  BOOL bInheritHandle,
        __in  DWORD dwProcessId
    """

    _open_process = WINDLL.kernel32.OpenProcess
    _open_process.argtypes = [DWORD, BOOL, DWORD]
    _open_process.restype = HANDLE

    h_process = _open_process(
        dw_desired_access, bool(b_inherit_handle), dw_process_id
    )
    if h_process == NULL:
        raise ctypes.WinError()
    return ProcessHandle(h_process, dw_access=dw_desired_access)

# -----------------------------------------------------------------------------
# File API and related

def get_handle_information(h_object):
    """
    BOOL WINAPI GetHandleInformation(
        __in   HANDLE hObject,
        __out  LPDWORD lpdwFlags
    );
    """
    _get_handle_information = WINDLL.kernel32.get_handle_information
    _get_handle_information.argtypes = [HANDLE, PDWORD]
    _get_handle_information.restype = bool
    _get_handle_information.errcheck = raise_if_zero

    dw_flags = DWORD(0)
    _get_handle_information(h_object, BY_REF(dw_flags))
    return dw_flags.value

def set_handle_information(h_object, dw_mask, dw_flags):
    """
    BOOL WINAPI SetHandleInformation(
        __in  HANDLE hObject,
        __in  DWORD dwMask,
        __in  DWORD dwFlags
    );
    """
    _set_handle_information = WINDLL.kernel32.SetHandleInformation
    _set_handle_information.argtypes = [HANDLE, DWORD, DWORD]
    _set_handle_information.restype = bool
    _set_handle_information.errcheck = raise_if_zero
    _set_handle_information(h_object, dw_mask, dw_flags)

# -----------------------------------------------------------------------------
# Synchronization API

# XXX NOTE
#
# Instead of waiting forever, we wait for a small period of time and loop.
# This is a workaround for an unwanted behavior of psyco-accelerated code:
# you can't interrupt a blocking call using Ctrl+C, because signal processing
# is only done between C calls.
#
# Also see: bug #2793618 in Psyco project
# https://sourceforge.net/p/psyco/bugs/80/

def wait_for_single_object(h_handle, dw_milliseconds=INFINITE):
    """
    DWORD WINAPI WaitForSingleObject(
        HANDLE hHandle,
        DWORD  dwMilliseconds
    );
    """
    _wait_for_single_object = WINDLL.kernel32.WaitForSingleObject
    _wait_for_single_object.argtypes = [HANDLE, DWORD]
    _wait_for_single_object.restype = DWORD

    if not dw_milliseconds and dw_milliseconds != 0:
        dw_milliseconds = INFINITE
    if dw_milliseconds != INFINITE:
        result = _wait_for_single_object(h_handle, dw_milliseconds)
        if result == WAIT_FAILED:
            raise ctypes.WinError()
    else:
        while 1:
            result = _wait_for_single_object(h_handle, 100)
            if result == WAIT_FAILED:
                raise ctypes.WinError()
            if result != WAIT_TIMEOUT:
                break
    return result

# -----------------------------------------------------------------------------
# Toolhelp32 API

def create_tool_help32snapshot(dw_flags=TH32CS_SNAPALL, th_32_process_id=0):
    """
    HANDLE WINAPI CreateToolhelp32Snapshot(
        __in  DWORD dwFlags,
        __in  DWORD th32ProcessID
    );
    """
    _create_tool_help32snapshot = WINDLL.kernel32.CreateToolhelp32Snapshot
    _create_tool_help32snapshot.argtypes = [DWORD, DWORD]
    _create_tool_help32snapshot.restype = HANDLE

    h_snapshot = _create_tool_help32snapshot(dw_flags, th_32_process_id)
    if h_snapshot == INVALID_HANDLE_VALUE:
        raise ctypes.WinError()
    return SnapshotHandle(h_snapshot)

def module32first(h_snapshot):
    """
    BOOL WINAPI Module32First(
        __in     HANDLE hSnapshot,
        __inout  LPMODULEENTRY32 lpme
    );
    """
    _module32first = WINDLL.kernel32.Module32First
    _module32first.argtypes = [HANDLE, LPMODULEENTRY32]
    _module32first.restype = bool

    me32 = MODULEENTRY32()
    success = _module32first(h_snapshot, BY_REF(me32))
    if not success:
        if get_last_error() == ERROR_NO_MORE_FILES:
            return None
        raise ctypes.WinError()
    return me32

def module32next(h_snapshot, me32=None):
    """
    BOOL WINAPI Module32Next(
        __in   HANDLE hSnapshot,
        __out  LPMODULEENTRY32 lpme
    );
    """
    _module32next = WINDLL.kernel32.Module32Next
    _module32next.argtypes = [HANDLE, LPMODULEENTRY32]
    _module32next.restype = bool

    if me32 is None:
        me32 = MODULEENTRY32()
    success = _module32next(h_snapshot, BY_REF(me32))
    if not success:
        if get_last_error() == ERROR_NO_MORE_FILES:
            return None
        raise ctypes.WinError()
    return me32

#==============================================================================
# This calculates the list of exported symbols.
_ALL = set(vars().keys()).difference(_ALL)
__all__ = [_x for _x in _ALL if not _x.startswith('_')]
__all__.sort()
#==============================================================================
