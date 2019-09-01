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
from tkinter import messagebox

from audio import PunishCoachAlarm
from constants.overlay import OverlayMode, OverlayPosition
from config import DefaultSettings, ReloadableConfigManager
from gui.model import OverlayModel
from gui.my_tkinter import StdStreamRedirector
from gui.my_tkinter.overlay import OverlayManager
from gui.view import TekkenBotPrimeView

from network import NoInternetConnectionError

from tekken.coach import PunishCoach
from tekken.launcher import Launcher

from .memory_override_panel_controller import MemoryOverwritePanelController

class TekkenBotPrimeController():
    """
    """
    def __init__(self, updater, title=None, icon=None):
        self.updater = updater
        self.title = title

        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        self.root = tk.Tk()
        self.config_manager = ReloadableConfigManager()
        self.reloadable_initial_settings = None
        self.model = OverlayModel()

        self.save_to_file = True
        self.is_auto_scroll_enabled = True

        self.root.title(self.title)
        self.root.iconbitmap(icon)
        self.root.geometry('{}x{}'.format(920, 720))
        self.root.protocol('WM_DELETE_WINDOW', self.__on_delete_window)

        self.updater.gui_container = self.root

        self.view = TekkenBotPrimeView(self.root, self)

        self.__redirect_stdout_to_console(self.view.console)

        self.launcher = None
        self.overlay_manager = None
        self.mop_controller = None
        self.punish_coach_alarm = None

        self.__initialize_console_text()
        self.root.mainloop()

    def check_for_updates(self):
        try:
            self.updater.is_update_available(
                use_cache=False,
                success_callback=self.__on_update_check_success,
                error_callback=self.__on_no_internet_connection,
                run_async=True
            )
        except NoInternetConnectionError:
            self.__on_no_internet_connection()

    def enable_save_to_file(self, enable):
        sys.stdout.enable_save_to_file(enable)
        sys.stderr.enable_save_to_file(enable)

    def enable_auto_scroll(self, enable):
        sys.stdout.enable_auto_scroll(enable)
        sys.stderr.enable_auto_scroll(enable)

    def enable_overlay(self, enable):
        self.overlay_manager.enable_overlay(enable)

    def enable_overlay_auto_hide(self, enable):
        self.overlay_manager.enable_automatic_overlay_hide(enable)

    def enable_punish_alarm(self, enable):
        self.punish_coach_alarm.enable(enable)

    def is_save_to_file_enabled(self):
        return self.save_to_file

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

    def populate_overlay_modes_submenu(self):
        return self.model.all_overlay_modes

    def populate_overlay_positions_submenu(self):
        return self.model.all_overlay_positions

    def populate_overlay_themes_submenu(self):
        return enumerate(self.model.get_overlay_themes_names())

    def restart(self):
        sys.stdout.write('restart')
        self.config_manager.reload_all()
        self.model.reload()
        self.view.load_overlay_themes(
            enumerate(self.model.get_overlay_themes_names())
        )
        self.__update_alarm_gui_settings()
        self.__update_overlay_gui_settings()
        self.punish_coach_alarm.reload()
        self.overlay_manager.reload()

    def show_memory_override(self, enable):
        self.view.show_memory_overwrite_panel(enable)

    def __initialize_console_text(self):
        sys.stdout.write_file(
            'data/readme.txt',
            callback=self.__post_console_initialization
        )

    def __initialize_memory_override_panel(self):
        self.mop_controller = MemoryOverwritePanelController(
            self.root, self.launcher
        )
        self.view.memory_overwride_panel = self.mop_controller.view
        self.show_memory_override(False)

    def __initialize_overlay_settings(self):
        self.__update_overlay_gui_settings()
        self.overlay_manager = OverlayManager(
            self.launcher,
            initial_settings=self.reloadable_initial_settings
        )

    def __initialize_punish_alarm(self):
        self.__update_alarm_gui_settings()
        self.punish_coach_alarm = PunishCoachAlarm(
            PunishCoach(self.launcher), self.reloadable_initial_settings
        )

    def __on_delete_window(self):
        sys.stdout.close()
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        self.root.destroy()

    def __on_no_internet_connection(self):
        messagebox.showerror(
            self.title, 'Unable to connect to the Internet.'
        )

    def __on_update_check_success(self, available):
        if available:
            if messagebox.askyesno(
                    self.title,
                    '{0} {1}'.format(
                        'A new version of Tekken Bot Prime is available.',
                        'Would you like to download it now?'
                    )
            ):
                self.updater.download_update(use_cache=True)
        else:
            messagebox.showinfo(
                self.title, 'There are currently no updates available.'
            )

    def __post_console_initialization(self):
        self.launcher = Launcher(self.root, extended_print=False)
        self.reloadable_initial_settings = self.config_manager.add_config(
            'settings.ini', parse=True, config_model_class=DefaultSettings
        )
        self.__initialize_overlay_settings()
        self.__initialize_punish_alarm()

        self.__initialize_memory_override_panel()

        self.root.after(1, self.root.focus_force())
        self.launcher.start()

    def __redirect_stdout_to_console(self, widget):
        sys.stdout = StdStreamRedirector(
            widget,
            {'auto_scroll': self.is_auto_scroll_enabled, 'tag': 'stdout'},
            {
                'file_path': 'tekkenbotprime.log',
                'save_to_file': self.save_to_file,
                'write_mode': 'w'
            },
            callback=self.original_stdout.write
        )
        sys.stderr = StdStreamRedirector(
            widget,
            {'auto_scroll': self.is_auto_scroll_enabled, 'tag': 'stderr'},
            {
                'file_path': 'tekkenbotprime.log',
                'save_to_file': self.save_to_file,
                'write_mode': 'a'
            },
            callback=self.original_stderr.write
        )

    def __update_alarm_gui_settings(self):
        self.view.enable_punish_alarm.set(
            self.reloadable_initial_settings.config['DEFAULT'].get(
                'alarm_enable'
            )
        )

    def __update_overlay_gui_settings(self):
        initial_settings = self.reloadable_initial_settings.config['DEFAULT']

        self.view.enable_overlay.set(initial_settings.get('overlay_enable'))
        self.view.overlay_auto_hide.set(
            initial_settings.get('overlay_automatic_hide')
        )
        self.view.overlay_mode.set(
            OverlayMode[initial_settings.get('overlay_mode')].name
        )
        self.view.overlay_position.set(
            OverlayPosition[initial_settings.get('overlay_position')].name
        )
        self.view.overlay_theme.set(
            self.model.get_index_by_filename(
                initial_settings.get('overlay_theme')
            )
        )
