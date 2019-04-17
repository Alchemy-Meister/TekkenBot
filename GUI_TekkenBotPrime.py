from tkinter import *
from tkinter.ttk import *
import GUI_FrameDataOverlay as fdo
import GUI_Overlay as ovr
import GUI_TimelineOverlay as tlo
import GUI_CommandInputOverlay as cio
import GUI_MatchStatOverlay as mso
import GUI_DebugInfoOverlay as dio
import GUI_PunishCoachOverlay as pco
import ConfigReader
from _FrameDataLauncher import FrameDataLauncher
import time
from enum import Enum
import VersionChecker
import webbrowser

class GUI_TekkenBotPrime(Tk):
    def __init__(self):
        self.overlay = None

        Tk.__init__(self)
        self.wm_title("Tekken Bot Prime")
        self.iconbitmap('TekkenData/tekken_bot_close.ico')

        self.color_scheme_config = ConfigReader.ConfigReader("color_scheme")
        self.color_scheme_config.add_comment("colors with names -> http://www.science.smith.edu/dftwiki/images/3/3d/TkInterColorCharts.png")
        self.changed_color_scheme("Current", False)

        self.menu = Menu(self)
        self.configure(menu=self.menu)

        self.text = Text(self, wrap="word")
        self.stdout = sys.stdout
        self.var_print_frame_data_to_file = BooleanVar(value=False)
        sys.stdout = TextRedirector(self.text, sys.stdout, self.write_to_overlay, self.var_print_frame_data_to_file, "stdout")
        self.stderr = sys.stderr
        sys.stderr = TextRedirector(self.text, sys.stderr, self.write_to_error, "stderr")
        self.text.tag_configure("stderr", foreground="#b22222")



        try:
            with open("TekkenData/tekken_bot_readme.txt") as fr:
                lines = fr.readlines()
            for line in lines:
                print(line)
        except:
            print("Error reading readme file.")

        VersionChecker.check_version()

        print("Tekken Bot Starting...")
        self.launcher = FrameDataLauncher(False)

        self.overlay = fdo.GUI_FrameDataOverlay(self, self.launcher)
        #self.graph = tlo.GUI_TimelineOverlay(self, self.launcher)

        self.tekken_bot_menu = Menu(self.menu)
        self.tekken_bot_menu.add_command(label="Restart", command=self.restart)

        self.tekken_bot_menu.add_checkbutton(label="Print Frame Data To \"TekkenData/frame_data_output.txt\"", onvalue=True, offvalue=False, variable=self.var_print_frame_data_to_file)
        self.menu.add_cascade(label="Tekken Bot", menu=self.tekken_bot_menu)


        self.checkbox_dict = {}
        self.column_menu = Menu(self.menu)
        for i, enum in enumerate(fdo.DataColumns):
            bool = self.overlay.redirector.columns_to_print[i]
            self.add_checkbox(self.column_menu, enum, "{} ({})".format(enum.name.replace('X', ' ').strip(), fdo.DataColumnsToMenuNames[enum]), bool, self.changed_columns)
        self.menu.add_cascade(label='Columns', menu=self.column_menu)

        self.display_menu = Menu(self.menu)
        for enum in ovr.DisplaySettings:
            default = self.overlay.tekken_config.get_property(ovr.DisplaySettings.config_name(), enum.name, False)
            self.add_checkbox(self.display_menu, enum, enum.name, default, self.changed_display)
        self.menu.add_cascade(label="Display", menu=self.display_menu)

        self.color_scheme_menu = Menu(self.menu)
        self.scheme_var = StringVar()
        for section in self.color_scheme_config.parser.sections():
            if section not in ("Comments", "Current"):
                self.color_scheme_menu.add_radiobutton(label=section, variable=self.scheme_var, value=section, command=lambda : self.changed_color_scheme(self.scheme_var.get()))
        self.menu.add_cascade(label="Color Scheme", menu=self.color_scheme_menu)

        self.overlay_mode_menu = Menu(self.menu)
        self.overlay_var = StringVar()
        for mode in OverlayMode:
            self.overlay_mode_menu.add_radiobutton(label=OverlayModeToDisplayName[mode], variable=self.overlay_var, value=mode.name, command=lambda : self.changed_mode(self.overlay_var.get()))
        self.menu.add_cascade(label="Mode", menu=self.overlay_mode_menu)
        self.mode = OverlayMode.FrameData

        self.tekken_bot_menu = Menu(self.menu)
        self.tekken_bot_menu.add_command(label=VersionChecker.CURRENT_VERSION)
        self.tekken_bot_menu.add_command(label="Check for new version", command=self.print_release_notes)
        self.tekken_bot_menu.add_command(label="Download Latest Release", command=self.download_latest_release)
        self.menu.add_cascade(label="Version", menu=self.tekken_bot_menu)


        self.text.grid(row = 2, column = 0, columnspan=2, sticky=N+S+E+W)
        #self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        #self.grid_columnconfigure(1, weight=1)

        self.geometry(str(920) + 'x' + str(720))

        self.update_launcher()
        self.overlay.hide()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def print_release_notes(self):
        VersionChecker.check_version(force_print=True)

    def download_latest_release(self):
        webbrowser.open('https://github.com/roguelike2d/TekkenBot/releases/')

    def restart(self):
        self.launcher = FrameDataLauncher(False)
        self.stop_overlay()
        self.start_overlay()

    def write_to_overlay(self, string):
        if self.var_print_frame_data_to_file.get() and 'NOW:' in string:
            with open("TekkenData/frame_data_output.txt", 'a') as fa:
                fa.write(string +'\n')
        if self.overlay != None:
            self.overlay.redirector.write(string)
        #if 'HIT' in string:
            #self.graph.redirector.write(string)

    def write_to_error(self, string):
        self.stderr.write(string)

    def add_checkbox(self, menu, lookup_key, display_string, default_value, button_command):
        var = BooleanVar()
        var.set(default_value)
        self.checkbox_dict[lookup_key] = var
        menu.add_checkbutton(label=display_string, onvalue=True, offvalue=False, variable=var, command = button_command)

    def changed_color_scheme(self, section, do_reboot=True):
        for enum in fdo.ColorSchemeEnum:
            fdo.CurrentColorScheme.dict[enum] = self.color_scheme_config.get_property(section, enum.name, fdo.CurrentColorScheme.dict[enum])
            self.color_scheme_config.set_property("Current", enum.name, fdo.CurrentColorScheme.dict[enum])
        self.color_scheme_config.write()
        if do_reboot:
            self.reboot_overlay()

    def changed_mode(self, mode):

        self.stop_overlay()

        self.mode = OverlayMode[mode]

        if self.mode != OverlayMode.Off:
            self.start_overlay()



    def changed_columns(self):
        generated_columns = []
        for enum in fdo.DataColumns:
            var = self.checkbox_dict[enum]
            generated_columns.append(var.get())
            if self.mode == OverlayMode.FrameData:
                self.overlay.update_column_to_print(enum, var.get())
        if self.mode == OverlayMode.FrameData:
            self.overlay.set_columns_to_print(generated_columns)

    def changed_display(self):
        for enum in ovr.DisplaySettings:
            var = self.checkbox_dict[enum]
            if self.overlay != None:
                self.overlay.tekken_config.set_property(ovr.DisplaySettings.config_name(), enum.name, var.get())
        if self.overlay != None:
            self.overlay.tekken_config.write()
        self.reboot_overlay()

    def stop_overlay(self):
        if self.overlay != None:
            self.overlay.toplevel.destroy()
        self.overlay = None

    def start_overlay(self):
        if self.mode == OverlayMode.FrameData:
            self.overlay = fdo.GUI_FrameDataOverlay(self, self.launcher)
            self.overlay.hide()
        #if self.mode == OverlayMode.Timeline:
        #    self.overlay = tlo.GUI_TimelineOverlay(self, self.launcher)
        #    self.overlay.hide()
        if self.mode == OverlayMode.CommandInput:
            self.overlay = cio.GUI_CommandInputOverlay(self, self.launcher)
            self.overlay.hide()
        if self.mode == OverlayMode.PunishCoach:
            self.overlay = pco.GUI_PunishCoachOverlay(self, self.launcher)
            self.overlay.hide()
        if self.mode == OverlayMode.MatchupRecord:
            self.overlay = mso.GUI_MatchStatOverlay(self, self.launcher)
            self.overlay.hide()
        if self.mode == OverlayMode.DebugInfo:
            self.overlay = dio.GUI_DebugInfoOverlay(self, self.launcher)
            self.overlay.hide()




    def reboot_overlay(self):
        self.stop_overlay()
        self.start_overlay()

    def update_launcher(self):
        time1 = time.time()
        successful_update = self.launcher.Update()

        if self.overlay != None:
            self.overlay.update_location()
            if successful_update:
                self.overlay.update_state()
        #self.graph.update_state()
        time2 = time.time()
        elapsed_time = 1000 * (time2 - time1)
        if self.launcher.gameState.game_reader.is_pid_valid():
            self.after(max(2, 8 - int(round(elapsed_time))), self.update_launcher)
        else:
            self.after(1000, self.update_launcher)

    def on_closing(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        self.destroy()



class TextRedirector(object):
    def __init__(self, widget, stdout, callback_function, var_print_frame_data_to_file,tag="stdout"):
        self.widget = widget
        self.stdout = stdout
        self.tag = tag
        self.callback_function = callback_function
        self.var_print_frame_data_to_file = var_print_frame_data_to_file

    def write(self, str):

        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see('end')
        self.callback_function(str)

    def flush(self):
        pass

class OverlayMode(Enum):
    Off = 0
    FrameData = 1
    #Timeline = 2
    CommandInput = 3
    PunishCoach = 4
    MatchupRecord = 5
    DebugInfo = 6

OverlayModeToDisplayName = {
    OverlayMode.Off : 'Off',
    OverlayMode.FrameData: 'Frame Data',
    OverlayMode.CommandInput: 'Command Inputs (and cancel window)',
    OverlayMode.PunishCoach: 'Punish Alarm (loud!)',
    OverlayMode.MatchupRecord: 'Matchup Stats',
    OverlayMode.DebugInfo: 'Debugging Variables',
}

if __name__ == '__main__':
    app = GUI_TekkenBotPrime()
    #app.update_launcher()
    app.mainloop()
