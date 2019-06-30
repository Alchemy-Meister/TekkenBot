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

from config import ReloadableConfig
from gui.controller import LaunchUpdaterController, TekkenBotPrimeController
from network.updater import Updater

class TekkenBotPrime():
    """
    """
    def __init__(self):
        updater_config = (
            ReloadableConfig('data/updater_config.ini').config['DEFAULT']
        )

        updater = Updater(
            updater_config['current_version'],
            updater_config['github_username'],
            updater_config['repository_name'],
            updater_config['download_filename_format']
        )
        del updater_config

        title = 'Tekken Bot Prime'
        icon = 'data/tekken_bot_close.ico'

        if updater.is_update_available():
            LaunchUpdaterController(
                updater, TekkenBotPrimeController, title=title, icon=icon
            )
        else:
            TekkenBotPrimeController(updater, title=title, icon=icon)

if __name__ == "__main__":
    TekkenBotPrime()
