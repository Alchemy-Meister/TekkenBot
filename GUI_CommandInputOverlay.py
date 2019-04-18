import GUI_Overlay
from tkinter import *
from tkinter.ttk import *
from MoveInfoEnums import InputDirectionCodes
from MoveInfoEnums import InputAttackCodes



class TextRedirector(object):
    def __init__(self, canvas, height):
        pass

    def write(self, str):
        pass


class GUI_CommandInputOverlay(GUI_Overlay.Overlay):

    symbol_map = {

        #InputDirectionCodes.u: '⇑',
        #InputDirectionCodes.uf: '⇗',
        #InputDirectionCodes.f: '⇒',
        #InputDirectionCodes.df: '⇘',
        #InputDirectionCodes.d: '⇓',
        #InputDirectionCodes.db: '⇙',
        #InputDirectionCodes.b: '⇐',
        #InputDirectionCodes.ub: '⇖',
        #InputDirectionCodes.N: '★',

        InputDirectionCodes.u : '↑',
        InputDirectionCodes.uf: '↗',
        InputDirectionCodes.f: '→',
        InputDirectionCodes.df: '↘',
        InputDirectionCodes.d: '↓',
        InputDirectionCodes.db: '↙',
        InputDirectionCodes.b: '←',
        InputDirectionCodes.ub: '↖',
        InputDirectionCodes.N: '★',
        InputDirectionCodes.NULL: '!'

    }


    def __init__(self, master, launcher):


        GUI_Overlay.Overlay.__init__(self, master, (1200, 86), "Tekken Bot: Command Input Overlay")

        self.launcher = launcher

        self.canvas = Canvas(self.toplevel, width=self.w, height=self.h, bg='black', highlightthickness=0, relief='flat')

        self.canvas.pack()

        self.length = 60
        self.step = self.w/self.length
        for i in range(self.length):
            self.canvas.create_text(i * self.step + (self.step / 2), 8, text = str(i), fill='snow')
            self.canvas.create_line(i * self.step, 0, i * self.step, self.h, fill="red")

        self.canvas

        self.redirector = TextRedirector(self.canvas, self.h)\

        self.stored_inputs = []
        self.stored_cancels = []


    def update_state(self):
        GUI_Overlay.Overlay.update_state(self)
        if self.launcher.gameState.state_log[-1].is_player_player_one:
            input = self.launcher.gameState.state_log[-1].bot.get_input_state()
            cancelable = self.launcher.gameState.state_log[-1].bot.is_cancelable
            bufferable = self.launcher.gameState.state_log[-1].bot.is_bufferable
            parry1 = self.launcher.gameState.state_log[-1].bot.is_parry1
            parry2 = self.launcher.gameState.state_log[-1].bot.is_parry2
        else:
            input = self.launcher.gameState.state_log[-1].opp.get_input_state()
            cancelable = self.launcher.gameState.state_log[-1].opp.is_cancelable
            bufferable = self.launcher.gameState.state_log[-1].opp.is_bufferable
            parry1 = self.launcher.gameState.state_log[-1].opp.is_parry1
            parry2 = self.launcher.gameState.state_log[-1].opp.is_parry2
        frame_count = self.launcher.gameState.state_log[-1].frame_count
        #print(input)
        self.update_input(input, self.color_from_cancel_booleans(cancelable, bufferable, parry1, parry2))

    def color_from_cancel_booleans(self, cancelable, bufferable, parry1, parry2):
        if parry1:
            fill_color = 'orange'
        elif parry2:
            fill_color = 'yellow'
        elif bufferable:
            fill_color = 'MediumOrchid1'
        elif cancelable:
            fill_color = 'SteelBlue1'
        else:
            fill_color = 'firebrick1'
        return fill_color

    def update_input(self, input, cancel_color):
        input_tag = "inputs"
        self.stored_inputs.append(input)
        self.stored_cancels.append(cancel_color)
        if len(self.stored_inputs) >= self.length:
            self.stored_inputs = self.stored_inputs[-self.length:]
            self.stored_cancels = self.stored_cancels[-self.length:]
            if input != self.stored_inputs[-2]:
                self.canvas.delete(input_tag)

                #print(self.stored_inputs)
                for i, (direction_code, attack_code, rage_flag) in enumerate(self.stored_inputs):
                    self.canvas.create_text(i * self.step + (self.step / 2), 30, text=GUI_CommandInputOverlay.symbol_map[direction_code], fill='snow',  font=("Consolas", 20), tag=input_tag)
                    self.canvas.create_text(i * self.step + (self.step / 2), 55, text=attack_code.name.replace('x', '').replace('N', ''), fill='snow',  font=("Consolas", 12), tag=input_tag)
                    x0 = i * self.step + 4
                    x1 = x0 + self.step - 8
                    self.canvas.create_rectangle(x0, 70, x1, self.h - 5, fill=self.stored_cancels[i], tag=input_tag)








