"""
A simple bot that presses buttons when emerging from block or hit stun.

"""

from Bot import Bot
from tekken_game_state import TekkenGameState
from TekkenEncyclopedia import TekkenEncyclopedia
from BotData import BotBehaviors
from CharacterData import *


class BotPunisher(Bot):

    def __init__(self, botCommands):
        super().__init__(botCommands)
        self.gameplan = None
        self.enemyCyclopedia = TekkenEncyclopedia(False)


    def Update(self, gameState: TekkenGameState):

        self.enemyCyclopedia.Update(gameState)

        if gameState.WasFightReset():
            self.botCommands.ClearCommands()
            self.gameplan = None

        if self.gameplan == None :
            char_id = gameState.GetBotCharId()
            if char_id != None:
                self.gameplan = GetGameplan(char_id)

        if self.gameplan != None:
            BotBehaviors.Basic(gameState, self.botCommands)
            if self.botCommands.IsAvailable():
                BotBehaviors.BlockAllAttacks(gameState, self.botCommands)
                frameAdvantage = None
                if gameState.IsBotBlocking():
                    frameAdvantage = self.enemyCyclopedia.GetFrameAdvantage(gameState.GetOppMoveId())
                elif gameState.IsBotGettingHit():
                    frameAdvantage = self.enemyCyclopedia.GetFrameAdvantage(gameState.GetOppMoveId(), isOnBlock=False)

                try:
                    frameAdvantage = int(frameAdvantage) * -1
                except:
                    frameAdvantage = None

                if frameAdvantage != None:
                    if frameAdvantage >= 10:
                        if gameState.IsBotWhileStanding():
                            punish = self.gameplan.GetMoveByFrame(ResponseTypes.ws_punishes, frameAdvantage)
                        else:
                            punish = self.gameplan.GetMoveByFrame(ResponseTypes.st_punishes, frameAdvantage)
                        if punish != None:
                            self.botCommands.AddCommand(punish)




