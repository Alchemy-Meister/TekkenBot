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

import logging
import platform
import sys
import tkinter as tk

from config import ReloadableConfig
from gui.controller import LaunchUpdaterController, TekkenBotPrimeController
from log import Formatter
from network.updater import NoInternetConnectionError, Updater
import win32.defines as win32

class TekkenBotPrime():
    """
    """
    def __init__(self):

        title = 'Tekken Bot Prime'
        icon = 'data/tekken_bot_close.ico'

        if platform.architecture()[0] != '64bit':
            root = tk.Tk()
            root.withdraw()
            root.iconbitmap(icon)
            tk.messagebox.showerror(
                title,
                '{}\n{}'.format(
                    'You are building the project with 32-bit Python.',
                    'Try the 64-bit version instead.'
                )
            )
            sys.exit(win32.ERROR_INVALID_ENVIRONMENT)

        logging_handler = logging.StreamHandler(sys.stdout)
        logging_handler.setFormatter(Formatter())
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging_handler)

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

        update_available = False
        try:
            update_available = updater.is_update_available(timeout=5)
        except NoInternetConnectionError:
            logger.debug('unable to check for updates')

        if update_available:
            logger.debug('update available')
            LaunchUpdaterController(
                updater, TekkenBotPrimeController, title=title, icon=icon
            )
        else:
            logger.debug('update not available')
            TekkenBotPrimeController(updater, title=title, icon=icon)

if __name__ == "__main__":
    TekkenBotPrime()
