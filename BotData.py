from tekken_game_state import TekkenGameState
from BasicCommands import BotCommands

class BotBehaviors:

    def Basic(gameState, botCommands):
        BotBehaviors.StopPressingButtonsAfterGettingHit(gameState, botCommands)
        BotBehaviors.GetUp(gameState, botCommands)
        BotBehaviors.TechCombos(gameState, botCommands)

    def StopPressingButtonsAfterGettingHit(gameState, botCommands):
        if gameState.IsBotStartedGettingHit():
            botCommands.ClearCommands()
        if gameState.IsBotStartedBeingThrown():
            botCommands.ClearCommands()

    def TechThrows(gameState, botCommands):
        if gameState.IsBotBeingThrown():
            botCommands.ThrowTech()

    def GetUp(gameState, botCommands):
        if gameState.IsBotOnGround():
            botCommands.GetUp()

    def TechCombos(gameState, botCommands):
        if gameState.IsBotBeingJuggled():
            botCommands.MashTech()

    def BlockAllAttacks(gameState: TekkenGameState, botCommands:BotCommands):
        if gameState.IsOppAttacking():
            if gameState.IsOppAttackLow():
                botCommands.BlockLowFull(max(0, gameState.GetOppTimeUntilImpact()))
            else:
                botCommands.BlockMidFull(max(0, gameState.GetOppTimeUntilImpact()))

    def UnblockIncomingAttacks(self, gameState: TekkenGameState):
        if gameState.IsOppAttacking():
            self.botCommands.WalkForward(max(0, gameState.GetOppTimeUntilImpact()))