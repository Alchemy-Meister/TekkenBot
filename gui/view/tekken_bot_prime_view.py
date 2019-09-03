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

import tkinter as tk
import tkinter.scrolledtext as tkst

class TekkenBotPrimeView():
    """
    """
    def __init__(self, root, controller):
        self.controller = controller
        self.menu_bar = tk.Menu(root)

        tekken_bot_menu = tk.Menu(self.menu_bar, tearoff=0)
        tekken_bot_menu.add_command(
            label='Restart', command=self.controller.restart
        )

        preferences_submenu = tk.Menu(tekken_bot_menu, tearoff=0)
        is_save_to_file_enabled = tk.BooleanVar(
            value=self.controller.is_save_to_file_enabled()
        )
        preferences_submenu.add_checkbutton(
            label='Save Log',
            onvalue=True, offvalue=False,
            variable=is_save_to_file_enabled,
            command=lambda: self.controller.enable_save_to_file(
                is_save_to_file_enabled.get()
            )
        )
        is_auto_scroll_enabled = tk.BooleanVar(value=True)
        preferences_submenu.add_checkbutton(
            label='Scroll on Output',
            onvalue=True, offvalue=False,
            variable=is_auto_scroll_enabled,
            command=lambda: self.controller.enable_auto_scroll(
                is_auto_scroll_enabled.get()
            )
        )

        # TODO change command
        preferences_submenu.add_command(label='Settings', command=None)

        tekken_bot_menu.add_cascade(
            label='Preferences', menu=preferences_submenu
        )

        is_memory_overwrite_panel_visible = tk.BooleanVar()
        view = tk.Menu(self.menu_bar, tearoff=0)
        view.add_checkbutton(
            label='Toggle Memory Overwrite',
            variable=is_memory_overwrite_panel_visible,
            command=lambda: self.controller.show_memory_override(
                is_memory_overwrite_panel_visible.get()
            )
        )

        punish_alarm_menu = tk.Menu(self.menu_bar, tearoff=0)

        self.enable_punish_alarm = tk.BooleanVar(value=False)
        punish_alarm_menu.add_checkbutton(
            label='Enable',
            variable=self.enable_punish_alarm,
            command=lambda: self.controller.enable_punish_alarm(
                self.enable_punish_alarm.get()
            )
        )

        self.overlay_menu = tk.Menu(self.menu_bar, tearoff=0)

        self.enable_overlay = tk.BooleanVar(value=False)
        self.overlay_menu.add_checkbutton(
            label='Enable',
            variable=self.enable_overlay,
            command=lambda: self.controller.enable_overlay(
                self.enable_overlay.get()
            )
        )

        self.overlay_auto_hide = tk.BooleanVar(value=False)
        self.overlay_menu.add_checkbutton(
            label='Auto-hide',
            variable=self.overlay_auto_hide,
            command=lambda: self.controller.enable_overlay_auto_hide(
                self.overlay_auto_hide.get()
            )
        )

        # self.overlay_layout = tk.StringVar()
        # overlay_layout_submenu = TekkenBotPrimeView.__create_populated_menu(
        #     root,
        #     self.overlay_layout,
        #     self.controller.populate_overlay_layouts_submenu(),
        #     self.controller.overlay_layout_change
        # )

        self.overlay_mode = tk.StringVar()
        overlay_mode_submenu = TekkenBotPrimeView.__create_populated_menu(
            root,
            self.overlay_mode,
            self.controller.populate_overlay_modes_submenu(),
            self.controller.overlay_mode_change
        )

        self.overlay_position = tk.StringVar()
        self.overlay_position_submenu = (
            TekkenBotPrimeView.__create_populated_menu(
                root,
                self.overlay_position,
                self.controller.populate_overlay_positions_submenu(),
                self.controller.overlay_position_change
            )
        )

        # self.overlay_menu.add_cascade(
        #     label='Layout', menu=overlay_layout_submenu
        # )
        self.overlay_menu.add_cascade(label='Mode', menu=overlay_mode_submenu)
        self.overlay_menu.add_cascade(
            label='Position', menu=self.overlay_position_submenu
        )

        self.overlay_theme = tk.IntVar()
        self.load_overlay_themes(
            self.controller.populate_overlay_themes_submenu()
        )

        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(
            label='Check for Updates...',
            command=self.controller.check_for_updates
        )

        self.menu_bar.add_cascade(label='Tekken Bot', menu=tekken_bot_menu)
        self.menu_bar.add_cascade(label='View', menu=view)
        self.menu_bar.add_cascade(label='Punish Alarm', menu=punish_alarm_menu)
        self.menu_bar.add_cascade(label='Overlay', menu=self.overlay_menu)
        self.menu_bar.add_cascade(label='Help', menu=help_menu)

        root.config(menu=self.menu_bar)

        self.memory_overwride_panel = None

        self.console = tkst.ScrolledText(root, state='disabled')
        self.console.grid(column=0, row=1, sticky='NSEW')

        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

    def enable_overlay_position(self, str_position, enable):
        self.overlay_position_submenu.entryconfig(
            str_position, state='normal' if enable else 'disabled'
        )

    def load_overlay_themes(self, theme_enumaration):
        try:
            overlay_theme_index = self.overlay_menu.index('Theme')
            self.overlay_menu.delete(overlay_theme_index)
        except tk.TclError:
            pass
        overlay_theme_submenu = TekkenBotPrimeView.__create_populated_menu(
            self.menu_bar,
            self.overlay_theme,
            theme_enumaration,
            self.controller.overlay_theme_change
        )
        self.overlay_menu.add_cascade(label='Theme', menu=overlay_theme_submenu)

    def show_memory_overwrite_panel(self, show):
        if self.memory_overwride_panel:
            if show:
                self.memory_overwride_panel.grid(column=0, row=0)
            else:
                self.memory_overwride_panel.grid_remove()

    @staticmethod
    def __create_populated_menu(root, variable, menu_list, callback):
        menu = tk.Menu(master=root, tearoff=0)
        for value, label in menu_list:
            menu.add_radiobutton(
                label=label,
                variable=variable,
                value=value,
                command=lambda: callback(variable.get())
            )
        return menu
