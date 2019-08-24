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
Wrapper for user32.dll in ctypes.
"""
# pylint: disable=unused-wildcard-import,wildcard-import
import ctypes
from .defines import *  #NOQA
from .kernel32 import get_last_error, set_last_error
from .gdi32 import POINT, LPPOINT, RECT, LPRECT
from .version import BITS

#--- Constants ----------------------------------------------------------------

HWND_DESKTOP = 0

MONITOR_DEFAULTTONULL = 0
MONITOR_DEFAULTTOPRIMARY = 1
MONITOR_DEFAULTTONEAREST = 2

SM_CYCAPTION = 4
SM_CXBORDER = 5
SM_SWAPBUTTON = 23
SM_CXSIZEFRAME = 32
SM_CYFRAME = 33
SM_CXPADDEDBORDER = 92

# GetWindowLong
GWL_STYLE = -16
GWL_EXSTYLE = -20

# Styles
WS_OVERLAPPED = 0x00000000
WS_MAXIMIZEBOX = 0x00010000
WS_MINIMIZEBOX = 0x00020000
WS_THICKFRAME = 0x00040000
WS_SYSMENU = 0x00080000
WS_CAPTION = 0x00C00000
WS_OVERLAPPEDWINDOW = (
    WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_THICKFRAME | WS_MINIMIZEBOX
    | WS_MAXIMIZEBOX
)

# Virtual-Key Codes
VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_LWIN = 0x5B
VK_RWIN = 0x5C

# --- structures ---------------------------------------------------

# pylint: disable=too-few-public-methods
class MONITORINFO(Structure):
    """
    typedef struct tagMONITORINFO {
        DWORD cbSize;
        RECT  rcMonitor;
        RECT  rcWork;
        DWORD dwFlags;
    } MONITORINFO, *LPMONITORINFO;
    """

    _fields_ = [
        ('cb_size', DWORD),
        ('rc_monitor', RECT),
        ('rc_work', RECT),
        ('dw_flags', DWORD)
    ]

    def __init__(self, *args, **kwds):
        super(MONITORINFO, self).__init__(*args, **kwds)
        self.cb_size = SIZE_OF(self)

    def __repr__(self):
        return 'cb_size: {}, rc_monitor: {}, rc_work: {}, dw_flags: {}'.format(
            self.cb_size,
            repr(self.rc_monitor),
            repr(self.rc_work),
            self.dw_flags
        )

LPMONITORINFO = POINTER(MONITORINFO)

class WINDOWPLACEMENT(Structure):
    """
    typedef struct _WINDOWPLACEMENT {
        UINT length;
        UINT flags;
        UINT showCmd;
        POINT ptMinPosition;
        POINT ptMaxPosition;
        RECT rcNormalPosition;
    } WINDOWPLACEMENT;
    """
    _fields_ = [
        ('length', UINT),
        ('flags', UINT),
        ('show_cmd', UINT),
        ('pt_min_position', POINT),
        ('pt_max_position', POINT),
        ('rc_normal_position', RECT)
    ]

    def __init__(self, window_placement=None):
        super(WINDOWPLACEMENT, self).__init__()
        self.length = SIZE_OF(self)

        if window_placement:
            self.flags = window_placement.flags
            self.show_cmd = window_placement.show_cmd
            self.pt_min_position.x = window_placement.pt_min_position.x
            self.pt_min_position.y = window_placement.pt_min_position.y
            self.pt_max_position.x = window_placement.pt_max_position.x
            self.pt_max_position.y = window_placement.pt_max_position.y
            self.rc_normal_position.left = (
                window_placement.rc_normal_position.left
            )
            self.rc_normal_position.top = (
                window_placement.rc_normal_position.top
            )
            self.rc_normal_position.right = (
                window_placement.rc_normal_position.right
            )
            self.rc_normal_position.bottom = (
                window_placement.rc_normal_position.bottom
            )

PWINDOWPLACEMENT = POINTER(WINDOWPLACEMENT)
LPWINDOWPLACEMENT = PWINDOWPLACEMENT

#--- High level classes -------------------------------------------------------

# Point() and Rect() are here instead of gdi32.py because they were mainly
# created to handle window coordinates rather than drawing on the screen.

# XXX not sure if these classes should be psyco-optimized,
# it may not work if the user wants to serialize them for some reason

class Point():
    """
    Python wrapper over the L{POINT} class.
    @type x: int
    @ivar x: Horizontal coordinate
    @type y: int
    @ivar y: Vertical coordinate
    """

    def __init__(self, x=0, y=0):
        """
        @see: L{POINT}
        @type  x: int
        @param x: Horizontal coordinate
        @type  y: int
        @param y: Vertical coordinate
        """
        #pylint: disable=invalid-name
        self.x = x
        self.y = y

    def __iter__(self):
        return (self.x, self.y).__iter__()

    def __len__(self):
        return 2

    def __getitem__(self, index):
        return (self.x, self.y)[index]

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError("index out of range")

    def __repr__(self):
        return 'x: {}, y: {}'.format(self.x, self.y)

    @property
    def _as_parameter_(self):
        """
        Compatibility with ctypes.
        Allows passing transparently a Point object to an API call.
        """
        return POINT(self.x, self.y)

    def screen_to_client(self, h_wnd):
        """
        Translates window screen coordinates to client coordinates.
        @see: L{client_to_screen}, L{translate}
        @type  h_wnd: int or L{HWND} or L{system.Window}
        @param h_wnd: Window handle.
        @rtype:  L{Point}
        @return: New object containing the translated coordinates.
        """
        return screen_to_client(h_wnd, self)

    def client_to_screen(self, h_wnd):
        """
        Translates window client coordinates to screen coordinates.
        @see: L{screen_to_client}, L{translate}
        @type  h_wnd: int or L{HWND} or L{system.Window}
        @param h_wnd: Window handle.
        @rtype:  L{Point}
        @return: New object containing the translated coordinates.
        """
        return client_to_screen(h_wnd, self)

    def translate(self, h_wnd_from=HWND_DESKTOP, h_wnd_to=HWND_DESKTOP):
        """
        Translate coordinates from one window to another.
        @note: To translate multiple points it's more efficient to use the
            L{MapWindowPoints} function instead.
        @see: L{client_to_screen}, L{screen_to_client}
        @type  h_wnd_from: int or L{HWND} or L{system.Window}
        @param h_wnd_from: Window handle to translate from.
            Use C{HWND_DESKTOP} for screen coordinates.
        @type  h_wnd_to: int or L{HWND} or L{system.Window}
        @param h_wnd_to: Window handle to translate to.
            Use C{HWND_DESKTOP} for screen coordinates.
        @rtype:  L{Point}
        @return: New object containing the translated coordinates.
        """
        return map_window_points(h_wnd_from, h_wnd_to, [self])

class Rect():
    """
    Python wrapper over the L{RECT} class.
    @type   left: int
    @ivar   left: Horizontal coordinate for the top left corner.
    @type    top: int
    @ivar    top: Vertical coordinate for the top left corner.
    @type  right: int
    @ivar  right: Horizontal coordinate for the bottom right corner.
    @type bottom: int
    @ivar bottom: Vertical coordinate for the bottom right corner.
    @type  width: int
    @ivar  width: Width in pixels. Same as C{right - left}.
    @type height: int
    @ivar height: Height in pixels. Same as C{bottom - top}.
    """

    def __init__(self, left=0, top=0, right=0, bottom=0):
        """
        @see: L{RECT}
        @type    left: int
        @param   left: Horizontal coordinate for the top left corner.
        @type     top: int
        @param    top: Vertical coordinate for the top left corner.
        @type   right: int
        @param  right: Horizontal coordinate for the bottom right corner.
        @type  bottom: int
        @param bottom: Vertical coordinate for the bottom right corner.
        """
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __iter__(self):
        return (self.left, self.top, self.right, self.bottom).__iter__()

    def __len__(self):
        return 2

    def __getitem__(self, index):
        return (self.left, self.top, self.right, self.bottom)[index]

    def __setitem__(self, index, value):
        if index == 0:
            self.left = value
        elif index == 1:
            self.top = value
        elif index == 2:
            self.right = value
        elif index == 3:
            self.bottom = value
        else:
            raise IndexError("index out of range")

    @property
    def _as_parameter_(self):
        """
        Compatibility with ctypes.
        Allows passing transparently a Point object to an API call.
        """
        return RECT(self.left, self.top, self.right, self.bottom)

    def __get_width(self):
        return self.right - self.left

    def __get_height(self):
        return self.bottom - self.top

    def __set_width(self, value):
        self.right = value - self.left

    def __set_height(self, value):
        self.bottom = value - self.top

    width = property(__get_width, __set_width)
    height = property(__get_height, __set_height)

    def __eq__(self, rect):
        if not isinstance(rect, Rect):
            return NotImplemented
        return (
            self.left == rect.left
            and self.top == rect.top
            and self.right == rect.right
            and self.bottom == rect.bottom
        )

    def __ne__(self, rect):
        return not self == rect

    def screen_to_client(self, h_wnd):
        """
        Translates window screen coordinates to client coordinates.
        @see: L{client_to_screen}, L{translate}
        @type  h_wnd: int or L{HWND} or L{system.Window}
        @param h_wnd: Window handle.
        @rtype:  L{Rect}
        @return: New object containing the translated coordinates.
        """
        topleft = screen_to_client(h_wnd, (self.left, self.top))
        bottomright = screen_to_client(h_wnd, (self.bottom, self.right))
        return Rect(topleft.x, topleft.y, bottomright.x, bottomright.y)

    def client_to_screen(self, h_wnd):
        """
        Translates window client coordinates to screen coordinates.
        @see: L{screen_to_client}, L{translate}
        @type  hWnd: int or L{HWND} or L{system.Window}
        @param hWnd: Window handle.
        @rtype:  L{Rect}
        @return: New object containing the translated coordinates.
        """
        topleft = client_to_screen(h_wnd, (self.left, self.top))
        bottomright = client_to_screen(h_wnd, (self.bottom, self.right))
        return Rect(topleft.x, topleft.y, bottomright.x, bottomright.y)

    def translate(self, h_wnd_from=HWND_DESKTOP, h_wnd_to=HWND_DESKTOP):
        """
        Translate coordinates from one window to another.
        @see: L{client_to_screen}, L{screen_to_client}
        @type  h_wnd_from: int or L{HWND} or L{system.Window}
        @param h_wnd_from: Window handle to translate from.
            Use C{HWND_DESKTOP} for screen coordinates.
        @type  h_wnd_to: int or L{HWND} or L{system.Window}
        @param h_wnd_to: Window handle to translate to.
            Use C{HWND_DESKTOP} for screen coordinates.
        @rtype:  L{Rect}
        @return: New object containing the translated coordinates.
        """
        points = [(self.left, self.top), (self.right, self.bottom)]
        return map_window_points(h_wnd_from, h_wnd_to, points)

    @staticmethod
    def get_rect_from_structure(rect_struc):
        return Rect(
            rect_struc.left, rect_struc.top, rect_struc.right, rect_struc.bottom
        )

    def __repr__(self):
        return 'x: {}, y: {}, width: {}, height: {}'.format(
            self.left, self.top, self.width, self.height
        )

class MonitorInfo():
    """
    Python wrapper over the L{MONITORINFO} class.
    @type monitor_info: L{MonitorInfo} or L{MONITORINFO}
    @ivar monitor_info: Another monitor info object.
    """

    MONITORINFOF_PRIMARY = 1

    def __init__(self, monitor_info=None):
        self.cb_size = monitor_info.cb_size
        self.rc_monitor = Rect.get_rect_from_structure(
            monitor_info.rc_monitor
        )
        self.rc_work = Rect.get_rect_from_structure(
            monitor_info.rc_work
        )
        self.dw_flags = monitor_info.dw_flags

    def __repr__(self):
        return 'cb_size: {}, rc_monitor: {}, rc_work: {}, dw_flags: {}'.format(
            self.cb_size,
            repr(self.rc_monitor),
            repr(self.rc_work),
            self.dw_flags
        )

class WindowPlacement():
    """
    Python wrapper over the L{WINDOWPLACEMENT} class.
    """

    def __init__(self, window_placement=None):
        """
        @type  window_placement: L{WindowPlacement} or L{WINDOWPLACEMENT}
        @param window_placement: Another window placement object.
        """

        # Initialize all properties with empty values.
        self.flags = 0
        self.show_cmd = 0
        self.pt_min_position = Point()
        self.pt_max_position = Point()
        self.rc_normal_position = Rect()

        # If a window placement was given copy it's properties.
        if window_placement:
            self.flags = window_placement.flags
            self.show_cmd = window_placement.show_cmd
            self.pt_min_position = Point(
                window_placement.pt_min_position.x,
                window_placement.pt_min_position.y
            )
            self.pt_max_position = Point(
                window_placement.pt_max_position.x,
                window_placement.pt_max_position.y
            )
            self.rc_normal_position = Rect(
                window_placement.rc_normal_position.left,
                window_placement.rc_normal_position.top,
                window_placement.rc_normal_position.right,
                window_placement.rc_normal_position.bottom,
            )

    @property
    def _as_parameter_(self):
        """
        Compatibility with ctypes.
        Allows passing transparently a Point object to an API call.
        """
        return WINDOWPLACEMENT(window_placement=self)

    def __repr__(self):
        return (
            """
            flags: {},\n
            show_cmd: {},\n
            pt_min_position: {},\n
            pt_max_position: {},\n
            rc_normal_position: {}
            """.format(
                self.flags,
                self.show_cmd,
                repr(self.pt_min_position),
                repr(self.pt_max_position),
                repr(self.rc_normal_position)
            )
        )

# --- user32.dll --------------------------------------------------------------

def find_window_a(lp_class_name=None, lp_window_name=None):
    """
    HWND FindWindowA(
        LPCTSTR lpClassName,
        LPCTSTR lpWindowName
    );
    """
    _find_window_a = WINDLL.user32.FindWindowA
    _find_window_a.argtypes = [LPSTR, LPSTR]
    _find_window_a.restype = HWND

    h_wnd = _find_window_a(lp_class_name, lp_window_name)
    if not h_wnd:
        errcode = get_last_error()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return h_wnd

def find_window_w(lp_class_name=None, lp_window_name=None):
    """
    HWND FindWindowW(
        LPCWSTR lpClassName,
        LPCWSTR lpWindowName
    );
    """
    _find_window_w = WINDLL.user32.FindWindowW
    _find_window_w.argtypes = [LPWSTR, LPWSTR]
    _find_window_w.restype = HWND

    h_wnd = _find_window_w(lp_class_name, lp_window_name)
    if not h_wnd:
        errcode = get_last_error()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return h_wnd

def find_window(lp_class_name=None, lp_window_name=None):
    return GuessStringType(find_window_a, find_window_w)(
        lp_class_name, lp_window_name
    )

def find_window_ex_a(
        hwnd_parent=None, hwnd_child_after=None,
        lp_class_name=None, lp_window_name=None
):
    """
    HWND WINAPI FindWindowExA(
        __in_opt  HWND hwndParent,
        __in_opt  HWND hwndChildAfter,
        __in_opt  LPCTSTR lpszClass,
        __in_opt  LPCTSTR lpszWindow
    );
    """
    _find_window_ex_a = WINDLL.user32.FindWindowExA
    _find_window_ex_a.argtypes = [HWND, HWND, LPSTR, LPSTR]
    _find_window_ex_a.restype = HWND

    h_wnd = _find_window_ex_a(
        hwnd_parent, hwnd_child_after, lp_class_name, lp_window_name
    )
    if not h_wnd:
        errcode = get_last_error()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return h_wnd

def find_window_ex_w(
        hwnd_parent=None, hwnd_child_after=None,
        lp_class_name=None, lp_window_name=None
):
    """
    HWND WINAPI FindWindowExW(
        __in_opt  HWND hwndParent,
        __in_opt  HWND hwndChildAfter,
        __in_opt  LPCWSTR lpszClass,
        __in_opt  LPCWSTR lpszWindow
    );
    """
    _find_window_ex_w = WINDLL.user32.FindWindowExW
    _find_window_ex_w.argtypes = [HWND, HWND, LPWSTR, LPWSTR]
    _find_window_ex_w.restype = HWND

    h_wnd = _find_window_ex_w(
        hwnd_parent, hwnd_child_after, lp_class_name, lp_window_name
    )
    if not h_wnd:
        errcode = get_last_error()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return h_wnd

FIND_WINDOW_EX = GuessStringType(find_window_ex_a, find_window_ex_w)

def get_async_key_state(v_key):
    """
    SHORT GetAsyncKeyState(
        int vKey
    );
    """
    _get_async_key_state = WINDLL.user32.GetAsyncKeyState
    _get_async_key_state.argtypes = [INT]
    _get_async_key_state.restype = SHORT
    return _get_async_key_state(v_key)

def get_window_text_a(h_wnd):
    """
    int WINAPI GetWindowTextA(
        __in   HWND hWnd,
        __out  LPTSTR lpString,
        __in   int nMaxCount
    );
    """
    _get_window_text_a = WINDLL.user32.GetWindowTextA
    _get_window_text_a.argtypes = [HWND, LPSTR, ctypes.c_int]
    _get_window_text_a.restype = ctypes.c_int


    n_max_count = 0x1000
    dw_char_size = SIZE_OF(CHAR)
    while 1:
        lp_string = ctypes.create_string_buffer(b'', n_max_count)
        n_count = _get_window_text_a(h_wnd, lp_string, n_max_count)
        if n_count == 0:
            raise ctypes.WinError()
        if n_count < n_max_count - dw_char_size:
            break
        n_max_count += 0x1000
    return lp_string.value

def get_window_text_w(h_wnd):
    """
    int WINAPI GetWindowTextA(
        __in   HWND hWnd,
        __out  LPWSTR lpString,
        __in   int nMaxCount
    );
    """
    _get_window_text_w = WINDLL.user32.GetWindowTextW
    _get_window_text_w.argtypes = [HWND, LPWSTR, ctypes.c_int]
    _get_window_text_w.restype = ctypes.c_int

    n_max_count = 0x1000
    dw_char_size = SIZE_OF(CHAR)
    while 1:
        lp_string = ctypes.create_unicode_buffer('', n_max_count)
        n_count = _get_window_text_w(h_wnd, lp_string, n_max_count)
        if n_count == 0:
            raise ctypes.WinError()
        if n_count < n_max_count - dw_char_size:
            break
        n_max_count += 0x1000
    return lp_string.value

GET_WINDOW_TEXT = GuessStringType(get_window_text_a, get_window_text_w)

def get_window_long_a(h_wnd, n_index=0):
    """
    LONG GetWindowLongA(
        HWND hWnd,
        int nIndex
    );
    """
    _get_window_long_a = WINDLL.user32.GetWindowLongA
    _get_window_long_a.argtypes = [HWND, ctypes.c_int]
    _get_window_long_a.restype = DWORD

    set_last_error(ERROR_SUCCESS)
    retval = _get_window_long_a(h_wnd, n_index)
    if retval == 0:
        errcode = get_last_error()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return retval

def get_window_long_w(h_wnd, n_index=0):
    _get_window_long_w = WINDLL.user32.GetWindowLongW
    _get_window_long_w.argtypes = [HWND, ctypes.c_int]
    _get_window_long_w.restype = DWORD

    set_last_error(ERROR_SUCCESS)
    retval = _get_window_long_w(h_wnd, n_index)
    if retval == 0:
        errcode = get_last_error()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return retval

def get_window_long(h_wnd, n_index=0):
    return DefaultStringType(get_window_long_a, get_window_long_w)(
        h_wnd, n_index
    )

if BITS == 32:
    def get_window_long_ptr_a(h_wnd, n_index=0):
        get_window_long_a(h_wnd, n_index)

    def get_window_long_ptr_w(h_wnd, n_index=0):
        get_window_long_w(h_wnd, n_index)

    def get_window_long_ptr(h_wnd, n_index=0):
        get_window_long(h_wnd, n_index)
else:
    def get_window_long_ptr_a(h_wnd, n_index=0):
        _get_window_long_ptr_a = WINDLL.user32.GetWindowLongPtrA
        _get_window_long_ptr_a.argtypes = [HWND, ctypes.c_int]
        _get_window_long_ptr_a.restype = SIZE_T

        set_last_error(ERROR_SUCCESS)
        retval = _get_window_long_ptr_a(h_wnd, n_index)
        if retval == 0:
            errcode = get_last_error()
            if errcode != ERROR_SUCCESS:
                raise ctypes.WinError(errcode)
        return retval

    def get_window_long_ptr_w(h_wnd, n_index=0):
        _get_window_long_ptr_w = WINDLL.user32.GetWindowLongPtrW
        _get_window_long_ptr_w.argtypes = [HWND, ctypes.c_int]
        _get_window_long_ptr_w.restype = DWORD

        set_last_error(ERROR_SUCCESS)
        retval = _get_window_long_ptr_w(h_wnd, n_index)
        if retval == 0:
            errcode = get_last_error()
            if errcode != ERROR_SUCCESS:
                raise ctypes.WinError(errcode)
        return retval

    def get_window_long_ptr(h_wnd, n_index=0):
        return DefaultStringType(get_window_long_ptr_a, get_window_long_ptr_w)(
            h_wnd, n_index
        )

def is_iconic(h_wnd):
    """
    BOOL IsIconic(
        HWND hWnd
    );
    """
    _is_iconic = WINDLL.user32.IsIconic
    _is_iconic.argtypes = [HWND]
    _is_iconic.restype = bool

    return _is_iconic(h_wnd)

def is_window_visible(h_wnd):
    """
    BOOL IsWindowVisible(
        HWND hWnd
    );
    """
    _is_window_visible = WINDLL.user32.IsWindowVisible
    _is_window_visible.argtypes = [HWND]
    _is_window_visible.restype = bool

    return _is_window_visible(h_wnd)

def client_to_screen(h_wnd, lp_point):
    """
    BOOL ClientToScreen(
        HWND hWnd,
        LPPOINT lpPoint
    );
    """
    _client_to_screen = WINDLL.user32.ClientToScreen
    _client_to_screen.argtypes = [HWND, LPPOINT]
    _client_to_screen.restype = bool
    _client_to_screen.errcheck = raise_if_zero

    if isinstance(lp_point, tuple):
        lp_point = POINT(*lp_point)
    else:
        lp_point = POINT(lp_point.x, lp_point.y)
    _client_to_screen(h_wnd, BY_REF(lp_point))
    return Point(lp_point.x, lp_point.y)

def get_shell_window():
    """
    HWND GetShellWindow(VOID);
    """
    _get_shell_window = WINDLL.user32.GetShellWindow
    _get_shell_window.argtypes = []
    _get_shell_window.restype = HWND
    _get_shell_window.errcheck = raise_if_zero
    return _get_shell_window()

def get_desktop_window():
    """
    HWND GetDesktopWindow(VOID);
    """
    _get_desktop_window = WINDLL.user32.GetDesktopWindow
    _get_desktop_window.argtypes = []
    _get_desktop_window.restype = HWND
    _get_desktop_window.errcheck = raise_if_zero
    return _get_desktop_window()

def get_foreground_window():
    """
    HWND GetForegroundWindow(VOID);
    """
    _get_foreground_window = WINDLL.user32.GetForegroundWindow
    _get_foreground_window.argtypes = []
    _get_foreground_window.restype = HWND
    _get_foreground_window.errcheck = raise_if_zero
    return _get_foreground_window()

def __get_monitor_info(get_monitor_info_func, h_monitor):
    get_monitor_info_func.argtypes = [HMONITOR, LPMONITORINFO]
    get_monitor_info_func.restype = bool
    get_monitor_info_func.errcheck = raise_if_zero

    monitor_info = MONITORINFO()
    success = get_monitor_info_func(h_monitor, BY_REF(monitor_info))
    if not success:
        raise WindowsError()
    return MonitorInfo(monitor_info)

def get_monitor_info_a(h_monitor):
    """
    BOOL GetMonitorInfoA(
        HMONITOR      hMonitor,
        LPMONITORINFO lpmi
    );
    """
    return __get_monitor_info(WINDLL.user32.GetMonitorInfoA, h_monitor)

def get_monitor_info_w(h_monitor):
    """
    BOOL GetMonitorInfoW(
        HMONITOR      hMonitor,
        LPMONITORINFO lpmi
    );
    """
    return __get_monitor_info(WINDLL.user32.GetMonitorInfoW, h_monitor)


def get_monitor_info(h_monitor):
    return GuessStringType(get_monitor_info_a, get_monitor_info_w)(h_monitor)

def get_system_metrics(n_index):
    """
    int GetSystemMetrics(
        int nIndex
    );
    """
    _get_system_metrics = WINDLL.user32.GetSystemMetrics
    _get_system_metrics.argtypes = [ctypes.c_int]
    _get_system_metrics.restype = ctypes.c_int

    metric = _get_system_metrics(n_index)
    error_code = get_last_error()
    if not metric and error_code != ERROR_SUCCESS:
        raise ctypes.WinError(error_code)
    return metric

def get_window_placement(h_wnd):
    """
    BOOL GetWindowPlacement(
        HWND hWnd,
        WINDOWPLACEMENT *lpwndpl
    );
    """
    _get_window_placement = WINDLL.user32.GetWindowPlacement
    _get_window_placement.argtypes = [HWND, PWINDOWPLACEMENT]
    _get_window_placement.restype = bool
    _get_window_placement.errcheck = raise_if_zero

    lpwndpl = WINDOWPLACEMENT()
    _get_window_placement(h_wnd, BY_REF(lpwndpl))
    return WindowPlacement(lpwndpl)

def set_window_placement(h_wnd, lpwndpl):
    """
    BOOL SetWindowPlacement(
        HWND hWnd,
        WINDOWPLACEMENT *lpwndpl
    );
    """
    _set_window_placement = WINDLL.user32.SetWindowPlacement
    _set_window_placement.argtypes = [HWND, PWINDOWPLACEMENT]
    _set_window_placement.restype = bool
    _set_window_placement.errcheck = raise_if_zero

    _set_window_placement(h_wnd, BY_REF(lpwndpl))

def get_window_rect(h_wnd):
    """
    BOOL WINAPI GetWindowRect(
        __in   HWND hWnd,
        __out  LPRECT lpRect
    );
    """
    _get_window_rect = WINDLL.user32.GetWindowRect
    _get_window_rect.argtypes = [HWND, LPRECT]
    _get_window_rect.restype = bool
    _get_window_rect.errcheck = raise_if_zero

    lp_rect = RECT()
    _get_window_rect(h_wnd, BY_REF(lp_rect))
    return Rect.get_rect_from_structure(lp_rect)

def get_window_thread_process_id(h_wnd):
    """
    DWORD GetWindowThreadProcessId(
        HWND hWnd,
        LPDWORD lpdwProcessId
    );
    """
    _get_window_thread_process_id = WINDLL.user32.GetWindowThreadProcessId
    _get_window_thread_process_id.argtypes = [HWND, LPDWORD]
    _get_window_thread_process_id.restype = DWORD
    _get_window_thread_process_id.errcheck = raise_if_zero

    dw_process_id = DWORD(0)
    dw_thread_id = _get_window_thread_process_id(h_wnd, BY_REF(dw_process_id))
    return (dw_thread_id, dw_process_id.value)

def map_window_points(h_wnd_from, h_wnd_to, lp_points):
    """
    int MapWindowPoints(
        __in     HWND hWndFrom,
        __in     HWND hWndTo,
        __inout  LPPOINT lpPoints,
        __in     UINT cPoints
    );
    """
    _map_window_points = WINDLL.user32.MapWindowPoints
    _map_window_points.argtypes = [HWND, HWND, LPPOINT, UINT]
    _map_window_points.restype = ctypes.c_int

    c_points = len(lp_points)
    lp_points = (POINT * c_points)(*lp_points)
    set_last_error(ERROR_SUCCESS)
    number = _map_window_points(
        h_wnd_from, h_wnd_to, BY_REF(lp_points), c_points
    )
    if number == 0:
        errcode = get_last_error()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    x_delta = number & 0xFFFF
    y_delta = (number >> 16) & 0xFFFF
    return x_delta, y_delta, [(Point.x, Point.y) for Point in lp_points]

def monitor_from_window(h_wnd, dw_flags):
    """
    HMONITOR MonitorFromWindow(
        HWND  hwnd,
        DWORD dwFlags
    );
    """
    _monitor_from_window = WINDLL.user32.MonitorFromWindow
    _monitor_from_window.argtypes = [HWND, DWORD]
    _monitor_from_window.restype = HMONITOR

    return _monitor_from_window(h_wnd, dw_flags)

def screen_to_client(h_wnd, lp_point):
    """
    BOOL ScreenToClient(
        __in  HWND hWnd,
        LPPOINT lpPoint
    );
    """
    _screen_to_client = WINDLL.user32.ScreenToClient
    _screen_to_client.argtypes = [HWND, LPPOINT]
    _screen_to_client.restype = bool
    _screen_to_client.errcheck = raise_if_zero

    if isinstance(lp_point, tuple):
        lp_point = POINT(*lp_point)
    else:
        lp_point = POINT(lp_point.x, lp_point.y)
    _screen_to_client(h_wnd, BY_REF(lp_point))
    return Point(lp_point.x, lp_point.y)
