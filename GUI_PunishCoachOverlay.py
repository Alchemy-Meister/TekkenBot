import GUI_Overlay
from tkinter import *
from tkinter.ttk import *
from TekkenEncyclopedia import PunishWindow
import SoundPlayer

class TextRedirector(object):
    def __init__(self, canvas, height):
        pass

    def write(self, str):
        pass


class GUI_PunishCoachOverlay(GUI_Overlay.Overlay):

    def __init__(self, master, launcher):


        GUI_Overlay.Overlay.__init__(self, master, (1200, 86), "Tekken Bot: Punish Coach Overlay")

        self.launcher = launcher

        self.canvas = Canvas(self.toplevel, width=self.w, height=self.h, bg='black', highlightthickness=0, relief='flat')

        self.canvas.pack()

        self.redirector = TextRedirector(self.canvas, self.h)

        self.stored_inputs = []
        self.stored_cancels = []

        self.current_window = None
        self.frames_since_new_window = 9999
        self.has_played_sound = False

        self.coach_tag = 'coach'
        self.border_tag = 'border'


    def update_state(self):
        GUI_Overlay.Overlay.update_state(self)
        if self.launcher.gameState.state_log[-1].is_player_player_one:
            cyclopedia = self.launcher.cyclopedia_p2
        else:
            cyclopedia = self.launcher.cyclopedia_p1

        #cyclopedia = self.launcher.cyclopedia_p1



        last_punish_window = None
        for punish_window in reversed(cyclopedia.PunishWindows):
            if not punish_window.result in (PunishWindow.Result.NOT_YET_CLOSED, ):
                last_punish_window = punish_window
                break

        if self.current_window != last_punish_window:

            self.current_window = last_punish_window
            self.frames_since_new_window = 0
            self.has_played_sound = False
            frame_advantage = self.current_window.get_frame_advantage()
            if frame_advantage >= 0:
                frame_advantage = '+' + str(frame_advantage)

            self.canvas.delete(self.coach_tag)
            self.canvas.create_text(self.w/2, 40, text = self.current_window.name, font=("Consolas", 30), fill='snow', tag=self.coach_tag)
            self.canvas.create_text(self.w / 4, 40, text=frame_advantage, font=("Consolas", 44), fill='snow', tag=self.coach_tag)
            self.canvas.create_text(self.w * 3 / 4, 40, text=frame_advantage, font=("Consolas", 44), fill='snow', tag=self.coach_tag)

            self.set_canvas_border_to_punish_indicator()


        else:
            self.frames_since_new_window += 1
            if self.frames_since_new_window < 60 and self.frames_since_new_window % 6 == 0:
                if not self.current_window.result in (PunishWindow.Result.JAB_ON_NOT_LAUNCHABLE, PunishWindow.Result.LAUNCH_ON_LAUNCHABLE, PunishWindow.Result.NO_WINDOW):
                    if self.frames_since_new_window % 12 == 0:
                        self.set_canvas_border_to_punish_indicator()
                    else:
                        self.set_canvas_border_to_flash()
                        if not self.has_played_sound:
                            self.play_sound_by_punish()
                            self.has_played_sound = True


    def set_canvas_border_to_punish_indicator(self):
        self.canvas.delete(self.border_tag)
        self.set_canvas_border_colors(self.get_canvas_border_color_by_punish(), 'firebrick1')

    def get_canvas_border_color_by_punish(self):
        if self.current_window.result == PunishWindow.Result.NO_PUNISH:
            if self.current_window.get_frame_advantage() > -14:
               return 'orchid1'
            else:
                return 'DeepPink2'
        if self.current_window.result in (PunishWindow.Result.JAB_ON_NOT_LAUNCHABLE, PunishWindow.Result.LAUNCH_ON_LAUNCHABLE):
            return 'SteelBlue1'
        if self.current_window.result in (PunishWindow.Result.NO_LAUNCH_ON_LAUNCHABLE,):
            return 'gold2'

    def play_sound_by_punish(self):
        if self.current_window.result == PunishWindow.Result.NO_PUNISH:
            # if self.current_window.get_frame_advantage() > -14:
            #     SoundPlayer.SoundPlayer.play_no_jab_punish()
            # else:
            #     SoundPlayer.SoundPlayer.play_no_launch_punish()
            if self.current_window.get_frame_advantage() == -10: # No switch in python QQ
                SoundPlayer.SoundPlayer.play_minus_10()
            elif self.current_window.get_frame_advantage() == -11:
                SoundPlayer.SoundPlayer.play_minus_11()
            elif self.current_window.get_frame_advantage() == -12:
                SoundPlayer.SoundPlayer.play_minus_12()
            elif self.current_window.get_frame_advantage() == -13:
                SoundPlayer.SoundPlayer.play_minus_13()
            elif self.current_window.get_frame_advantage() == -14:
                SoundPlayer.SoundPlayer.play_minus_14()
            elif self.current_window.get_frame_advantage() == -15:
                SoundPlayer.SoundPlayer.play_minus_15()
            elif self.current_window.get_frame_advantage() == -16:
                SoundPlayer.SoundPlayer.play_minus_16()
            else:
                SoundPlayer.SoundPlayer.play_no_launch_punish()



        if self.current_window.result in (PunishWindow.Result.JAB_ON_NOT_LAUNCHABLE, PunishWindow.Result.LAUNCH_ON_LAUNCHABLE):
            pass

        if self.current_window.result in (PunishWindow.Result.NO_LAUNCH_ON_LAUNCHABLE,):
            SoundPlayer.SoundPlayer.play_no_launch_punish()


    def set_canvas_border_colors(self, color1, color2):
        self.canvas.create_rectangle(0, 0, self.w, self.h, width=10, outline=color1, tag=self.border_tag)
        self.canvas.create_rectangle(10, 10, self.w - 10, self.h - 10, width=5, outline=color2, tag=self.border_tag)

    def set_canvas_border_to_flash(self):
        self.canvas.delete(self.border_tag)
        self.set_canvas_border_colors('snow', self.get_canvas_border_color_by_punish())



