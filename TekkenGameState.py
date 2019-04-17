"""
This module's classes are responsible for reading and interpreting the memory
of a Tekken7.exe proecess.

TekkenGameReader reads the memory of Tekken7.exe, extracts information about
the state of the game, then saves a 'snapshot' of each frame.

Each GameSnapshot has 2 BotSnapshots, together encapsulating the information
of both players and shared data for a single game frame.

TekkenGameState saves these snapshots and provides an api that abstracts away
the difference between questions that query one player (is player 1 currently
attacking?), both players (what is the expected frame advantage when player 2
emerges from block), or multiple game states over time (did player 1 just begin
to block this frame?, what was the last move player 2 did?).
"""

from collections import Counter

import ctypes as c
from ctypes import wintypes as w
import struct
import math

# pylint: disable=wildcard-import
from MoveInfoEnums import *  # NOQA
from ConfigReader import ConfigReader, ReloadableConfig
from MoveDataReport import MoveDataReport
import MovelistParser

import module_enumerator
import pid_searcher
import win32.kernel32 as kernel32

from tekken.game_reader import TekkenGameReader

class TekkenGameState:
    def __init__(self):
        self.game_reader = TekkenGameReader()

        self.duplicate_frame_obtained = 0
        self.stateLog = []
        self.mirroredStateLog = []

        self.isMirrored = False

        self.futureStateLog = None

    def Update(self, buffer=0):
        game_state = self.game_reader.get_updated_state(buffer)

        if game_state is not None:
            # we don't run perfectly in sync, if we get back the same frame,
            # throw it away
            if(
                    not self.stateLog
                    or game_state.frame_count != self.stateLog[-1].frame_count
            ):
                self.duplicate_frame_obtained = 0

                frames_lost = 0
                if self.stateLog:
                    frames_lost = game_state.frame_count - \
                        self.stateLog[-1].frame_count - 1
                    if frames_lost > 0:
                        pass
                        #print("DROPPED FRAMES: " + str(frames_lost))

                for i in range(min(7 - buffer, frames_lost)):
                    #print("RETRIEVING FRAMES")
                    dropped_game_state = self.game_reader.get_updated_state(
                        min(7, frames_lost + buffer) - i)
                    self.AppendGamedata(dropped_game_state)

                self.AppendGamedata(game_state)
                return True

            self.duplicate_frame_obtained += 1
        return False

    def AppendGamedata(self, gameData):
        if not self.isMirrored:
            self.stateLog.append(gameData)
            self.mirroredStateLog.append(gameData.FromMirrored())
        else:
            self.stateLog.append(gameData.FromMirrored())
            self.mirroredStateLog.append(gameData)

        if len(self.stateLog) > 300:
            self.stateLog.pop(0)
            self.mirroredStateLog.pop(0)

    def FlipMirror(self):
        temp_log = self.mirroredStateLog
        self.mirroredStateLog = self.stateLog
        self.stateLog = temp_log
        self.isMirrored = not self.isMirrored

    def BackToTheFuture(self, frames):
        if self.futureStateLog is not None:
            raise AssertionError(
                'Already called BackToTheFuture, '
                'need to return to the present first, Marty'
            )
        else:
            self.futureStateLog = self.stateLog[0 - frames:]
            self.stateLog = self.stateLog[:0 - frames]

    def ReturnToPresent(self):
        if self.futureStateLog is None:
            raise AssertionError(
                "We're already in the present, Marty, what are you doing?")
        self.stateLog += self.futureStateLog
        self.futureStateLog = None

    def IsGameHappening(self):
        return not self.game_reader.is_state_reacquisition_required()

    def IsBotOnLeft(self):
        is_player_one_on_left = (
            self.game_reader.original_facing == self.stateLog[-1].facing_bool
        )
        if not self.isMirrored:
            return is_player_one_on_left
        return not is_player_one_on_left

    def GetBotHealth(self):
        return max(0, 170 - self.stateLog[-1].bot.damage_taken)

    def GetDist(self):
        return self.stateLog[-1].GetDist()

    def DidOppComboCounterJustStartXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return (
                self.stateLog[0 - frames_ago].opp.combo_counter == 1
                and self.stateLog[0 - frames_ago - 1].opp.combo_counter == 0
            )
        return False

    def DidOppComboCounterJustEndXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return (
                self.stateLog[0 - frames_ago].opp.combo_counter == 0
                and self.stateLog[0 - frames_ago - 1].opp.combo_counter > 0
            )
        return False

    def GetOppComboDamageXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return self.stateLog[0 - frames_ago].opp.combo_damage
        return 0

    def GetOppComboHitsXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return self.stateLog[0 - frames_ago].opp.combo_counter
        return 0

    def GetOppJuggleDamageXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return self.stateLog[0 - frames_ago].opp.juggle_damage
        return 0

    def DidBotStartGettingPunishedXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return self.stateLog[0 - frames_ago].bot.IsPunish()
        else:
            return False

    def DidOppStartGettingPunishedXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return self.stateLog[0 - frames_ago].opp.IsPunish()
        else:
            return False

    def BotFramesUntilRecoveryXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return (
                self.stateLog[0 - frames_ago].bot.recovery
                - self.stateLog[0 - frames_ago].bot.move_timer
            )
        else:
            return 99

    def OppFramesUntilRecoveryXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return (
                self.stateLog[0 - frames_ago].opp.recovery
                - self.stateLog[0 - frames_ago].opp.move_timer
            )
        else:
            return 99

    def IsBotBlocking(self):
        return self.stateLog[-1].bot.IsBlocking()

    def IsBotGettingCounterHit(self):
        return self.stateLog[-1].bot.IsGettingCounterHit()

    def IsBotGettingHitOnGround(self):
        return self.stateLog[-1].bot.IsGettingGroundHit()

    def IsOppBlocking(self):
        return self.stateLog[-1].opp.IsBlocking()

    def IsOppGettingHit(self):
        return self.stateLog[-1].opp.IsGettingHit()

    def IsBotGettingHit(self):
        # or self.GetFramesSinceBotTookDamage() < 15
        return self.stateLog[-1].bot.IsGettingHit()
        # return self.GetFramesSinceBotTookDamage() < 15

    def IsOppHitting(self):
        return self.stateLog[-1].opp.IsHitting()

    def IsBotStartedGettingHit(self):
        if len(self.stateLog) > 2:
            return (
                self.IsBotGettingHit() and
                not self.stateLog[-2].bot.IsGettingHit()
            )
        return False

    def IsBotStartedBeingThrown(self):
        if len(self.stateLog) > 2:
            return (
                self.IsBotBeingThrown()
                and not self.stateLog[-2].opp.IsInThrowing()
            )
        return False

    def IsBotComingOutOfBlock(self):
        if(len(self.stateLog) >= 2):
            previousState = self.stateLog[-2].bot.IsBlocking()
            currentState = self.stateLog[-1].bot.IsBlocking()
            return previousState and not currentState
        else:
            return False

    def GetRecoveryOfMoveId(self, moveID):
        largestTime = -1
        for state in reversed(self.stateLog):
            if(state.bot.move_id == moveID):
                largestTime = max(largestTime, state.bot.move_timer)
        return largestTime

    def GetLastMoveID(self):
        for state in reversed(self.stateLog):
            if(state.bot.startup > 0):
                return state.bot.move_id
        return -1

    def GetBotJustMoveID(self):
        return self.stateLog[-2].bot.move_id

    def DidBotRecentlyDoMove(self):
        if len(self.stateLog) > 5:
            return (
                self.stateLog[-1].bot.move_timer
                < self.stateLog[-5].bot.move_timer
            )
        return False

    def DidBotRecentlyDoDamage(self):
        if len(self.stateLog) > 10:
            if(
                    self.stateLog[-1].opp.damage_taken
                    > self.stateLog[-20].opp.damage_taken
            ):
                return True
        return False

    def IsBotCrouching(self):
        return self.stateLog[-1].bot.IsTechnicalCrouch()

    def IsOppAttackMid(self):
        return self.stateLog[-1].opp.IsAttackMid()

    def IsOppAttackUnblockable(self):
        return self.stateLog[-1].opp.IsAttackUnblockable()

    def IsOppAttackAntiair(self):
        return self.stateLog[-1].opp.IsAttackAntiair()

    def IsOppAttackThrow(self):
        return self.stateLog[-1].opp.IsAttackThrow()

    def IsOppAttackLow(self):
        return self.stateLog[-1].opp.IsAttackLow()

    def IsOppAttacking(self):
        return self.stateLog[-1].opp.IsAttackStarting()

    # only finds landing canceled moves?
    def GetOppMoveInterruptedFrames(self):
        if len(self.stateLog) > 3:
            if self.stateLog[-1].opp.move_timer == 1:
                interruptedFrames = self.stateLog[-2].opp.move_timer - (
                    self.stateLog[-3].opp.move_timer + 1)
                if interruptedFrames > 0:
                    # landing animation causes move_timer to go *up* to the end
                    # of the move
                    return interruptedFrames
        return 0

    def GetFramesUntilOutOfBlock(self):
        # print(self.stateLog[-1].bot.block_flags)
        if not self.IsBotBlocking():
            return 0
        else:
            recovery = self.stateLog[-1].bot.recovery
            blockFrames = self.GetFramesBotHasBeenBlockingAttack()
            return (recovery) - blockFrames

    def GetFrameProgressOfOppAttack(self):
        mostRecentStateWithAttack = None
        framesSinceLastAttack = 0
        for state in reversed(self.stateLog):
            if mostRecentStateWithAttack == None:
                if state['p2_attack_startup'] > 0:
                    mostRecentStateWithAttack = state
            elif(
                    state['p2_move_id'] == mostRecentStateWithAttack.opp.move_id
                    and state.opp.move_timer
                    < mostRecentStateWithAttack.opp.move_timer
            ):
                framesSinceLastAttack += 1
            else:
                break
        return framesSinceLastAttack

    def GetFramesBotHasBeenBlockingAttack(self):
        if not self.stateLog[-1].bot.IsBlocking():
            return 0
        else:
            opponentMoveId = self.stateLog[-1].opp.move_id
            opponentMoveTimer = self.stateLog[-1].opp.move_timer

            framesSpentBlocking = 0
            for state in reversed(self.stateLog):
                # print(state.opp.move_timer)
                # print(state.opp.move_id)
                # print(opponentMoveId)
                if(
                        state.bot.IsBlocking()
                        and state.opp.move_timer <= opponentMoveTimer
                        and state.opp.move_id == opponentMoveId
                        and state.opp.move_timer > state.opp.startup
                ):
                    framesSpentBlocking += 1
                    opponentMoveTimer = state.opp.move_timer
                else:
                    break
            # print(framesSpentBlocking)
            return framesSpentBlocking

    def IsOppWhiffingXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return self.stateLog[0 - frames_ago].opp.IsAttackWhiffing()
        else:
            return False

    def IsOppWhiffing(self):
        return self.stateLog[-1].opp.IsAttackWhiffing()

    def IsBotWhiffing(self):
        return self.stateLog[-1].bot.IsAttackWhiffing()

    def IsBotWhileStanding(self):
        return self.stateLog[-1].bot.IsWhileStanding()

    def GetBotFramesUntilRecoveryEnds(self):
        return (
            self.stateLog[-1].bot.recovery - self.stateLog[-1].bot.move_timer
        )

    def IsBotMoveChanged(self):
        if len(self.stateLog) > 2:
            return (
                self.stateLog[-1].bot.move_id
                != self.stateLog[-2].bot.move_id
            )
        return False

    def IsBotWhiffingAlt(self):
        currentBot = self.stateLog[-1].bot
        if currentBot.startup == 0:  # we might still be in recovery
            for i, state in enumerate(reversed(self.stateLog)):
                if state.bot.startup > 0:
                    pass
        else:
            return currentBot.IsAttackWhiffing()

    def GetOpponentMoveIDWithCharacterMarker(self):
        characterMarker = self.stateLog[-1].opp.char_id
        return self.stateLog[-1].opp.move_id + characterMarker * 10000000

    def GetOppStartup(self):
        return self.stateLog[-1].opp.startup

    def GetBotStartupXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return self.stateLog[0 - frames_ago].bot.startup
        else:
            return False

    def GetOppActiveFrames(self):
        return self.stateLog[-1].opp.GetActiveFrames()

    def GetLastActiveFrameHitWasOn(self, frames):
        returnNextState = False
        for state in reversed(self.stateLog[-(frames + 2):]):
            if returnNextState:
                return (state.opp.move_timer - state.opp.startup) + 1

            if state.bot.move_timer == 1:
                returnNextState = True

        return 0

        # return (
        #     self.stateLog[-1].opp.move_timer - self.stateLog[-1].opp.startup
        # )
        # elapsedActiveFrames = 0
        # opp_move_timer = -1
        # for state in reversed(self.stateLog):
        #     elapsedActiveFrames += 1
        # if (
        #         state.bot.move_timer == 1
        #         or state.opp.move_timer == state.opp.startup
        # ):
        #     return elapsedActiveFrames
        # return -1

    def GetOppActiveFramesXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return self.stateLog[0 - frames_ago].opp.GetActiveFrames()
        return 0

    def GetOppRecovery(self):
        return self.stateLog[-1].opp.recovery

    def GetOppFramesTillNextMove(self):
        return self.GetOppRecovery() - self.GetOppMoveTimer()

    def GetBotFramesTillNextMove(self):
        return self.GetBotRecovery() - self.GetBotMoveTimer()

    def GetBotRecovery(self):
        return self.stateLog[-1].bot.recovery

    def GetOppMoveId(self):
        return self.stateLog[-1].opp.move_id

    def GetOppAttackType(self):
        return self.stateLog[-1].opp.attack_type

    def GetOppAttackTypeXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return self.stateLog[0 - frames_ago].opp.attack_type
        return False

    def GetBotMoveId(self):
        return self.stateLog[-1].bot.move_id

    def GetBotStartup(self):
        return self.stateLog[-1].bot.startup

    def GetBotMoveTimer(self):
        return self.stateLog[-1].bot.move_timer

    def GetOppMoveTimer(self):
        return self.stateLog[-1].opp.move_timer

    def IsBotAttackStarting(self):
        return (self.GetBotStartup() - self.GetBotMoveTimer()) > 0

    def GetOppTimeUntilImpact(self):
        return (
            self.GetOppStartup() - self.stateLog[-1].opp.move_timer
            + self.stateLog[-1].opp.GetActiveFrames()
        )

    def GetBotTimeUntilImpact(self):
        return (
            self.GetBotStartup() - self.stateLog[-1].bot.move_timer
            + self.stateLog[-1].bot.GetActiveFrames()
        )

    def IsBotOnGround(self):
        return self.stateLog[-1].bot.IsOnGround()

    def IsBotBeingKnockedDown(self):
        return self.stateLog[-1].bot.IsBeingKnockedDown()

    def IsBotBeingWallSplatted(self):
        return self.stateLog[-1].bot.IsGettingWallSplatted()

    def GetOppDamage(self):
        return self.stateLog[-1].opp.attack_damage

    def GetMostRecentOppDamage(self):
        if self.stateLog[-1].opp.attack_damage > 0:
            return self.stateLog[-1].opp.attack_damage

        currentHealth = self.stateLog[-1].bot.damage_taken

        for state in reversed(self.stateLog):
            if state.bot.damage_taken < currentHealth:
                return currentHealth - state.bot.damage_taken
        return 0

    def GetOppLatestNonZeroStartupAndDamage(self):
        for state in reversed(self.stateLog):
            damage = state.opp.attack_damage
            startup = state.opp.startup
            if damage > 0 or startup > 0:
                return (startup, damage)
        return (0, 0)

    def IsBotJustGrounded(self):
        if len(self.stateLog) > 2:
            return (
                self.stateLog[-1].bot.IsOnGround()
                and not self.stateLog[-2].bot.IsOnGround()
                and not self.stateLog[-2].bot.IsBeingJuggled()
                and not self.stateLog[-2].bot.IsBeingKnockedDown()
            )
        return False

    def IsBotBeingJuggled(self):
        return self.stateLog[-1].bot.IsBeingJuggled()

    def IsBotStartedBeingJuggled(self):
        if len(self.stateLog) > 2:
            return (
                self.stateLog[-1].bot.IsBeingJuggled()
                and not self.stateLog[-2].bot.IsBeingJuggled()
            )
        return False

    def IsBotBeingThrown(self):
        return self.stateLog[-1].opp.IsInThrowing()

    def IsOppWallSplat(self):
        return self.stateLog[-1].opp.IsWallSplat()

    def DidBotJustTakeDamage(self, frames_ago=1):
        if len(self.stateLog) > frames_ago:
            return max(
                0,
                self.stateLog[0 - frames_ago].bot.damage_taken
                - self.stateLog[0 - frames_ago - 1].bot.damage_taken
            )
        return 0

    def DidOppJustTakeDamage(self, frames_ago=1):
        if len(self.stateLog) > frames_ago:
            return max(
                0,
                self.stateLog[0 - frames_ago].opp.damage_taken
                - self.stateLog[0 - frames_ago - 1].opp.damage_taken
            )
        return 0

    def DidOppTakeDamageDuringStartup(self):
        current_damage_taken = self.stateLog[-1].opp.damage_taken
        current_move_timer = self.stateLog[-1].opp.move_timer
        for state in reversed(self.stateLog):
            if state.opp.damage_taken < current_damage_taken:
                return True
            if current_move_timer < state.opp.move_timer:
                return False
            else:
                current_move_timer = state.opp.move_timer
        return False

    def DidBotTimerInterruptXMovesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            # if(
            #         self.stateLog[0 - frames_ago].bot.move_id != 32769
            #         or self.stateLog[0 - frames_ago -1].bot.move_id != 32769
            # ):
            return (
                self.stateLog[0 - frames_ago].bot.move_timer
                < self.stateLog[0 - frames_ago - 1].bot.move_timer
            )
            #print(
            #     '{} {}'.format(
            #         self.stateLog[0 - frames_ago].bot.move_timer,
            #         self.stateLog[0 - frames_ago - 1].bot.move_timer
            #     )
            # )
            # return (
            #     self.stateLog[0 - frames_ago].bot.move_timer
            #     != self.stateLog[0 - frames_ago - 1].bot.move_timer + 1
            # )

        return False

    def DidBotStartGettingHitXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return (
                self.stateLog[0 - frames_ago].bot.IsGettingHit()
                and not self.stateLog[0 - frames_ago - 1].bot.IsGettingHit()
            )
        return False

    def DidOppStartGettingHitXFramesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return (
                self.stateLog[0 - frames_ago].opp.IsGettingHit()
                and not self.stateLog[0 - frames_ago - 1].opp.IsGettingHit()
            )
        return False

    def DidBotIdChangeXMovesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return (
                self.stateLog[0 - frames_ago].bot.move_id
                != self.stateLog[0 - frames_ago - 1].bot.move_id
            )
        return False

    def DidOppIdChangeXMovesAgo(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return (
                self.stateLog[0 - frames_ago].opp.move_id
                != self.stateLog[0 - frames_ago - 1].opp.move_id
            )
        return False

    def GetBotElapsedFramesOfRageMove(self, rage_move_startup):
        frozenFrames = 0
        last_move_timer = -1
        for state in reversed(self.stateLog[-rage_move_startup:]):
            if state.bot.move_timer == last_move_timer:
                frozenFrames += 1
            last_move_timer = state.bot.move_timer
        return rage_move_startup - frozenFrames

    def IsOppInRage(self):
        return self.stateLog[-1].opp.IsInRage()

    def DidOpponentUseRageRecently(self, recentlyFrames):
        if not self.IsOppInRage():
            for state in reversed(self.stateLog[-recentlyFrames:]):
                if state.opp.IsInRage():
                    return True
        return False

    def GetFramesSinceBotTookDamage(self):
        damage_taken = self.stateLog[-1].bot.damage_taken
        for i, state in enumerate(reversed(self.stateLog)):
            if state.bot.damage_taken < damage_taken:
                return i
        return 1000

    def GetLastOppSnapshotWithDifferentMoveId(self):
        moveId = self.stateLog[-1].opp.move_id
        for state in reversed(self.stateLog):
            if state.opp.move_id != moveId:
                return state
        return self.stateLog[-1]

    def GetLastOppWithDifferentMoveId(self):
        return self.GetLastOppSnapshotWithDifferentMoveId().opp

    def GetOppLastMoveInput(self):
        oppMoveId = self.stateLog[-1].opp.move_id
        input = []
        for state in reversed(self.stateLog):
            if (
                    state.opp.move_id != oppMoveId
                    and state.opp.GetInputState()[1] != InputAttackCodes.N
            ):
                input.append(state.opp.GetInputState())
                return input

        return [(InputDirectionCodes.N, InputAttackCodes.N, False)]

    def GetCurrentOppMoveString(self):
        if self.stateLog[-1].opp.movelist_parser != None:
            move_id = self.stateLog[-1].opp.move_id
            previous_move_id = -1

            input_array = []

            i = len(self.stateLog)

            while True:
                next_move, last_move_was_empty_cancel = self.GetOppMoveString(
                    move_id, previous_move_id)
                next_move = str(next_move)

                if last_move_was_empty_cancel:
                    input_array[-1] = ''

                # if len(next_move) > 0:
                input_array.append(next_move)

                if(
                        self.stateLog[-1].opp.movelist_parser
                        .can_be_done_from_neutral(move_id)
                ):
                    break

                while True:
                    i -= 1
                    if i < 0:
                        break
                    if self.stateLog[i].opp.move_id != move_id:
                        previous_move_id = move_id
                        move_id = self.stateLog[i].opp.move_id
                        break
                if i < 0:
                    break

            clean_input_array = reversed(
                [a for a in input_array if len(a) > 0])
            return ','.join(clean_input_array)
        else:
            return 'N/A'

        # self.stateLog[-1].opp.movelist_parser.can_be_done_from_neutral

    def GetOppMoveString(self, move_id, previous_move_id):
        return self.stateLog[-1].opp.movelist_parser.input_for_move(
            move_id, previous_move_id
        )

    def HasOppReturnedToNeutralFromMoveId(self, move_id):
        for state in reversed(self.stateLog):
            if state.opp.move_id == move_id:
                return False
            if state.opp.movelist_parser.can_be_done_from_neutral(
                    state.opp.move_id
            ):
                return True
        return True

    def GetFrameDataOfCurrentOppMove(self):
        if self.stateLog[-1].opp.startup > 0:
            opp = self.stateLog[-1].opp
        else:
            gameState = self.GetLastOppSnapshotWithDifferentMoveId()
            if gameState != None:
                opp = gameState.opp
            else:
                opp = self.stateLog[-1].opp
        return self.GetFrameData(self.stateLog[-1].bot, opp)

    def GetFrameDataOfCurrentBotMove(self):
        return self.GetFrameData(self.stateLog[-1].opp, self.stateLog[-1].bot)

    def GetFrameData(self, defendingPlayer, attackingPlayer):
        return (
            (defendingPlayer.recovery + attackingPlayer.startup)
            - attackingPlayer.recovery
        )

    def GetBotCharId(self):
        char_id = self.stateLog[-1].bot.char_id
        # if -1 < char_id < 50:
        print("Character: " + str(char_id))
        return char_id

    def IsFulfillJumpFallbackConditions(self):
        if len(self.stateLog) > 10:
            if (
                    self.stateLog[-7].bot.IsAirborne()
                    and self.stateLog[-7].opp.IsAirborne()
            ):
                if (
                        not self.stateLog[-8].bot.IsAirborne()
                        or not self.stateLog[-8].opp.IsAirborne()
                ):
                    for state in self.stateLog[-10:]:
                        if not(
                                state.bot.IsHoldingUp()
                                or state.opp.IsHoldingUp()
                        ):
                            return False
                    return True
        return False

    def IsOppAbleToAct(self):
        return self.stateLog[-1].opp.IsAbleToAct()

    def GetBotInputState(self):
        return self.stateLog[-1].bot.GetInputState()

    def GetOppInputState(self):
        return self.stateLog[-1].opp.GetInputState()

    def GetBotName(self):
        return self.stateLog[-1].bot.character_name

    def GetOppName(self):
        return self.stateLog[-1].opp.character_name

    def GetBotThrowTech(self, activeFrames):
        for state in reversed(self.stateLog[-activeFrames:]):
            tech = state.bot.throw_tech
            if tech != ThrowTechs.NONE:
                return tech
        return ThrowTechs.NONE

    def GetOppTrackingType(self, startup):
        if len(self.stateLog) > startup:
            complex_states = [ComplexMoveStates.UNKN]
            for state in reversed(self.stateLog[-startup:]):
                if -1 < state.opp.GetTrackingType().value < 8:
                    complex_states.append(state.opp.GetTrackingType())
            return Counter(complex_states).most_common(1)[0][0]
        else:
            return ComplexMoveStates.F_MINUS

    def GetOppTechnicalStates(self, startup):

        #opp_id = self.stateLog[-1].opp.move_id
        tc_frames = []
        tj_frames = []
        cancel_frames = []
        buffer_frames = []
        pc_frames = []
        homing_frames1 = []
        homing_frames2 = []
        parryable_frames1 = []
        parryable_frames2 = []
        startup_frames = []
        frozen_frames = []

        #found = False
        # for state in reversed(self.stateLog):
        # if state.opp.move_id == opp_id and not state.opp.is_bufferable:
        #found = True
        previous_state = None
        skipped_frames_counter = 0
        frozen_frames_counter = 0
        for i, state in enumerate(reversed(self.stateLog[-startup:])):
            if previous_state != None:
                is_skipped = (
                    state.opp.move_timer != previous_state.opp.move_timer - 1
                )
                if is_skipped:
                    skipped_frames_counter += 1
                is_frozen = (
                    state.bot.move_timer == previous_state.bot.move_timer
                )
                if is_frozen:
                    frozen_frames_counter += 1
            else:
                is_skipped = False
                is_frozen = False
            if skipped_frames_counter + i <= startup:
                tc_frames.append(state.opp.IsTechnicalCrouch())
                tj_frames.append(state.opp.IsTechnicalJump())
                cancel_frames.append(state.opp.IsAbleToAct())
                buffer_frames.append(state.opp.IsBufferable())
                pc_frames.append(state.opp.IsPowerCrush())
                homing_frames1.append(state.opp.IsHoming1())
                homing_frames2.append(state.opp.IsHoming2())
                parryable_frames1.append(state.opp.IsParryable1())
                parryable_frames2.append(state.opp.IsParryable2())
                startup_frames.append(is_skipped)
                frozen_frames.append(is_frozen)

            previous_state = state

        parryable1 = MoveDataReport('PY1', parryable_frames1)
        parryable2 = MoveDataReport('PY2', parryable_frames2)
        unparryable = MoveDataReport(
            'NO PARRY?', [
                not parryable1.is_present() and not parryable2.is_present()
            ]
        )

        return [
            MoveDataReport('TC', tc_frames),
            MoveDataReport('TJ', tj_frames),
            MoveDataReport('BUF', buffer_frames),
            MoveDataReport('xx', cancel_frames),
            MoveDataReport('PC', pc_frames),
            MoveDataReport('HOM1', homing_frames1),
            MoveDataReport('HOM2', homing_frames2),
            MoveDataReport('SKIP', startup_frames),
            MoveDataReport('FROZ', frozen_frames),
            # parryable1,
            # parryable2,
            # unparryable
        ]

    def IsFightOver(self):
        return self.duplicate_frame_obtained > 5

    def WasTimerReset(self):
        if len(self.stateLog) > 2:
            return (
                self.stateLog[-1].timer_frames_remaining
                > self.stateLog[-2].timer_frames_remaining
            )
        return False

    def DidTimerStartTicking(self, buffer):
        return self.stateLog[-1].timer_frames_remaining == 3600 - 1 - buffer

    def WasFightReset(self):
        false_reset_buffer = 0
        if len(self.stateLog) > 2:
            return (
                self.stateLog[-1].frame_count < self.stateLog[-2].frame_count
                and self.stateLog[-2].frame_count > false_reset_buffer
            )
        return False

    def GetTimer(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            return self.stateLog[-frames_ago].timer_frames_remaining
        return False

    def GetRoundNumber(self):
        return self.stateLog[-1].opp.wins + self.stateLog[-1].bot.wins

    def GetOppRoundSummary(self, frames_ago):
        if len(self.stateLog) > frames_ago:
            opp = self.stateLog[-frames_ago].opp
            bot = self.stateLog[-frames_ago].bot
            return (opp.wins, bot.damage_taken)
        return (0, 0)

    def GetRangeOfMove(self):
        move_timer = self.stateLog[-1].opp.move_timer
        opp_id = self.stateLog[-1].opp.move_id
        for state in reversed(self.stateLog):
            starting_skeleton = state.opp.skeleton
            bot_skeleton = state.bot.skeleton
            old_dist = state.GetDist()
            if move_timer < state.opp.move_timer:
                break
            if opp_id != state.opp.move_id:
                break
            move_timer = state.opp.move_timer
        ending_skeleton = self.stateLog[-1].opp.skeleton

        avg_ss_x = sum(starting_skeleton[0]) / len(starting_skeleton[0])
        avg_ss_z = sum(starting_skeleton[2]) / len(starting_skeleton[2])
        avg_bs_x = sum(bot_skeleton[0]) / len(bot_skeleton[0])
        avg_bs_z = sum(bot_skeleton[2]) / len(bot_skeleton[2])

        vector_towards_bot = (avg_bs_x - avg_ss_x, avg_bs_z - avg_ss_z)

        toward_bot_magnitude = math.sqrt(
            pow(vector_towards_bot[0], 2) + pow(vector_towards_bot[1], 2))
        unit_vector_towards_bot = (
            vector_towards_bot[0] / toward_bot_magnitude,
            vector_towards_bot[1] / toward_bot_magnitude
        )

        movements = [
            (ai_x - bi_x, ai_z - bi_z) for ai_x, bi_x, ai_z, bi_z in zip(
                ending_skeleton[0], starting_skeleton[0],
                ending_skeleton[2], starting_skeleton[2])
        ]
        dotproducts = []
        for movement in movements:
            dotproducts.append(
                movement[0] * unit_vector_towards_bot[0]
                + movement[1] * unit_vector_towards_bot[1]
            )

        max_product = max(dotproducts)
        max_index = dotproducts.index(max_product)
        return max_index, max_product

    def IsBotUsingOppMovelist(self):
        return self.stateLog[-1].bot.use_opponents_movelist

    def GetCurrentBotMoveName(self):
        move_id = self.stateLog[-1].bot.move_id
        return self.GetOppMoveName(
            move_id, self.stateLog[-1].bot.use_opponents_movelist,
            is_for_bot=True
        )

    def GetCurrentOppMoveName(self):
        move_id = self.stateLog[-1].opp.move_id
        return self.GetOppMoveName(
            move_id, self.stateLog[-1].opp.use_opponents_movelist,
            is_for_bot=False
        )

    def GetOppMoveName(self, move_id, use_opponents_movelist, is_for_bot=False):

        if move_id > 30000:
            return 'Universal_{}'.format(move_id)

        try:
            if (
                    not self.isMirrored and not is_for_bot
                    or self.isMirrored and is_for_bot
            ):
                if not use_opponents_movelist:
                    movelist = self.game_reader.p2_movelist_names
                else:
                    movelist = self.game_reader.p1_movelist_names
            else:
                if not use_opponents_movelist:
                    movelist = self.game_reader.p1_movelist_names
                else:
                    movelist = self.game_reader.p2_movelist_names

            return movelist[(move_id * 2) + 4].decode('utf-8')
        except:
            return "ERROR"

    def is_tekken_foreground_wnd(self):
        return self.game_reader.is_tekken_foreground_wnd()
