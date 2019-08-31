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
from constants.battle import PunishResult
from constants.event import PunishWindowEvent
from patterns.observer import Publisher, Subscriber
from patterns.singleton import Singleton
from tekken import Launcher

class PunishCoach(metaclass=Singleton):
    """
    """
    def __init__(self, launcher: Launcher):
        self.__launcher = launcher
        self.__current_punish_window = None
        self.__frames_since_new_window = 0

        subscriber = Subscriber()
        self.__launcher.publisher.register(
            Launcher.Event.UPDATED, subscriber, self.update_punish_window
        )
        self.publisher = Publisher(PunishWindowEvent)

    def update_punish_window(self, success):
        if success:
            if self.__launcher.game_state.state_log[-1].is_player_player_one:
                cyclopedia = self.__launcher.cyclopedia_p2
            else:
                cyclopedia = self.__launcher.cyclopedia_p1

            last_punish_window = self.__current_punish_window
            self.__current_punish_window = next(
                (
                    punish_window for punish_window in reversed(
                        cyclopedia.punish_windows
                    )
                    if punish_window.result != PunishResult.NOT_YET_CLOSED
                ),
                None
            )

            if self.__current_punish_window:
                if self.__current_punish_window != last_punish_window:
                    self.__frames_since_new_window = 0
                    self.publisher.dispatch(
                        PunishWindowEvent.CHANGED, self.__current_punish_window
                    )
                else:
                    self.__frames_since_new_window += 1
                    self.publisher.dispatch(
                        PunishWindowEvent.SAME, self.__frames_since_new_window
                    )
