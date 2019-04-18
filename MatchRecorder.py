
from tekken_game_state import TekkenGameState
from ButtonCommandEnum import Command
from MoveInfoEnums import InputDirectionCodes
from MoveInfoEnums import InputAttackCodes
import time

class MatchRecorder:
    NOTATION = {
        Command.HoldForward : 'F',
        Command.HoldBack: 'B',
        Command.HoldDown: 'D',
        Command.HoldUp: 'U',

        Command.Hold1: '+1*',
        Command.Hold2: '+2*',
        Command.Hold3: '+3*',
        Command.Hold4: '+4*',

        Command.ReleaseForward: '-F',
        Command.ReleaseBack: '-B',
        Command.ReleaseDown: '-D',
        Command.ReleaseUp: '-U',

        Command.Release1: '+1-',
        Command.Release2: '+2-',
        Command.Release3: '+3-',
        Command.Release4: '+4-',

        Command.HoldRage: 'R',
        Command.ReleaseRage: '=R',
    }

    def __init__(self):
        self.input_log = []
        self.p1_name = "UNKNOWN"
        self.p2_name = "UNKNOWN"


    def Update(self, gameState:TekkenGameState):
        self.p1_name = gameState.GetBotName()
        self.p2_name = gameState.GetOppName()

        bot_input = gameState.GetBotInputState()
        opp_input = gameState.GetOppInputState()
        #self.input_log.append(bot_input[0].name + "," + bot_input[1].name + "|" + opp_input[0].name + "," + opp_input[1].name)
        self.input_log.append((bot_input, opp_input))

    def GetInputAsCommands(self, index):
        commands = []
        previous_input = [(InputDirectionCodes.N, InputAttackCodes.N, False), (InputDirectionCodes.N, InputAttackCodes.N, False)]
        for input in self.input_log:
            commands += self.TransitionToCommandFromCommand(input[index], previous_input[index])
            previous_input = input
        #print(self.CompressCommands(commands))
        return self.CompressCommands(commands)

    def CompressCommands(self, commands):
        compressed_commands = []
        wait_frames = 0
        for command in commands:
            if command[0] == Command.Wait:
                wait_frames += 1
            else:
                if wait_frames > 0:
                    compressed_commands.append((Command.Wait, wait_frames))
                    wait_frames = 0
                compressed_commands.append(command)
        compressed_commands.append((Command.Wait, wait_frames))

        return compressed_commands



    def GetInputAsNotation(self, index):
        commands = self.GetInputAsCommands(index)
        notation = self.GetCommandsAsNotation(commands)
        return notation


    def GetCommandsAsNotation(self, commands):
        notation = ""
        for command in commands:
            if command[0] == Command.Wait:
                notation += str(command[1]) + ', '
            else:
                notation += MatchRecorder.NOTATION[command[0]] + ', '
        return notation


    def TransitionToCommandFromCommand(self, input, prev_input):
        command = []
        new_dir = input[0].name
        prev_dir = prev_input[0].name

        command += self.CheckForString('u', prev_dir, new_dir, Command.HoldUp, Command.ReleaseUp)
        command += self.CheckForString('d', prev_dir, new_dir, Command.HoldDown, Command.ReleaseDown)
        command += self.CheckForString('b', prev_dir, new_dir, Command.HoldBack, Command.ReleaseBack)
        command += self.CheckForString('f', prev_dir, new_dir, Command.HoldForward, Command.ReleaseForward)


        new_att = input[1].name
        prev_att = prev_input[1].name

        command += self.CheckForString('1', prev_att, new_att, Command.Hold1, Command.Release1)
        command += self.CheckForString('2', prev_att, new_att, Command.Hold2, Command.Release2)
        command += self.CheckForString('3', prev_att, new_att, Command.Hold3, Command.Release3)
        command += self.CheckForString('4', prev_att, new_att, Command.Hold4, Command.Release4)

        new_rage = input[2]
        prev_rage = prev_input[2]

        if new_rage and not prev_rage:
            command.append((Command.HoldRage, 0))

        if prev_rage and not new_rage:
            command.append((Command.ReleaseRage, 0))

        command.append((Command.Wait, 1))

        return command

    def CheckForString(self, string, old, new, on_add, on_remove):
        command = []
        if string in old and not string in new:
            command.append((on_remove, 0))
        if string in new and not string in old:
            command.append((on_add, 0))
        return command


    REPLAY_DIR = "TekkenData/Replays/"
    def PrintInputLog(self):
        print("Recording match...")

        with open(MatchRecorder.REPLAY_DIR + str(time.strftime('%Y_%b_%d_%H.%M.%SS_') + self.p1_name + 'v' + self.p2_name), 'w') as fw:
            fw.write(self.GetInputAsNotation(0) + "\n")
            fw.write(self.GetInputAsNotation(1) + "\n")
        print("...match recorded")


