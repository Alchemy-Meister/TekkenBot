from tkinter import *
from tkinter.ttk import *
import time
from datetime import date
from MatchRecorder import MatchRecorder
from tekken_game_state import TekkenGameState

from GameInputter import *
from BasicCommands import *
from NotationParser import *

class BotRecorder():
    def __init__(self):
        self.toplevel = Tk()
        self.recorder = MatchRecorder()
        self.game_state = TekkenGameState()

        self.playback_going = False
        self.is_recording = False #set this to true to record some matches
        self.is_playback_mode = True




    def update_launcher(self):

        time1 = time.time()

        buffer = 4


        successful = self.game_state.Update(buffer)
        if successful and self.game_state.IsGameHappening():


            if self.game_state.WasTimerReset():
                print("timer reset")
                if self.is_recording:
                    self.recorder.PrintInputLog()
                self.playback_going = False

            if self.game_state.DidTimerStartTicking(buffer + 60):
                self.playback("2017_Jul_20_22.15.36S_ALISAvKING")
                print("ticking begins")
                if self.is_recording:
                    self.recorder = MatchRecorder()
                self.playback_going = True

            if len(self.game_state.stateLog) > 2:
                self.recorder.Update(self.game_state)

            if self.playback_going and self.is_playback_mode:
                self.p1_controller.Update(self.game_state.is_tekken_foreground_wnd(), self.game_state.IsBotOnLeft())
                self.p2_controller.Update(self.game_state.is_tekken_foreground_wnd(), not self.game_state.IsBotOnLeft())

                self.p1_bot.Update(self.game_state)
                self.p2_bot.Update(self.game_state)

        time2 = time.time()
        elapsed_time = 1000 * (time2 - time1)
        self.toplevel.after(max(2, 8 - int(round(elapsed_time))), self.update_launcher)




    def playback(self, filename):
        p1_controller = GameControllerInputter(False)
        p2_controller = GameControllerInputter(True)

        p1_bot = BotCommands(p1_controller, True)
        p2_bot = BotCommands(p2_controller, True)

        with open("TekkenData/Replays/" + filename) as fr:
            p1_commands = fr.readline().strip()
            p2_commands = fr.readline().strip()

        p1_bot.AddCommand([(Command.ReleaseAll, 0), (Command.Wait, 1)] + ParseMoveList(p1_commands) + [(Command.ReleaseAll, 1)])
        p2_bot.AddCommand([(Command.ReleaseAll, 0), (Command.Wait, 1)] + ParseMoveList(p2_commands) + [(Command.ReleaseAll, 1)])

        self.p1_controller = p1_controller
        self.p2_controller = p2_controller

        self.p1_bot = p1_bot
        self.p2_bot = p2_bot




if __name__ == '__main__':
    app = BotRecorder()
    app.update_launcher()
    app.toplevel.mainloop()