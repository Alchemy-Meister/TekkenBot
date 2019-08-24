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
import sys
import enum
import time
import queue
import threading
from patterns.observer import Publisher
from tekken_game_state import TekkenGameState
from TekkenEncyclopedia import TekkenEncyclopedia

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
        self.initialized = False
        self.publisher = Publisher(Launcher.Event)
        self.game_state = None
        self.cyclopedia_p2 = None
        self.cyclopedia_p1 = None
        self.queue = queue.Queue()
        self.__run = True

        self.delay = Launcher.INITIAL_SHORT_DELAY
        self.last_executed_time = None

    def start(self):
        self.__start()
        self.__update_launcher()

    def stop(self):
        self.__run = False

    def __start(self):
        try:
            message = self.queue.get_nowait()
            if isinstance(message, dict):
                self.game_state = message['game_state']
                self.cyclopedia_p1 = message['p1']
                self.cyclopedia_p2 = message['p2']
                if not self.initialized:
                    self.initialized = True
                    self.publisher.dispatch(Launcher.Event.INITIALIZED)
                self.publisher.dispatch(
                    Launcher.Event.UPDATED, message['sucessful']
                )
            else:
                self.initialized = False
                self.publisher.dispatch(Launcher.Event.CLOSED)

            self.__update_delay()
        except queue.Empty:
            pass
        self.view.after(self.delay, self.__start)

    def __update_delay(self):
        if self.last_executed_time is None:
            self.last_executed_time = time.time()
        else:
            now = time.time()
            elapsed_time = 1000 * (now - self.last_executed_time)
            avg_delay = (self.delay * 0.8 + elapsed_time * 0.2) / 2
            if avg_delay > Launcher.INITIAL_SHORT_DELAY:
                self.delay = int(avg_delay)
            self.last_executed_time = now

    def __update_launcher(self):
        def update(launcher_queue):
            if not self.game_state:
                game_state = TekkenGameState()
            if not self.cyclopedia_p1:
                cyclopedia_p1 = TekkenEncyclopedia(
                    True, print_extended_frame_data=self.extended_print
                )
            if not self.cyclopedia_p2:
                cyclopedia_p2 = TekkenEncyclopedia(
                    False, print_extended_frame_data=self.extended_print
                )
            while self.__run:
                start = time.time()
                sucessful = game_state.update()
                if sucessful:
                    cyclopedia_p1.update(game_state)
                    cyclopedia_p2.update(game_state)
                launcher_queue.put(
                    {
                        'sucessful': sucessful,
                        'game_state': game_state,
                        'p1': cyclopedia_p1,
                        'p2': cyclopedia_p2
                    }
                )
                end = time.time()
                elapsed_time = end - start
                if game_state.get_reader().is_pid_valid():
                    time.sleep(
                        max(
                            Launcher.INITIAL_SHORT_DELAY / 1000,
                            Launcher.INITIAL_LONG_DELAY / 1000 - elapsed_time
                        )
                    )
                else:
                    if self.initialized:
                        launcher_queue.put(False)
                    time.sleep(1)

        threading.Thread(target=update, args=(self.queue,)).start()
