import math
import random
import time
from TekkenEncyclopedia import TekkenEncyclopedia
from ArtificialKeyboard import ArtificalKeyboard

import GameInputter
import TekkenGameState
import BasicCommands
from BotFrameTrap import BotFrameTrap
from BotPunisher import BotPunisher
from BotRecorder import BotRecorder

#print("ADMIN STATUS: " + str(c.windll.shell32.IsUserAnAdmin()))


class TekkenBotLauncher:
    def __init__(self, botClass, isPlayerOne):
        self.gameState = TekkenGameState.TekkenGameState()
        self.gameController = GameInputter.GameControllerInputter()
        self.botCommands = BasicCommands.BotCommands(self.gameController)
        self.botBrain = botClass(self.botCommands)
        self.benchmarkTime = time.time()
        self.frameRateCounter = 0
        self.frameRate = 0
        self.isPlayerOne = isPlayerOne
        self.doMashAccept = False #before turning this on, make sure that your 'accept' key and your '3' key are different in GameControllerInputter.

    def Update(self):
        successfulUpdate = self.gameState.Update()

        if self.gameState.IsGameHappening() and successfulUpdate:
            self.frameRateCounter += 1

            if not self.isPlayerOne:
                self.gameState.FlipMirror()

            self.gameController.Update(self.gameState.is_tekken_foreground_wnd(), self.gameState.IsBotOnLeft())
            self.botCommands.Update(self.gameState)
            self.botBrain.Update(self.gameState)

            if not self.isPlayerOne:
                self.gameState.FlipMirror()

        if self.doMashAccept:
            self.MashAccept()


        elapsedTime = time.time() - self.benchmarkTime
        if elapsedTime >= 1:
            self.frameRate = self.frameRateCounter / elapsedTime
            self.frameRateCounter = 0
            self.benchmarkTime = time.time()
            if self.frameRate < 31:
                pass
                #print("WARNING! FRAME RATE IS LESS THAN 30 FPS (" + str(int(self.frameRate)) + "). TEKKEN BOT MAY BEHAVE ERRATICALLY.")

    def GetBot(self):
        return self.botBrain

    def MashAccept(self): #Useful for Treasure Mode
        if self.gameState.is_tekken_foreground_wnd():
            if (random.randint(0, 1) == 0):
                ArtificalKeyboard.PressKey(GameInputter.Keys_P2.A)
            else:
                ArtificalKeyboard.ReleaseKey(GameInputter.Keys_P2.A)

if __name__ == "__main__":
    launcher = TekkenBotLauncher(BotRecorder, True)
    while(True):
        launcher.Update()
        time.sleep(.005)
