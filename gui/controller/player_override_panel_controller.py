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

from constants.battle import BattleHealth
from gui.model import CharacterModel
from gui.view import PlayerOverwritePanel
from tekken import Launcher

class PlayerOverwritePanelController():
    """
    """
    def __init__(self, master, launcher: Launcher, player_num=1):
        self.character_model = CharacterModel()
        self.tekken_writer = launcher.game_state.get_writer()
        self.str_player = 'p{}'.format(player_num)

        self.view = PlayerOverwritePanel(
            master,
            self,
            format_string=self.str_player.capitalize(),
            text='Player {}'.format(player_num),
            max_health=BattleHealth.ARCADE_MAX_HEALTH.value
        )

    def checkbox_character_overwrite_change(self, enable):
        setattr(
            self.tekken_writer,
            'enable_{}_character_overwrite'.format(self.str_player),
            enable
        )

    def checkbox_health_overwrite_change(self, enable):
        setattr(
            self.tekken_writer,
            'enable_{}_health_overwrite'.format(self.str_player),
            enable
        )

    def populate_character_combobox(self):
        return self.character_model.get_name_values(sort=True)

    def default_overwrite_character(self):
        return getattr(
            CharacterModel,
            'get_{}_default_character'.format(self.str_player)
        )()

    def combobox_overwrite_character_change(self, event):
        setattr(
            self.tekken_writer,
            '{}_character_overwrite'.format(self.str_player),
            event.widget.get_selected()
        )

    def scale_health_overwrite_change(self, health):
        self.view.health_value.set(health)
        if self.view.str_health.get() != str(health):
            self.view.str_health.set(health)
            setattr(
                self.tekken_writer,
                '{}_health_overwrite'.format(self.str_player),
                health
            )
