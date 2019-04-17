import GUI_Overlay
from tkinter import *
from tkinter.ttk import *
from GUI_Overlay import CurrentColorScheme, ColorSchemeEnum


class TextRedirector(object):
    def __init__(self, text):
        self.text = text
        self.text.tag_configure("center", justify="center")


    def write(self, str):
        if '!RECORD' in str:
            self.text.configure(state="normal")
            self.text.insert("1.0", '\n')
            self.text.insert("1.0", str.split('|')[1], ("center",))
            self.text.delete("4.0", "end")
            self.text.configure(state="disabled")
            self.text.see('0.0')


class GUI_MatchStatOverlay(GUI_Overlay.Overlay):
    def __init__(self, master, launcher):

        GUI_Overlay.Overlay.__init__(self, master, (600, 70), "Tekken Bot: Match Stats Overlay")

        #self.launcher = FrameDataLauncher(self.enable_nerd_data)
        self.launcher = launcher

        Grid.columnconfigure(self.toplevel, 0, weight=1)
        Grid.rowconfigure(self.toplevel, 0, weight=1)

        self.text = self.create_textbox()

        self.redirector = TextRedirector(self.text)

        if not self.launcher.gameState.game_reader.reacquire_names:
            for record in self.launcher.cyclopedia_p1.get_matchup_record(self.launcher.gameState):
                self.redirector.write(record)


    def create_textbox(self):
        textbox = Text(self.toplevel, width = 35, font=("Consolas, 14"), wrap=NONE, highlightthickness=0, pady=0, relief='flat')
        textbox.grid(row=0, column=0, sticky=N + S + W + E)
        textbox.configure(background=self.background_color)
        textbox.configure(foreground=CurrentColorScheme.dict[ColorSchemeEnum.system_text])
        return textbox