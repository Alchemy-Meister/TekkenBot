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
import tkinter as tk

from constants.overlay import OverlayMode, OverlayPosition
from config import ReloadableConfigManager
from gui.model import OverlayModel
from gui.my_tkinter import StdStreamRedirector
from gui.my_tkinter.overlay import OverlayManager
from gui.view import TekkenBotPrimeView

from tekken.launcher import Launcher

from .memory_override_panel_controller import MemoryOverwritePanelController

class TekkenBotPrimeController():
    """
    """
    def __init__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        self.root = tk.Tk()
        self.model = OverlayModel()

        self.save_to_file = True
        self.is_auto_scroll_enabled = True

        self.root.title('Tekken Bot Prime')
        self.root.iconbitmap('TekkenData/tekken_bot_close.ico')
        self.root.geometry('{}x{}'.format(920, 720))
        self.root.protocol('WM_DELETE_WINDOW', self.on_delete_window)

        self.view = TekkenBotPrimeView(self.root, self)

        self.launcher = Launcher(self.root, extended_print=False)

        self.overlay_manager = None
        self.__intialize_overlay_settings()

        self.__redirect_stdout_to_console(self.view.console)
        TekkenBotPrimeController.__initialize_console_text()

        self.__initialize_memory_override_panel()

        self.launcher.start()
        self.root.mainloop()

    def restart(self):
        self.model.reload()
        self.view.load_overlay_themes(
            enumerate(self.model.get_overlay_themes_names())
        )
        sys.stdout.write('restart')

    def enable_save_to_file(self, enable):
        sys.stdout.enable_save_to_file(enable)

    def is_save_to_file_enabled(self):
        return self.save_to_file

    def enable_auto_scroll(self, enable):
        sys.stdout.enable_auto_scroll(enable)

    def show_memory_override(self, enable):
        if enable:
            self.view.show_memory_overwrite_panel()
        else:
            self.view.hide_memory_overwrite_panel()

    def enable_overlay(self, enable):
        self.overlay_manager.enable_overlay(enable)

    def overlay_mode_change(self, overlay_mode_name):
        self.overlay_manager.change_overlay(
            OverlayModel.get_overlay_mode_enum(overlay_mode_name)
        )

    def overlay_position_change(self, overlay_position_name):
        self.overlay_manager.change_overlay_position(
            OverlayModel.get_overlay_position_enum(overlay_position_name)
        )

    def overlay_theme_change(self, overlay_theme_index):
        self.overlay_manager.change_overlay_theme(
            self.model.get_theme(overlay_theme_index)
        )

    def check_for_updates(self):
        sys.stdout.write('There are currently no updates available.')

    def on_delete_window(self):
        sys.stdout.close()
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        self.root.destroy()

    def populate_overlay_modes_submenu(self):
        return self.model.all_overlay_modes

    def populate_overlay_positions_submenu(self):
        return self.model.all_overlay_positions

    def populate_overlay_themes_submenu(self):
        return enumerate(self.model.get_overlay_themes_names())

    def __redirect_stdout_to_console(self, widget):
        sys.stdout = StdStreamRedirector(
            widget,
            {'auto_scroll': self.is_auto_scroll_enabled, 'tag': 'stdout'},
            {
                'file_path': 'tekkenbotprime.log',
                'save_to_file': self.save_to_file
            },
            self.overlay_manager.write_to_overlay
        )
        sys.stderr = StdStreamRedirector(
            widget,
            {'auto_scroll': self.is_auto_scroll_enabled, 'tag': 'stderr'},
            callback=self.original_stderr.write # TODO disable on build version
        )

    @staticmethod
    def __initialize_console_text():
        sys.stdout.write_file('data/readme.txt')

    def __initialize_memory_override_panel(self):
        self.mop_controller = MemoryOverwritePanelController(
            self.root, self.launcher
        )
        self.view.memory_overwride_panel = self.mop_controller.view
        self.show_memory_override(False)

    def __intialize_overlay_settings(self):
        settings = ReloadableConfigManager().add_config(
            'settings.ini', parse=True
        ).config['DEFAULT']

        default_overlay_enabled = settings.get('overlay_enable')
        default_overlay_mode = OverlayMode[settings.get('overlay_mode')]
        default_overlay_position = OverlayPosition[
            settings.get('overlay_position')
        ]
        default_overlay_theme_index, default_overlay_theme = (
            self.model.get_theme_tuple_by_filename(
                settings.get('overlay_theme')
            )
        )
        self.view.enable_overlay.set(default_overlay_enabled)
        self.view.overlay_mode.set(default_overlay_mode.name)
        self.view.overlay_position.set(default_overlay_position.name)
        self.view.overlay_theme.set(default_overlay_theme_index)

        self.overlay_manager = OverlayManager(
            self.launcher,
            default_overlay_enabled=default_overlay_enabled,
            default_overlay_id=default_overlay_mode.value,
            default_position=default_overlay_position,
            default_theme=default_overlay_theme
        )
