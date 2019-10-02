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
import logging
from pathlib import Path
import sys

from log import Formatter
import win32.winmm as winmm

class SoundPlayer():
    """
    """
    @staticmethod
    def play(media_path):
        SoundPlayer.close()
        media_path = Path(media_path)
        if not media_path.is_absolute():
            media_path = media_path.absolute()
        if not media_path.suffix:
            media_path = next(
                (
                    media_file for media_file in media_path.parent.iterdir()
                    if media_path.name == media_file.stem
                ), None
            )
        open_media_command = 'open "{}" alias media'.format(media_path)
        SoundPlayer.__logger.debug(
            'sending command to CMI: %s', open_media_command
        )
        winmm.mci_send_string(open_media_command)
        winmm.mci_send_string('play media')

    @staticmethod
    def close():
        winmm.mci_send_string('close all')

    @classmethod
    def initialize_class_logger(cls):
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(Formatter())
        cls.__logger = logging.getLogger(__name__)
        cls.__logger.setLevel(logging.DEBUG)
        cls.__logger.addHandler(stdout_handler)
