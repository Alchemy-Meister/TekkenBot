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
from config import DefaultSettings
from constants.battle import PunishResult
from constants.event import PunishWindowEvent
from patterns.observer import Subscriber
from tekken.coach import PunishCoach

from .sound_player import SoundPlayer

class PunishCoachAlarm():
    """
    """
    def __init__(self, punish_coach: PunishCoach, initial_settings):
        self.__enabled = False
        self.__sound_folder = None
        self.__voice_folder = None
        self.__sound_played = False
        self.__current_punish_window = None

        self.reloadable_settings = initial_settings
        if self.reloadable_settings:
            self.reload()

        subscriber = Subscriber()
        punish_coach.publisher.register(
            PunishWindowEvent.CHANGED, subscriber, self.__initialize_variables
        )
        punish_coach.publisher.register(
            PunishWindowEvent.SAME, subscriber, self.__play_sound)

    def enable(self, enable):
        self.__enabled = enable
        if not self.__enabled:
            SoundPlayer.close()

    def reload(self):
        if self.reloadable_settings:
            settings = self.reloadable_settings.config['DEFAULT']
        else:
            settings = DefaultSettings.SETTINGS['DEFAULT']
        self.__enabled = settings.get('alarm_enable')
        self.__sound_folder = settings.get('alarm_sound_folder')
        self.__voice_folder = settings.get('alarm_voice_folder')

    def __initialize_variables(self, current_punish_window):
        self.__current_punish_window = current_punish_window
        self.__sound_played = False

    def __play_sound(self, frames_since_new_window):
        if(
                self.__enabled
                and frames_since_new_window < 60
                and not frames_since_new_window % 6
                and not self.__sound_played
        ):
            if(
                    getattr(
                        self.__current_punish_window.result,
                        'is_wrong_punish',
                        False
                    )
            ):
                if(
                        self.__current_punish_window
                        == PunishResult.NO_LAUNCH_ON_LAUNCHABLE
                ):
                    SoundPlayer.play(
                        'data/audios/sound/{}/no_launch_punish'.format(
                            self.__sound_folder
                        )
                    )
                else:
                    frame_advantage = (
                        self.__current_punish_window.get_frame_advantage()
                    )
                    try:
                        SoundPlayer.play(
                            'data/audios/voice/{}/{}'.format(
                                self.__voice_folder, frame_advantage
                            )
                        )
                    except OSError:
                        SoundPlayer.play(
                            'data/audios/sound/{}/no_jab_punish'.format(
                                self.__sound_folder
                            )
                        )
                self.__sound_played = True
            elif self.__current_punish_window.result != PunishResult.NO_WINDOW:
                SoundPlayer.play(
                    'data/audios/sound/{}/correct'.format(self.__sound_folder)
                )
                self.__sound_played = True
