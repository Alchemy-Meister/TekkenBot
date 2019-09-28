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
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_QUERY_INFORMATION = 0x0400

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

# Memory access
PAGE_NOACCESS = 0x01
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08
PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_GUARD = 0x100
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
MEM_RELEASE = 0x8000
MEM_FREE = 0x10000
MEM_PRIVATE = 0x20000
MEM_MAPPED = 0x40000
SEC_IMAGE = 0x1000000
MEM_IMAGE = SEC_IMAGE

# DuplicateHandle constants
DUPLICATE_SAME_ACCESS = 0x00000002

# GetHandleInformation / SetHandleInformation
HANDLE_FLAG_INHERIT = 0x00000001
HANDLE_FLAG_PROTECT_FROM_CLOSE = 0x00000002

# RegisterWaitForSingleObject
WT_EXECUTEDEFAULT = 0x00000000
WT_EXECUTEONLYONCE = 0x00000008

# --- Handle wrappers ---------------------------------------------------------

class Handle:
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

class ThreadHandle(Handle):
    """
    Win32 thread handle.
    @type dwAccess: int
    @ivar dwAccess: Current access flags to this handle.
            This is the same value passed to L{OpenThread}.
            Can only be C{None} if C{aHandle} is also C{None}.
            Defaults to L{THREAD_ALL_ACCESS}.
    @see: L{Handle}
    """

    def __init__(
            self, a_handle=None, b_ownership=True, dw_access=THREAD_ALL_ACCESS
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
            This is the same value passed to L{OpenThread}.
            Can only be C{None} if C{a_handle} is also C{None}.
            Defaults to L{THREAD_ALL_ACCESS}.
        """
        super(ThreadHandle, self).__init__(a_handle, b_ownership)
        self.dw_access = dw_access
        if a_handle is not None and dw_access is None:
            msg = "Missing access flags for thread handle: %x" % a_handle
            raise TypeError(msg)

    def get_tid(self):
        """
        @rtype:  int
        @return: Thread global ID.
        """
        return get_thread_id(self.value)

# XXX maybe add functions related to the toolhelp snapshots here?
class SnapshotHandle(Handle):
    """
    Toolhelp32 snapshot handle.
    @see: L{Handle}
    """

# --- Structure wrappers ------------------------------------------------------

# Don't psyco-optimize this class because it needs to be serialized.
class MemoryBasicInformation:
    """
    Memory information object returned by L{VirtualQueryEx}.
    """
    READABLE = (
        PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY
        | PAGE_READONLY | PAGE_READWRITE | PAGE_WRITECOPY
    )
    WRITEABLE = (
        PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY | PAGE_READWRITE
        | PAGE_WRITECOPY
    )
    COPY_ON_WRITE = PAGE_EXECUTE_WRITECOPY | PAGE_WRITECOPY
    EXECUTABLE = (
        PAGE_EXECUTE | PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE
        | PAGE_EXECUTE_WRITECOPY
    )
    EXECUTABLE_AND_WRITEABLE = PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY

    def __init__(self, mbi=None):
        """
        @type  mbi: L{MEMORY_BASIC_INFORMATION} or L{MemoryBasicInformation}
        @param mbi: Either a L{MEMORY_BASIC_INFORMATION} structure or another
            L{MemoryBasicInformation} instance.
        """
        if mbi is None:
            self.base_address = None
            self.allocation_base = None
            self.allocation_protect = None
            self.region_size = None
            self.state = None
            self.protect = None
            self.type = None
        else:
            self.base_address = mbi.base_address
            self.allocation_base = mbi.allocation_base
            self.allocation_protect = mbi.allocation_protect
            self.region_size = mbi.region_size
            self.state = mbi.state
            self.protect = mbi.protect
            self.type = mbi.type

            # Only used when copying MemoryBasicInformation objects, instead of
            # instancing them from a MEMORY_BASIC_INFORMATION structure.
            if hasattr(mbi, 'content'):
                self.content = mbi.content
            if hasattr(mbi, 'filename'):
                self.content = mbi.filename

    def __contains__(self, address):
        """
        Test if the given memory address falls within this memory region.
        @type  address: int
        @param address: Memory address to test.
        @rtype:  bool
        @return: C{True} if the given memory address falls within this memory
            region, C{False} otherwise.
        """
        return (
            self.base_address <= address < self.base_address + self.region_size
        )

    def is_free(self):
        """
        @rtype:  bool
        @return: C{True} if the memory in this region is free.
        """
        return self.state == MEM_FREE

    def is_reserved(self):
        """
        @rtype:  bool
        @return: C{True} if the memory in this region is reserved.
        """
        return self.state == MEM_RESERVE

    def is_commited(self):
        """
        @rtype:  bool
        @return: C{True} if the memory in this region is commited.
        """
        return self.state == MEM_COMMIT

    def is_image(self):
        """
        @rtype:  bool
        @return: C{True} if the memory in this region belongs to an executable
            image.
        """
        return self.type == MEM_IMAGE

    def is_mapped(self):
        """
        @rtype:  bool
        @return: C{True} if the memory in this region belongs to a mapped file.
        """
        return self.type == MEM_MAPPED

    def is_private(self):
        """
        @rtype:  bool
        @return: C{True} if the memory in this region is private.
        """
        return self.type == MEM_PRIVATE

    def is_guard(self):
        """
        @rtype:  bool
        @return: C{True} if all pages in this region are guard pages.
        """
        return self.is_commited() and bool(self.protect & PAGE_GUARD)

    def has_content(self):
        """
        @rtype:  bool
        @return: C{True} if the memory in this region has any data in it.
        """
        return (
            self.is_commited()
            and not bool(self.protect & (PAGE_GUARD | PAGE_NOACCESS))
        )

    def is_readable(self):
        """
        @rtype:  bool
        @return: C{True} if all pages in this region are readable.
        """
        return self.has_content() and bool(self.protect & self.READABLE)

    def is_writeable(self):
        """
        @rtype:  bool
        @return: C{True} if all pages in this region are writeable.
        """
        return self.has_content() and bool(self.protect & self.WRITEABLE)

    def is_copy_on_write(self):
        """
        @rtype:  bool
        @return: C{True} if all pages in this region are marked as
            copy-on-write. This means the pages are writeable, but changes
            are not propagated to disk.
        @note:
            Typically data sections in executable images are marked like this.
        """
        return self.has_content() and bool(self.protect & self.COPY_ON_WRITE)

    def is_executable(self):
        """
        @rtype:  bool
        @return: C{True} if all pages in this region are executable.
        @note: Executable pages are always readable.
        """
        return self.has_content() and bool(self.protect & self.EXECUTABLE)

    def is_executable_and_writeable(self):
        """
        @rtype:  bool
        @return: C{True} if all pages in this region are executable and
            writeable.
        @note: The presence of such pages make memory corruption
            vulnerabilities much easier to exploit.
        """
        return (
            self.has_content()
            and bool(self.protect & self.EXECUTABLE_AND_WRITEABLE)
        )

#--- SECURITY_ATTRIBUTES structure --------------------------------------------

class SECURITY_ATTRIBUTES(Structure):
    """
    typedef struct _SECURITY_ATTRIBUTES {
        DWORD nLength;
        LPVOID lpSecurityDescriptor;
        BOOL bInheritHandle;
    } SECURITY_ATTRIBUTES, *PSECURITY_ATTRIBUTES, *LPSECURITY_ATTRIBUTES;
    """
    _fields_ = [
        ('n_length', DWORD),
        ('lp_security_descriptor', LPVOID),
        ('b_inherit_handle', BOOL),
    ]
LPSECURITY_ATTRIBUTES = POINTER(SECURITY_ATTRIBUTES)

# --- MEMORY_BASIC_INFORMATION structure --------------------------------------

# pylint: disable=too-few-public-methods
class MemoryBasicInformationStruc(Structure):
    """
    typedef struct _MEMORY_BASIC_INFORMATION {
        PVOID BaseAddress;
        PVOID AllocationBase;
        DWORD AllocationProtect;
        SIZE_T RegionSize;
        DWORD State;
        DWORD Protect;
        DWORD Type;
    } MEMORY_BASIC_INFORMATION, *PMEMORY_BASIC_INFORMATION;
    """
    _fields_ = [
        ('base_address', SIZE_T),    # remote pointer
        ('allocation_base', SIZE_T),    # remote pointer
        ('allocation_protect', DWORD),
        ('region_size', SIZE_T),
        ('state', DWORD),
        ('protect', DWORD),
        ('type', DWORD),
    ]
PMEMORY_BASIC_INFORMATION = POINTER(MemoryBasicInformationStruc)

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
        ('dw_size', DWORD),
        ('th_32_module_id', DWORD),
        ('th_32_process_id', DWORD),
        ('glbl_cnt_usage', DWORD),
        ('proc_cnt_usage', DWORD),
        ('mod_base_addr', LPVOID),  # BYTE*
        ('mod_base_size', DWORD),
        ('h_module', HMODULE),
        ('sz_module', TCHAR * (MAX_MODULE_NAME32 + 1)),
        ('sz_exe_path', TCHAR * MAX_PATH),
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

# -----------------------------------------------------------------------------
# DLL API

# HMODULE WINAPI LoadLibrary(
#   __in  LPCTSTR lpFileName
# );
def __load_library_function(function, lp_file_name):
    h_module = function(lp_file_name)
    if h_module == NULL:
        raise ctypes.WinError()
    return h_module

def load_library_a(lp_file_name):
    _load_library_a = WINDLL.kernel32.LoadLibraryA
    _load_library_a.argtypes = [LPSTR]
    _load_library_a.restype = HMODULE

    return __load_library_function(_load_library_a, lp_file_name)

def load_library_w(lp_file_name):
    _load_library_w = WINDLL.kernel32.LoadLibraryW
    _load_library_w.argtypes = [LPWSTR]
    _load_library_w.restype = HMODULE

    return __load_library_function(_load_library_w, lp_file_name)

def load_library(lp_file_name):
    return GuessStringType(load_library_a, load_library_w)(lp_file_name)

def __get_module_handle__function(function, lp_module_name):
    h_module = function(lp_module_name)
    if h_module == NULL:
        raise ctypes.WinError()
    return h_module

def get_module_handle_a(lp_module_name):
    """
    HMODULE WINAPI GetModuleHandleA(
        __in_opt  LPCSTR lpModuleName
    );
    """
    _get_module_handle_a = WINDLL.kernel32.GetModuleHandleA
    _get_module_handle_a.argtypes = [LPSTR]
    _get_module_handle_a.restype = HMODULE

    return __get_module_handle__function(_get_module_handle_a, lp_module_name)

def get_module_handle_w(lp_module_name):
    """
    HMODULE WINAPI GetModuleHandleW(
        __in_opt  LPCWSTR lpModuleName
    );
    """
    _get_module_handle_w = WINDLL.kernel32.GetModuleHandleW
    _get_module_handle_w.argtypes = [LPWSTR]
    _get_module_handle_w.restype = HMODULE

    return __get_module_handle__function(_get_module_handle_w, lp_module_name)

def get_module_handle(lp_module_name):
    return GuessStringType(get_module_handle_a, get_module_handle_w)(
        lp_module_name
    )

def get_proc_address_a(h_module, lp_proc_name):
    """
    FARPROC WINAPI GetProcAddressA(
        __in  HMODULE hModule,
        __in  LPSTR lpProcName
    );
    """
    _get_proc_address = WINDLL.kernel32.GetProcAddress
    _get_proc_address.argtypes = [HMODULE, LPVOID]
    _get_proc_address.restype = LPVOID

    if isinstance(lp_proc_name, int):
        lp_proc_name = LPVOID(lp_proc_name)
        if lp_proc_name.value & (~0xFFFF):
            raise ValueError(
                'ordinal number too large: %d' % lp_proc_name.value
            )
    elif isinstance(lp_proc_name, bytes):
        lp_proc_name = ctypes.c_char_p(lp_proc_name)
    else:
        raise TypeError(str(type(lp_proc_name)))
    return _get_proc_address(h_module, lp_proc_name)

def get_proc_address_w(h_module, lp_proc_name):
    return make_wide_version(get_proc_address_a)(h_module, lp_proc_name)

def get_proc_address(h_module, lp_proc_name):
    return GuessStringType(get_proc_address_a, get_proc_address_w)(
        h_module, lp_proc_name
    )

def free_library(h_module):
    """
    BOOL WINAPI FreeLibrary(
        __in  HMODULE hModule
    );
    """
    _free_library = WINDLL.kernel32.FreeLibrary
    _free_library.argtypes = [HMODULE]
    _free_library.restype = bool
    _free_library.errcheck = raise_if_zero
    _free_library(h_module)

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

def write_process_memory(h_process, lp_base_address, lp_buffer, n_size=None):
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

    if n_size is None:
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

def virtual_alloc_ex(
        h_process,
        lp_address=0,
        dw_size=0x1000,
        fl_allocation_type=MEM_COMMIT | MEM_RESERVE,
        fl_protect=PAGE_EXECUTE_READWRITE
):
    """
    LPVOID WINAPI VirtualAllocEx(
        __in      HANDLE hProcess,
        __in_opt  LPVOID lpAddress,
        __in      SIZE_T dwSize,
        __in      DWORD flAllocationType,
        __in      DWORD flProtect
    );
    """
    _virtual_alloc_ex = WINDLL.kernel32.VirtualAllocEx
    _virtual_alloc_ex.argtypes = [HANDLE, LPVOID, SIZE_T, DWORD, DWORD]
    _virtual_alloc_ex.restype = LPVOID

    lp_address = _virtual_alloc_ex(
        h_process, lp_address, dw_size, fl_allocation_type, fl_protect
    )
    if lp_address == NULL:
        raise ctypes.WinError()
    return lp_address

def virtual_query_ex(h_process, lp_address):
    """
    SIZE_T WINAPI VirtualQueryEx(
        __in      HANDLE hProcess,
        __in_opt  LPCVOID lpAddress,
        __out     PMEMORY_BASIC_INFORMATION lpBuffer,
        __in      SIZE_T dwLength
    );
    """
    _virtual_query_ex = WINDLL.kernel32.VirtualQueryEx
    _virtual_query_ex.argtypes = [
        HANDLE, LPVOID, PMEMORY_BASIC_INFORMATION, SIZE_T
    ]
    _virtual_query_ex.restype = SIZE_T

    lp_buffer = MemoryBasicInformationStruc()
    dw_length = SIZE_OF(MemoryBasicInformationStruc)
    success = _virtual_query_ex(
        h_process, lp_address, BY_REF(lp_buffer), dw_length
    )
    if success == 0:
        raise ctypes.WinError()
    return MemoryBasicInformation(lp_buffer)

def virtual_protect_ex(
        h_process, lp_address, dw_size, fl_new_protect=PAGE_EXECUTE_READWRITE
):
    """
    BOOL WINAPI VirtualProtectEx(
        __in   HANDLE hProcess,
        __in   LPVOID lpAddress,
        __in   SIZE_T dwSize,
        __in   DWORD flNewProtect,
        __out  PDWORD lpflOldProtect
    );
    """
    _virtual_protect_ex = WINDLL.kernel32.VirtualProtectEx
    _virtual_protect_ex.argtypes = [HANDLE, LPVOID, SIZE_T, DWORD, PDWORD]
    _virtual_protect_ex.restype = bool
    _virtual_protect_ex.errcheck = raise_if_zero

    fl_old_protect = DWORD(0)
    _virtual_protect_ex(
        h_process, lp_address, dw_size, fl_new_protect, BY_REF(fl_old_protect)
    )
    return fl_old_protect.value

def virtual_free_ex(h_process, lp_address, dw_size=0, dw_free_type=MEM_RELEASE):
    """
    BOOL WINAPI VirtualFreeEx(
        __in  HANDLE hProcess,
        __in  LPVOID lpAddress,
        __in  SIZE_T dwSize,
        __in  DWORD dwFreeType
    );
    """
    _virtual_free_ex = WINDLL.kernel32.VirtualFreeEx
    _virtual_free_ex.argtypes = [HANDLE, LPVOID, SIZE_T, DWORD]
    _virtual_free_ex.restype = bool
    _virtual_free_ex.errcheck = raise_if_zero
    _virtual_free_ex(h_process, lp_address, dw_size, dw_free_type)

def create_remote_thread(
        h_process,
        lp_start_address,
        lp_parameter,
        lp_thread_attributes=None,
        dw_stack_size=0,
        dw_creation_flags=0,
):
    """
    HANDLE WINAPI CreateRemoteThread(
        __in   HANDLE hProcess,
        __in   LPSECURITY_ATTRIBUTES lpThreadAttributes,
        __in   SIZE_T dwStackSize,
        __in   LPTHREAD_START_ROUTINE lpStartAddress,
        __in   LPVOID lpParameter,
        __in   DWORD dwCreationFlags,
        __out  LPDWORD lpThreadId
    );
    """
    _create_remote_thread = WINDLL.kernel32.CreateRemoteThread
    _create_remote_thread.argtypes = [
        HANDLE, LPSECURITY_ATTRIBUTES, SIZE_T, LPVOID, LPVOID, DWORD, LPDWORD
    ]
    _create_remote_thread.restype = HANDLE

    if lp_thread_attributes:
        lp_thread_attributes = BY_REF(lp_thread_attributes)
    dw_thread_id = DWORD(0)
    h_thread = _create_remote_thread(
        h_process,
        lp_thread_attributes,
        dw_stack_size,
        lp_start_address,
        lp_parameter,
        dw_creation_flags,
        BY_REF(dw_thread_id)
    )
    if not h_thread:
        raise ctypes.WinError()
    return ThreadHandle(h_thread), dw_thread_id.value

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
    if h_process is NULL:
        raise ctypes.WinError()
    return ProcessHandle(h_process, dw_access=dw_desired_access)

def get_thread_id(h_thread):
    """
    DWORD WINAPI GetThreadId(
        __in  HANDLE hThread
    );
    """
    _get_thread_id = WINDLL.kernel32.GetThreadId
    _get_thread_id.argtypes = [HANDLE]
    _get_thread_id.restype = DWORD

    dw_thread_id = _get_thread_id(h_thread)
    if dw_thread_id == 0:
        raise ctypes.WinError()
    return dw_thread_id

def get_exit_code_thread(h_thread):
    """
    # BOOL WINAPI GetExitCodeThread(
        __in   HANDLE hThread,
        __out  LPDWORD lpExitCode
    );
    """
    _get_exit_code_thread = WINDLL.kernel32.GetExitCodeThread
    _get_exit_code_thread.argtypes = [HANDLE, PDWORD]
    _get_exit_code_thread.restype = bool
    _get_exit_code_thread.errcheck = raise_if_zero

    lp_exit_code = DWORD(0)
    _get_exit_code_thread(h_thread, BY_REF(lp_exit_code))
    return lp_exit_code.value

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

WAIT_OR_TIMER_CALLBACK = ctypes.WINFUNCTYPE(
    None, PVOID, BOOL
)

def wait_or_timer_callback(callback):
    return WAIT_OR_TIMER_CALLBACK(callback)

def register_wait_for_single_object(
        h_object, callback, context, dw_milliseconds=INFINITE,
        dw_flags=WT_EXECUTEDEFAULT
):
    """
    BOOL RegisterWaitForSingleObject(
        PHANDLE phNewWaitObject,
        HANDLE hObject,
        WAITORTIMERCALLBACK Callback,
        PVOID Context,
        ULONG dwMilliseconds,
        ULONG dwFlags
    );
    """

    _register_wait_for_single_object = (
        WINDLL.kernel32.RegisterWaitForSingleObject
    )
    _register_wait_for_single_object.argtypes = [
        PHANDLE, HANDLE, WAIT_OR_TIMER_CALLBACK, PVOID, ULONG, ULONG
    ]
    _register_wait_for_single_object.restype = bool

    ph_new_wait_object = HANDLE()
    result = _register_wait_for_single_object(
        BY_REF(ph_new_wait_object),
        h_object,
        callback,
        context,
        dw_milliseconds,
        dw_flags
    )
    if not result:
        raise ctypes.WinError()
    return ph_new_wait_object

def unregister_wait(wait_handle):
    """
    BOOL UnregisterWait(
        HANDLE WaitHandle
    );
    """

    _unregister_wait = WINDLL.kernel32.UnregisterWait
    _unregister_wait.argtypes = [HANDLE]
    _unregister_wait.restype = bool

    result = _unregister_wait(wait_handle)
    if not result and get_last_error() != ERROR_IO_PENDING:
        raise ctypes.WinError()

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

def query_performance_counter():
    """
    BOOL QueryPerformanceCounter(
        LARGE_INTEGER *lpPerformanceCount
    );
    """
    _query_performance_counter = WINDLL.kernel32.QueryPerformanceCounter
    _query_performance_counter.argtypes = [PLONGLONG]
    _query_performance_counter.restype = bool
    _query_performance_counter.errcheck = raise_if_zero

    large_integer = LONGLONG()
    success = _query_performance_counter(BY_REF(large_integer))
    if not success:
        raise ctypes.WinError(get_last_error())
    return large_integer

def query_performance_frequency():
    """
    BOOL QueryPerformanceFrequency(
        LARGE_INTEGER *lpFrequency
    );
    """
    _query_performance_frequency = WINDLL.kernel32.QueryPerformanceFrequency
    _query_performance_frequency.argtypes = [PLONGLONG]
    _query_performance_frequency.restype = bool
    _query_performance_frequency.errcheck = raise_if_zero

    large_integer = LONGLONG()
    success = _query_performance_frequency(BY_REF(large_integer))
    if not success:
        raise ctypes.WinError(get_last_error())
    return large_integer

#==============================================================================
# This calculates the list of exported symbols.
_ALL = set(vars().keys()).difference(_ALL)
__all__ = [_x for _x in _ALL if not _x.startswith('_')]
__all__.sort()
#==============================================================================
