"""
A simple bot that presses buttons when emerging from block or hit stun.

"""

from Bot import Bot
from tekken_game_state import TekkenGameState
from BotData import BotBehaviors
from NotationParser import ParseMoveList
from MatchRecorder import MatchRecorder

class BotFrameTrap(Bot):

    def __init__(self, botCommands):
        super().__init__(botCommands)
        self.SetFrameTrapCommandFromNotationString("+4")
        self.recorder = None
        self.inputDelay = 0
        self.inputDelayCode = None


    def Update(self, gameState: TekkenGameState):
        if not self.recorder == None:
            self.recorder.Update(gameState)

        BotBehaviors.Basic(gameState, self.botCommands)

        if self.botCommands.IsAvailable():
            BotBehaviors.BlockAllAttacks(gameState, self.botCommands)
            if gameState.IsBotBlocking() or gameState.IsBotGettingHit():
                self.botCommands.AddCommand(self.response)



    def SetFrameTrapCommandFromNotationString(self, notation: str):
        try:
            self.response = ParseMoveList(">, " + notation + ", >>")
            #print(self.response)
        except:
            print("Could not parse move: " + str(notation))

    def Record(self):
        self.recorder = MatchRecorder()

    def Stop(self):
        notation = self.recorder.GetInputAsNotation()
        #commands = self.recorder.GetInputAsCommands()
        #self.botCommands.ClearCommands()
        #self.botCommands.AddCommand(commands)
        self.recorder = None
        return notation
