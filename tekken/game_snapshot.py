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

import math

class GameSnapshot:
    """

    """
    def __init__(
            self, bot, opp, frame_count, timer_in_frames, facing_bool,
            opponent_name, is_player_player_one
    ):
        self.bot = bot
        self.opp = opp
        self.frame_count = frame_count
        self.facing_bool = facing_bool
        self.timer_frames_remaining = timer_in_frames
        self.opponent_name = opponent_name
        self.is_player_player_one = is_player_player_one

    def FromMirrored(self):
        """

        """
        return GameSnapshot(
            self.opp, self.bot, self.frame_count, self.timer_frames_remaining,
            self.facing_bool, self.opponent_name, self.is_player_player_one
        )

    def GetDist(self):
        """

        """
        # print(
        #     '{}, {} : {}, {}'.format(
        #         self.bot.skeleton[0][22], self.opp.skeleton[0][22],
        #         self.bot.skeleton[2][22], self.opp.skeleton[2][22]
        #     )
        # )
        return math.hypot(
            self.bot.skeleton[0][22] - self.opp.skeleton[0][22],
            self.bot.skeleton[2][22] - self.opp.skeleton[2][22]
        )
