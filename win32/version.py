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
Detect the current architecture and operating system.
Some functions here are really from kernel32.dll, others from version.dll.
"""

#pylint: disable=unused-wildcard-import,wildcard-import
from .defines import *  # NOQA

# --- NTDDI version -----------------------------------------------------------
NTDDI_VISTA = 0x06000000

# --- OSVERSIONINFO and OSVERSIONINFOEX structures and constants --------------
class OSVersionInfoA(Structure):
    """
    typedef struct _OSVERSIONINFOA {
        DWORD dwOSVersionInfoSize;
        DWORD dwMajorVersion;
        DWORD dwMinorVersion;
        DWORD dwBuildNumber;
        DWORD dwPlatformId;
        CHAR  szCSDVersion[128];
    } OSVERSIONINFOA;
    """
    _fields_ = [
        ("dw_os_version_info_size", DWORD),
        ("dw_major_version", DWORD),
        ("dw_minor_version", DWORD),
        ("dw_build_mumber", DWORD),
        ("dw_platform_id", DWORD),
        ("sz_csd_version", CHAR * 128),
    ]
class OSVersionInfoW(Structure):
    """
    typedef struct _OSVERSIONINFOW {
        DWORD dwOSVersionInfoSize;
        DWORD dwMajorVersion;
        DWORD dwMinorVersion;
        DWORD dwBuildNumber;
        DWORD dwPlatformId;
        WCHAR szCSDVersion[128];
    } OSVERSIONINFOW;
    """
    _fields_ = [
        ("dw_os_version_info_size", DWORD),
        ("dw_major_version", DWORD),
        ("dw_minor_version", DWORD),
        ("dw_build_mumber", DWORD),
        ("dw_platform_id", DWORD),
        ("sz_csd_version", WCHAR * 128),
    ]

class OSVersionInfoExA(Structure):
    """
    typedef struct _OSVERSIONINFOEXA {
        DWORD dwOSVersionInfoSize;
        DWORD dwMajorVersion;
        DWORD dwMinorVersion;
        DWORD dwBuildNumber;
        DWORD dwPlatformId;
        CHAR  szCSDVersion[128];
        WORD  wServicePackMajor;
        WORD  wServicePackMinor;
        WORD  wSuiteMask;
        BYTE  wProductType;
        BYTE  wReserved;
    } OSVERSIONINFOEXA;
    """
    _fields_ = [
        ("dw_os_version_info_size", DWORD),
        ("dw_major_version", DWORD),
        ("dw_minor_version", DWORD),
        ("dw_build_mumber", DWORD),
        ("dw_platform_id", DWORD),
        ("sz_csd_version", CHAR * 128),
        ("w_service_pack_major", WORD),
        ("w_service_pack_minor", WORD),
        ("w_suite_mask", WORD),
        ("w_product_type", BYTE),
        ("w_reserved", BYTE),
    ]

    def __init__(self):
        super().__init__()
        self.dw_os_version_info_size = SIZE_OF(self)

class OSVersionInfoExW(Structure):
    """
    typedef struct _OSVERSIONINFOEXW {
        ULONG  dwOSVersionInfoSize;
        ULONG  dwMajorVersion;
        ULONG  dwMinorVersion;
        ULONG  dwBuildNumber;
        ULONG  dwPlatformId;
        WCHAR  szCSDVersion[128];
        USHORT wServicePackMajor;
        USHORT wServicePackMinor;
        USHORT wSuiteMask;
        UCHAR  wProductType;
        UCHAR  wReserved;
    } OSVERSIONINFOEXW;
    """
    _fields_ = [
        ("dw_os_version_info_size", DWORD),
        ("dw_major_version", DWORD),
        ("dw_minor_version", DWORD),
        ("dw_build_mumber", DWORD),
        ("dw_platform_id", DWORD),
        ("sz_csd_version", WCHAR * 128),
        ("w_service_pack_major", WORD),
        ("w_service_pack_minor", WORD),
        ("w_suite_mask", WORD),
        ("w_product_type", BYTE),
        ("w_reserved", BYTE),
    ]

    def __init__(self):
        super().__init__()
        self.dw_os_version_info_size = SIZE_OF(self)

# HANDLE WINAPI GetCurrentProcess(void);
def get_current_process():
    """
    return 0xFFFFFFFFFFFFFFFFL
    """
    _get_current_process = WINDLL.kernel32.GetCurrentProcess
    _get_current_process.argtypes = []
    _get_current_process.restype = HANDLE
    return _get_current_process()

def get_version_ex_a():
    """
    BOOL WINAPI GetVersionExA(
    __inout  LPOSVERSIONINFOA lpVersionInfo
    );
    """
    _get_version_ex_a = WINDLL.kernel32.GetVersionExA
    _get_version_ex_a.argtypes = [POINTER(OSVersionInfoExA)]
    _get_version_ex_a.restype = bool
    _get_version_ex_a.errcheck = raise_if_zero

    osvi = OSVersionInfoExA()
    try:
        _get_version_ex_a(BY_REF(osvi))
    except WindowsError:
        osvi = OSVersionInfoA()
        _get_version_ex_a.argtypes = [POINTER(OSVersionInfoA)]
        _get_version_ex_a(BY_REF(osvi))
    return osvi

def get_version_ex_w():
    """
    BOOL WINAPI GetVersionExW(
    __inout  LPOSVERSIONINFOW lpVersionInfo
    );
    """
    _get_version_ex_w = WINDLL.kernel32.GetVersionExW
    _get_version_ex_w.argtypes = [POINTER(OSVersionInfoExW)]
    _get_version_ex_w.restype = bool
    _get_version_ex_w.errcheck = raise_if_zero

    osvi = OSVersionInfoExW()
    try:
        _get_version_ex_w(BY_REF(osvi))
    except WindowsError:
        osvi = OSVersionInfoW()
        _get_version_ex_w.argtypes = [POINTER(OSVersionInfoW)]
        _get_version_ex_w(BY_REF(osvi))
    return osvi

GET_VERISON_EX = GuessStringType(get_version_ex_a, get_version_ex_w)

def _get_ntddi(osvi):
    """
    Determines the current operating system.
    This function allows you to quickly tell apart major OS differences.
    For more detailed information call L{kernel32.GetVersionEx} instead.
    @note:
        Wine reports itself as Windows XP 32 bits
        (even if the Linux host is 64 bits).
        ReactOS may report itself as Windows 2000 or Windows XP,
        depending on the version of ReactOS.
    @type  osvi: L{OSVersionInfoExA}
    @param osvi: Optional. The return value from L{kernel32.GetVersionEx}.
    @rtype:  int
    @return: NTDDI version number.
    """
    if not osvi:
        osvi = GET_VERISON_EX()
    ntddi = 0
    ntddi += (osvi.dw_major_version & 0xFF) << 24
    ntddi += (osvi.dw_minor_version & 0xFF) << 16
    ntddi += (osvi.w_service_pack_major & 0xFF) << 8
    ntddi += (osvi.w_service_pack_minor & 0xFF)
    return ntddi

_OSVI = GET_VERISON_EX()

# Current operating system as an NTDDI constant.
# See L{_get_ntddi} for more details.
NTDDI_VERSION = _get_ntddi(_OSVI)
