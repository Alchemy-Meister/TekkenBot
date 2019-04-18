import GUI_Overlay
from tkinter import *
from tkinter.ttk import *
from GUI_Overlay import CurrentColorScheme, ColorSchemeEnum


class TextRedirector(object):
    def __init__(self, text):
        pass


    def write(self, str):
        pass

class GUI_DebugInfoOverlay(GUI_Overlay.Overlay):
    def __init__(self, master, launcher):

        GUI_Overlay.Overlay.__init__(self, master, (1200, 120), "Tekken Bot: Match Stats Overlay")

        #self.launcher = FrameDataLauncher(self.enable_nerd_data)
        self.launcher = launcher

        Grid.columnconfigure(self.toplevel, 0, weight=1)
        Grid.rowconfigure(self.toplevel, 0, weight=1)

        self.canvas = Canvas(self.toplevel, width=self.w, height=self.h, bg='black', highlightthickness=0, relief='flat')
        self.canvas.configure(background=self.background_color)
        self.canvas.pack()

        self.textbox_width = 10

        self.textbox_names = [
            'p1_tracking',
            'p1_???',
            'p1_movename',
            'p1_moveindex',
            'p1_stun_state',
            'p2_stun_state',

            'p2_moveindex',
            'p2_movename',
            'p2_???',
            'p2_tracking',


        ]

        for i in range(self.textbox_width):
            Grid.columnconfigure(self.canvas, i, weight=1)

        self.textboxes = []
        self.textboxes_last_inputs = [None] * self.textbox_width
        for i in range(self.textbox_width):
            self.textboxes.append(self.create_textbox(self.canvas, i))
            self.write_to_textbox(i, str(self.textbox_names[i]))

        self.redirector = TextRedirector(None)
        self.prev_move_id = 0



    def create_textbox(self, master, col):
        textbox = Text(master, font=("Consolas, 10"), wrap=NONE, highlightthickness=0, pady=0, relief='flat')
        textbox.grid(row=0, column=col, sticky=N + S + W + E)
        textbox.configure(background=self.background_color)
        textbox.configure(foreground=CurrentColorScheme.dict[ColorSchemeEnum.system_text])
        return textbox

    def write_to_textbox(self, textbox_index, out):
        if out != self.textboxes_last_inputs[textbox_index]:
            self.textboxes_last_inputs[textbox_index] = out
            textbox = self.textboxes[textbox_index]
            textbox.configure(state="normal")
            textbox.insert("end", out + '\n')
            lines = int(textbox.index('end-1c').split('.')[0])
            max_lines = 8
            if lines > max_lines:
                textbox.delete("2.0", '3.0')
            textbox.configure(state="disabled")
            textbox.see('end')

    def update_state(self):
        gameState = self.launcher.gameState

        self.canvas.delete("debug")
        if len(gameState.state_log) > 1:
            self.draw_debug_info_for_bot(gameState.state_log[-1].bot, gameState.get_current_bot_move_name(), 10, W, True)
            self.draw_debug_info_for_bot(gameState.state_log[-1].opp, gameState.get_current_opp_move_name(), self.w - 10, E, False)

        move_id = gameState.state_log[-1].opp.move_id
        if self.prev_move_id != move_id:
            self.prev_move_id = move_id
            #gameState.state_log[-1].opp.movelist_parser.print_can_be_done_from_neutral(move_id)
            #gameState.state_log[-1].opp.movelist_parser.print_input_for_move(move_id)
            #if move_id < 30000:
                #gameState.state_log[-1].opp.movelist_parser.print_nodes(move_id)


    def draw_debug_info_for_bot(self, bot, move_name, x, anchor, left_or_right):
        debug_tag = 'debug'
        tracking_state = bot.complex_state
        simple_state = bot.simple_state
        stun_state = bot.stun_state
        #font_color = CurrentColorScheme.dict[ColorSchemeEnum.system_text]
        #self.canvas.create_text(x, 10, text=tracking_state.name, fill=font_color, font=("Consolas", 12), anchor=anchor, tag=debug_tag)
        #self.canvas.create_text(x, 40, text=simple_state.name, fill=font_color, font=("Consolas", 12), anchor=anchor, tag=debug_tag)
        #self.canvas.create_text(x, 70, text=move_name, fill=font_color, font=("Consolas", 12), anchor=anchor, tag=debug_tag)
        if left_or_right:
            index = 0
            iterate = 1
        else:
            index = self.textbox_width - 1
            iterate = -1
        self.write_to_textbox(index, tracking_state.name)
        self.write_to_textbox(index + iterate, simple_state.name)
        self.write_to_textbox(index + 2 * iterate, move_name)
        self.write_to_textbox(index + 3 * iterate, str('0x{:x}'.format(bot.move_id)))
        self.write_to_textbox(index + 4 * iterate, stun_state.name)

