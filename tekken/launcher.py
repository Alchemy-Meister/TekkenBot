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
"""
import enum
import logging
import traceback
import sys

from log import Formatter
from patterns.observer import Publisher
from win32.utils import os_time

from .encyclopedia import TekkenEncyclopedia
from .game_state import TekkenGameState

class Launcher:
    """
    """
    class Event(enum.IntEnum):
        INITIALIZED = enum.auto()
        UPDATED = enum.auto()
        CLOSED = enum.auto()

    INITIAL_SHORT_DELAY = 2
    INITIAL_LONG_DELAY = 8

    def __init__(self, view, extended_print=False):
        self.view = view
        self.extended_print = extended_print

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(Formatter())
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(stdout_handler)

        self.initialized = False
        self.publisher = Publisher(Launcher.Event)
        self.game_state = TekkenGameState()
        self.cyclopedia_p1 = TekkenEncyclopedia(
            True, print_extended_frame_data=self.extended_print
        )
        self.cyclopedia_p2 = TekkenEncyclopedia(
            False, print_extended_frame_data=self.extended_print
        )

    def start(self):
        self.__update_launcher()

    def __update_launcher(self):
        start = os_time.now(resolution=os_time.Resolution.MILLI)
        sucessful = self.game_state.update()
        if sucessful:
            try:
                self.cyclopedia_p1.update(self.game_state)
                self.cyclopedia_p2.update(self.game_state)
            except:
                traceback.print_exc()
        end = os_time.now(resolution=os_time.Resolution.MILLI)
        elapsed_time = (end - start)
        if self.game_state.is_pid_valid():
            if self.game_state.is_tekken_visible():
                if not self.initialized:
                    self.initialized = True
                    self.publisher.dispatch(Launcher.Event.INITIALIZED)
                else:
                    self.publisher.dispatch(Launcher.Event.UPDATED, sucessful)
            self.view.after(
                max(
                    Launcher.INITIAL_SHORT_DELAY,
                    round(Launcher.INITIAL_LONG_DELAY - elapsed_time)
                ),
                self.__update_launcher
            )
        else:
            if self.initialized:
                self.initialized = False
                self.publisher.dispatch(Launcher.Event.CLOSED)
            self.view.after(1000, self.__update_launcher)
