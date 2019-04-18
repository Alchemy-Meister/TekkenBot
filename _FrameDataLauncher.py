from tekken_game_state import TekkenGameState
from TekkenEncyclopedia import TekkenEncyclopedia
import time

class FrameDataLauncher:
    def __init__(self, print_extended_frame_data=False):
        self.gameState = TekkenGameState()
        self.cyclopedia_p2 = TekkenEncyclopedia(False, print_extended_frame_data)
        self.cyclopedia_p1 = TekkenEncyclopedia(True, print_extended_frame_data)


    def Update(self):
        successfulUpdate = self.gameState.update()
        if successfulUpdate:
            self.cyclopedia_p1.Update(self.gameState)
            self.cyclopedia_p2.Update(self.gameState)
        return successfulUpdate

if __name__ == "__main__":
    launcher = FrameDataLauncher()
    while(True):
        launcher.Update()
        time.sleep(.05)
