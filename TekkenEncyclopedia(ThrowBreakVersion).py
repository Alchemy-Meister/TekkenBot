"""
Collects information from TekkenGameState over time in hopes of synthesizing it and presenting it in a more useful way.

"""

import time
from enum import Enum

import artificial_keyboard
from MoveInfoEnums import AttackType
from MoveInfoEnums import ComplexMoveStates
from MoveInfoEnums import ThrowTechs
from TekkenGameState import TekkenGameState


class TekkenEncyclopedia:
    def __init__(self, isPlayerOne=False, print_extended_frame_data=False):
        self.FrameData = {}
        self.GameEvents = []
        self.current_game_event = None
        self.isPlayerOne = isPlayerOne
        self.print_extended_frame_data = print_extended_frame_data

        self.active_frame_wait = 1

        self.was_fight_being_reacquired = True
        self.is_match_recorded = False

        self.stat_filename = "TekkenData/matches.txt"
        if self.isPlayerOne:
            self.LoadStats()

        self.current_punish_window = None
        self.PunishWindows = []
        self.current_frame_data_entry = None
        self.previous_frame_data_entry = None

    def LoadStats(self):
        self.stat_dict = {}
        self.stat_dict['char_stats'] = {}
        self.stat_dict['matchup_stats'] = {}
        self.stat_dict['opponent_stats'] = {}
        try:
            with open(self.stat_filename, 'r', encoding='utf-8') as fr:
                lines = fr.readlines()
            for line in lines:
                if '|' in line:
                    args = line.split('|')
                    result = args[0].strip()
                    player_char = args[2].strip()
                    opponent_name = args[4].strip()
                    opponent_char = args[5].strip()
                    self.AddStat(result, player_char, opponent_name, opponent_char)
        except FileNotFoundError:
            pass

    def AddStat(self, result, player_char, opponent_name, opponent_char):

        if not opponent_char in self.stat_dict['char_stats']:
            self.stat_dict['char_stats'][opponent_char] = [0, 0, 0]
        if not opponent_name in self.stat_dict['opponent_stats']:
            self.stat_dict['opponent_stats'][opponent_name] = [0, 0, 0]
        matchup_string = "{} vs {}".format(player_char, opponent_char)
        if not matchup_string in self.stat_dict['matchup_stats']:
            self.stat_dict['matchup_stats'][matchup_string] = [0, 0, 0]

        if 'WIN' in result:
            index = 0
        elif 'LOSS' in result:
            index = 1
        else:
            index = 2

        self.stat_dict['char_stats'][opponent_char][index] += 1
        self.stat_dict['opponent_stats'][opponent_name][index] += 1
        self.stat_dict['matchup_stats'][matchup_string][index] += 1

    def RecordFromStat(self, catagory, lookup):
        try:

            stats = self.stat_dict[catagory][lookup]
            wins = stats[0]
            losses = stats[1]
            draws = stats[2]

        except:
            wins = 0
            losses = 0
            draws = 0

        if draws <= 0:
            return "{} - {}".format(wins, losses)
        else:
            return "{} - {} - {}".format(wins, losses, draws)

    def GetPlayerString(self, reverse=False):
        if (self.isPlayerOne and not reverse) or (not self.isPlayerOne and reverse):
            return "p1: "
        else:
            return "p2: "

    def GetFrameAdvantage(self, moveId, isOnBlock=True):
        if moveId in self.FrameData:
            if isOnBlock:
                return self.FrameData[moveId].onBlock
            else:
                return self.FrameData[moveId].onNormalHit
        else:
            return None

    # Set the dummy to jump and hold up and this prints the frame difference.
    def CheckJumpFrameDataFallback(self, gameState):
        if not self.isPlayerOne:
            if gameState.IsFulfillJumpFallbackConditions():
                print("p1 jump frame diff: " + str(gameState.GetBotMoveTimer() - gameState.GetOppMoveTimer()))

    def Update(self, gameState: TekkenGameState):
        if self.isPlayerOne:
            gameState.FlipMirror()

        # self.CheckJumpFrameDataFallback(gameState)

        self.DetermineFrameData(gameState)

        self.DetermineGameStats(gameState)

        self.DetermineCoachingTips(gameState)

        if self.isPlayerOne:
            gameState.FlipMirror()

    def DetermineCoachingTips(self, gameState: TekkenGameState):

        if self.previous_frame_data_entry != self.current_frame_data_entry:
            self.previous_frame_data_entry = self.current_frame_data_entry

            if self.current_punish_window != None:
                self.ClosePunishWindow(PunishWindow.Result.NO_WINDOW, do_close_frame_data_entries=False)

            # if int(self.current_frame_data_entry.currentFrameAdvantage) <= 999999:
            self.current_punish_window = PunishWindow(self.current_frame_data_entry.prefix,
                                                      self.current_frame_data_entry.move_id,
                                                      self.current_frame_data_entry.input,
                                                      int(self.current_frame_data_entry.hitRecovery),
                                                      int(self.current_frame_data_entry.blockRecovery),
                                                      int(self.current_frame_data_entry.activeFrames))
            self.PunishWindows.append(self.current_punish_window)
            self.punish_window_counter = 0

        if self.current_punish_window != None:
            self.punish_window_counter += 1
            # if self.punish_window_counter > self.current_punish_window.size:

            was_block_punish = gameState.DidOppStartGettingPunishedXFramesAgo(
                1) or gameState.DidOppStartGettingHitXFramesAgo(1)

            if was_block_punish:
                leeway = (gameState.OppFramesUntilRecoveryXFramesAgo(2) - 1)
                LAUNCH_PUNISHIBLE = 15
                BAD_PUNISH_THRESHOLD = 13
                # if leeway == 0:
                # self.ClosePunishWindow(PunishWindow.Result.PERFECT_PUNISH)
                # else:
                fa = (-1 * self.current_punish_window.get_frame_advantage())
                startup = fa - leeway
                if fa >= LAUNCH_PUNISHIBLE and startup <= BAD_PUNISH_THRESHOLD:
                    self.ClosePunishWindow(PunishWindow.Result.NO_LAUNCH_ON_LAUNCHABLE)
                elif fa >= LAUNCH_PUNISHIBLE:
                    self.ClosePunishWindow(PunishWindow.Result.LAUNCH_ON_LAUNCHABLE)
                else:
                    self.ClosePunishWindow(PunishWindow.Result.JAB_ON_NOT_LAUNCHABLE)

            elif gameState.HasOppReturnedToNeutralFromMoveId(
                    self.current_punish_window.move_id) and self.punish_window_counter >= self.current_punish_window.hit_recovery:
                if self.current_punish_window.get_frame_advantage() <= -10:
                    self.ClosePunishWindow(PunishWindow.Result.NO_PUNISH)
                else:
                    self.ClosePunishWindow(PunishWindow.Result.NO_WINDOW)
            if self.current_punish_window != None:
                self.current_punish_window.adjust_window(gameState.GetOppFramesTillNextMove(),
                                                         gameState.GetBotFramesTillNextMove())

            # perfect_punish = False
            # if was_block_punish:
            # perfect_punish = gameState.WasBotMoveOnLastFrameXFramesAgo(2)

    def ClosePunishWindow(self, result, do_close_frame_data_entries=True):
        self.current_punish_window.close_window(result)
        self.current_punish_window = None
        if do_close_frame_data_entries:
            self.previous_frame_data_entry = None
            self.current_frame_data_entry = None

    def DetermineGameStats(self, gameState: TekkenGameState):
        frames_ago = 4
        if self.current_game_event == None:
            if gameState.DidOppComboCounterJustStartXFramesAgo(frames_ago):
                gameState.BackToTheFuture(frames_ago)

                combo_counter_damage = gameState.GetOppComboDamageXFramesAgo(1)

                was_unblockable = gameState.IsOppAttackUnblockable()
                was_antiair = gameState.IsOppAttackAntiair()
                was_block_punish = gameState.DidBotStartGettingPunishedXFramesAgo(1)
                perfect_punish = False
                if was_block_punish:
                    perfect_punish = gameState.BotFramesUntilRecoveryXFramesAgo(2) == 1
                was_counter_hit = gameState.IsBotGettingCounterHit()
                was_ground_hit = gameState.IsBotGettingHitOnGround()

                was_whiff_punish = gameState.GetBotStartupXFramesAgo(2) > 0

                was_low_hit = gameState.IsOppAttackLow()
                was_mid_hit_on_crouching = gameState.IsOppAttackMid() and gameState.IsBotCrouching()
                was_throw = gameState.IsBotBeingThrown()

                was_damaged_during_attack = gameState.DidOppTakeDamageDuringStartup()

                gameState.ReturnToPresent()

                if was_unblockable:
                    hit = GameStatEventEntry.EntryType.UNBLOCKABLE
                elif was_antiair:
                    hit = GameStatEventEntry.EntryType.ANTIAIR
                elif was_throw:
                    hit = GameStatEventEntry.EntryType.THROW
                elif was_damaged_during_attack:
                    hit = GameStatEventEntry.EntryType.POWER_CRUSHED
                elif was_block_punish:
                    hit = GameStatEventEntry.EntryType.PUNISH
                elif was_counter_hit:
                    hit = GameStatEventEntry.EntryType.COUNTER
                elif was_ground_hit:
                    hit = GameStatEventEntry.EntryType.GROUND
                elif was_whiff_punish:
                    hit = GameStatEventEntry.EntryType.WHIFF_PUNISH
                elif was_low_hit:
                    hit = GameStatEventEntry.EntryType.LOW
                elif was_mid_hit_on_crouching:
                    hit = GameStatEventEntry.EntryType.MID
                else:
                    hit = GameStatEventEntry.EntryType.NO_BLOCK
                self.current_game_event = GameStatEventEntry(gameState.stateLog[-1].timer_frames_remaining,
                                                             self.GetPlayerString(True), hit, combo_counter_damage)

                # print("event open")
            else:
                bot_damage_taken = gameState.DidBotJustTakeDamage(frames_ago + 1)
                if bot_damage_taken > 0:
                    # print('armored')
                    game_event = GameStatEventEntry(gameState.stateLog[-1].timer_frames_remaining,
                                                    self.GetPlayerString(True), GameStatEventEntry.EntryType.ARMORED,
                                                    0)  # this is probably gonna break for Yoshimitsu's self damage moves
                    game_event.close_entry(gameState.stateLog[-1].timer_frames_remaining, 1, bot_damage_taken, 0,
                                           len(self.GameEvents))

                    self.GameEvents.append(game_event)



        else:
            if gameState.DidOppComboCounterJustEndXFramesAgo(frames_ago) or gameState.WasFightReset():
                hits = gameState.GetOppComboHitsXFramesAgo(frames_ago + 1)
                damage = gameState.GetOppComboDamageXFramesAgo(frames_ago + 1)
                juggle = gameState.GetOppJuggleDamageXFramesAgo(frames_ago + 1)
                self.current_game_event.close_entry(gameState.stateLog[-1].timer_frames_remaining, hits, damage, juggle,
                                                    len(self.GameEvents))
                self.GameEvents.append(self.current_game_event)
                self.current_game_event = None
                # print("event closed")

        if gameState.WasFightReset():
            # print("p1: NOW:0")
            # print("p2: NOW:0")
            if self.isPlayerOne:
                if gameState.game_reader.reacquire_names == False and self.was_fight_being_reacquired:
                    self.is_match_recorded = False

                    for entry in self.get_matchup_record(gameState):
                        print(entry)

                round_number = gameState.GetRoundNumber()
                print("!ROUND | {} | HIT".format(round_number))
                if (gameState.stateLog[-1].bot.wins == 3 or gameState.stateLog[
                    -1].opp.wins == 3) and not self.is_match_recorded:
                    self.is_match_recorded = True

                    player_name = "You"
                    p1_char_name = gameState.stateLog[-1].opp.character_name
                    p1_wins = gameState.stateLog[-1].opp.wins

                    opponent_name = gameState.stateLog[-1].opponent_name
                    p2_char_name = gameState.stateLog[-1].bot.character_name
                    p2_wins = gameState.stateLog[-1].bot.wins

                    if gameState.stateLog[-1].is_player_player_one:
                        player_char, player_wins = p1_char_name, p1_wins
                        opponent_char, opponent_wins = p2_char_name, p2_wins
                    else:
                        player_char, player_wins = p2_char_name, p2_wins
                        opponent_char, opponent_wins = p1_char_name, p1_wins

                    if player_wins == opponent_wins:
                        result = 'DRAW'
                    elif player_wins > opponent_wins:
                        result = 'WIN'
                    else:
                        result = "LOSS"

                    match_result = '{} | {} | {} | vs | {} | {} | {}-{} | {}'.format(result, player_name, player_char,
                                                                                     opponent_name, opponent_char,
                                                                                     player_wins, opponent_wins,
                                                                                     time.strftime('%Y_%m_%d_%H.%M'))
                    print("{}".format(match_result))
                    self.AddStat(result, player_char, opponent_name, opponent_char)
                    with open(self.stat_filename, "a", encoding='utf-8') as fa:
                        fa.write(match_result + '\n')
            if (gameState.GetTimer(frames_ago) < 3600 and len(self.GameEvents) > 0) or True:
                summary = RoundSummary(self.GameEvents, gameState.GetOppRoundSummary(frames_ago))

            self.GameEvents = []

        self.was_fight_being_reacquired = gameState.game_reader.reacquire_names

    def get_matchup_record(self, gameState):
        if gameState.stateLog[-1].is_player_player_one:
            opponent_char = gameState.stateLog[-1].bot.character_name
            player_char = gameState.stateLog[-1].opp.character_name
        else:
            opponent_char = gameState.stateLog[-1].opp.character_name
            player_char = gameState.stateLog[-1].bot.character_name
        opponent_name = gameState.stateLog[-1].opponent_name
        return [
            ("!RECORD | vs {}: {}".format(opponent_char, self.RecordFromStat('char_stats', opponent_char))),
            ("!RECORD | vs {}: {}".format(opponent_name, self.RecordFromStat('opponent_stats', opponent_name))),
            ("!RECORD | {} vs {}: {}".format(player_char, opponent_char, self.RecordFromStat("matchup_stats",
                                                                                             "{} vs {}".format(
                                                                                                 player_char,
                                                                                                 opponent_char))))
        ]

    def DetermineFrameData(self, gameState):
        if (
                gameState.IsBotBlocking() or gameState.IsBotGettingHit() or gameState.IsBotBeingThrown() or gameState.IsBotBeingKnockedDown() or gameState.IsBotBeingWallSplatted()):  # or gameState.IsBotUsingOppMovelist()): #or  gameState.IsBotStartedBeingJuggled() or gameState.IsBotJustGrounded()):
            # print(gameState.stateLog[-1].bot.move_id)
            # print(gameState.stateLog[-1].bot.move_timer)
            # print(gameState.stateLog[-1].bot.recovery)
            # print(gameState.DidBotIdChangeXMovesAgo(self.active_frame_wait))

            if gameState.DidBotIdChangeXMovesAgo(self.active_frame_wait) or gameState.DidBotTimerInterruptXMovesAgo(
                    self.active_frame_wait):  # or gameState.DidOppIdChangeXMovesAgo(self.active_frame_wait):

                is_recovering_before_long_active_frame_move_completes = (
                        gameState.GetBotRecovery() - gameState.GetBotMoveTimer() == 0)
                gameState.BackToTheFuture(self.active_frame_wait)

                # print(gameState.GetOppActiveFrames())
                if (
                        not self.active_frame_wait >= gameState.GetOppActiveFrames() + 1) and not is_recovering_before_long_active_frame_move_completes:
                    self.active_frame_wait += 1
                else:
                    gameState.ReturnToPresent()

                    currentActiveFrame = gameState.GetLastActiveFrameHitWasOn(self.active_frame_wait)

                    gameState.BackToTheFuture(self.active_frame_wait)

                    opp_id = gameState.GetOppMoveId()

                    if opp_id in self.FrameData:
                        frameDataEntry = self.FrameData[opp_id]
                    else:
                        frameDataEntry = FrameDataEntry(self.print_extended_frame_data)
                        self.FrameData[opp_id] = frameDataEntry

                    frameDataEntry.currentActiveFrame = currentActiveFrame

                    frameDataEntry.currentFrameAdvantage = '??'
                    frameDataEntry.move_id = opp_id
                    # frameDataEntry.damage =
                    frameDataEntry.damage = gameState.GetOppDamage()
                    frameDataEntry.startup = gameState.GetOppStartup()

                    if frameDataEntry.damage == 0 and frameDataEntry.startup == 0:
                        frameDataEntry.startup, frameDataEntry.damage = gameState.GetOppLatestNonZeroStartupAndDamage()

                    frameDataEntry.activeFrames = gameState.GetOppActiveFrames()
                    frameDataEntry.hitType = AttackType(gameState.GetOppAttackType()).name
                    if gameState.IsOppAttackThrow():
                        frameDataEntry.hitType += "_THROW"

                    frameDataEntry.recovery = gameState.GetOppRecovery()

                    # frameDataEntry.input = frameDataEntry.InputTupleToInputString(gameState.GetOppLastMoveInput())

                    frameDataEntry.input = gameState.GetCurrentOppMoveString()

                    frameDataEntry.technical_state_reports = gameState.GetOppTechnicalStates(frameDataEntry.startup - 1)

                    frameDataEntry.tracking = gameState.GetOppTrackingType(frameDataEntry.startup)

                    # print(gameState.GetRangeOfMove())

                    gameState.ReturnToPresent()

                    # frameDataEntry.throwTech = gameState.GetBotThrowTech(frameDataEntry.activeFrames + frameDataEntry.startup)
                    frameDataEntry.throwTech = gameState.GetBotThrowTech(1)

                    time_till_recovery_opp = gameState.GetOppFramesTillNextMove()
                    time_till_recovery_bot = gameState.GetBotFramesTillNextMove()

                    new_frame_advantage_calc = time_till_recovery_bot - time_till_recovery_opp

                    frameDataEntry.currentFrameAdvantage = frameDataEntry.WithPlusIfNeeded(new_frame_advantage_calc)

                    if gameState.IsBotBlocking():
                        frameDataEntry.onBlock = new_frame_advantage_calc
                    else:
                        if gameState.IsBotGettingCounterHit():
                            frameDataEntry.onCounterHit = new_frame_advantage_calc
                        else:
                            frameDataEntry.onNormalHit = new_frame_advantage_calc

                    frameDataEntry.hitRecovery = time_till_recovery_opp
                    frameDataEntry.blockRecovery = time_till_recovery_bot

                    frameDataEntry.move_str = gameState.GetCurrentOppMoveName()
                    frameDataEntry.prefix = self.GetPlayerString()

                    print(str(frameDataEntry))

                    self.current_frame_data_entry = frameDataEntry

                    gameState.BackToTheFuture(self.active_frame_wait)

                    self.active_frame_wait = 1
                gameState.ReturnToPresent()


class FrameDataEntry:
    def __init__(self, print_extended=False):
        self.print_extended = print_extended
        self.prefix = '??'
        self.move_id = '??'
        self.move_str = '??'
        self.startup = '??'
        self.calculated_startup = -1
        self.hitType = '??'
        self.onBlock = '??'
        self.onCounterHit = '??'
        self.onNormalHit = '??'
        self.recovery = '??'
        self.damage = '??'
        self.blockFrames = '??'
        self.activeFrames = '??'
        self.currentFrameAdvantage = '??'
        self.currentActiveFrame = '??'
        self.input = '??'
        self.technical_state_reports = []
        self.blockRecovery = '??'
        self.hitRecovery = '??'
        self.throwTech = None
        self.tracking = ComplexMoveStates.F_MINUS

    def WithPlusIfNeeded(self, value):
        try:
            if value >= 0:
                return '+' + str(value)
            else:
                return str(value)
        except:
            return str(value)

    def InputTupleToInputString(self, inputTuple):
        s = ""
        for input in inputTuple:
            s += (input[0].name + input[1].name.replace('x', '+')).replace('N', '')
        if input[2]:
            s += "+R"
        return s

    def __repr__(self):

        notes = ''
        MAGIC_THROW_BREAK_NUMBER = 1
        MAGIC_THROW_BREAK_FLOAT = 1
        if self.throwTech != None and self.throwTech != ThrowTechs.NONE:
            throw_type = self.throwTech.name
            if throw_type == "TE1":
                # press 1
                artificial_keyboard.press_and_release_n_times(0x16, MAGIC_THROW_BREAK_FLOAT, MAGIC_THROW_BREAK_NUMBER)

            elif throw_type == "TE2":
                # press 2
                artificial_keyboard.press_and_release_n_times(0x17, MAGIC_THROW_BREAK_FLOAT, MAGIC_THROW_BREAK_NUMBER)

            elif throw_type == "TE1_2":
                # press 1+2
                artificial_keyboard.press_and_release_n_times(0x18, MAGIC_THROW_BREAK_FLOAT, MAGIC_THROW_BREAK_NUMBER)

            notes += self.throwTech.name + " "

        self.calculated_startup = self.startup
        for report in self.technical_state_reports:
            # if not self.print_extended:
            if 'TC' in report.name and report.is_present():
                notes += str(report)
            elif 'TJ' in report.name and report.is_present():
                notes += str(report)
            elif 'PC' in report.name and report.is_present():
                notes += str(report)
            elif 'SKIP' in report.name and report.is_present():
                # print(report)
                self.calculated_startup -= report.total_present()
            elif 'FROZ' in report.name and report.is_present():
                # print(report)
                self.calculated_startup -= report.total_present()
            elif self.print_extended:
                if report.is_present():
                    notes += str(report)
        nerd_string = ""
        if self.print_extended:
            pass
            # notes += ' stun {}'.format(self.blockRecovery)
            # notes += ' a_recovery {}'.format(self.hitRecovery)
            # notes += "Total:" + str(self.recovery) + "f "

        if self.calculated_startup != self.startup:
            self.calculated_startup = str(self.calculated_startup) + "?"

        non_nerd_string = "{:^5}|{:^4}|{:^4}|{:^7}|{:^4}|{:^4}|{:^4}|{:^5}|{:^3}|{:^2}|{:^3}|{:^3}|{:^3}|".format(
            str(self.input),
            str(self.move_id),
            self.move_str,
            str(self.hitType)[:7],
            str(self.calculated_startup),
            self.WithPlusIfNeeded(self.onBlock),
            self.WithPlusIfNeeded(self.onNormalHit),
            self.WithPlusIfNeeded(self.onCounterHit),
            (str(self.currentActiveFrame) + "/" + str(self.activeFrames)),
            self.tracking.name.replace('_MINUS', '-').replace("_PLUS", '+').replace(ComplexMoveStates.UNKN.name, '?'),
            self.recovery,
            self.hitRecovery,
            self.blockRecovery
        )

        notes_string = "{}".format(notes)
        now_string = " NOW:{}".format(str(self.currentFrameAdvantage))
        return self.prefix + non_nerd_string + notes_string + now_string


class GameStatEventEntry:
    class EntryType(Enum):
        COUNTER = 1
        PUNISH = 2
        WHIFF_PUNISH = 3
        LOW = 4
        MID = 5
        THROW = 6
        GROUND = 7
        NO_BLOCK = 8

        ARMORED = 10

        UNBLOCKABLE = 12

        ANTIAIR = 14
        POWER_CRUSHED = 15

        # Not implemented
        LOW_PARRY = 9
        OUT_OF_THE_AIR = 13

    class PunishType(Enum):
        NONE = 0
        PERFECT = 1
        JAB = 2
        JAB_ON_LAUNCH_PUNISHIBLE = 3

    def __init__(self, time_in_frames, player_string, hit_type: EntryType, combo_counter_damage):
        self.start_time = time_in_frames
        self.player_string = player_string
        self.hit_type = hit_type
        self.damage_already_on_combo_counter = combo_counter_damage

    def close_entry(self, time_in_frames, total_hits, total_damage, juggle_damage, times_hit):
        self.end_time = time_in_frames
        self.total_hits = total_hits
        self.total_damage = max(0, total_damage - self.damage_already_on_combo_counter)
        self.juggle_damage = juggle_damage

        print('{} {} | {} | {} | {} | {} | HIT'.format(self.player_string, self.hit_type.name, self.total_damage,
                                                       self.total_hits, self.start_time, self.end_time))


class RoundSummary:
    def __init__(self, events, round_variables):
        self.events = events
        self.collated_events = self.collate_events(events)
        total_damage = 0
        sources, types = self.collated_events
        # print('{} combos for {} damage'.format(types[0][0], types[0][1]))
        # print('{} pokes for {} damage'.format(types[1][0], types[1][1]))
        for event, hits, damage in sources:
            if damage > 0:
                # print('{} {} for {} damage'.format(hits, event.name, damage))
                total_damage += damage

        # print('total damage dealt {} ({})'.format(round_variables[1], total_damage))

    def collate_events(self, events):
        hits_into_juggles = 0
        hits_into_pokes = 0
        damage_from_juggles = 0
        damage_from_pokes = 0
        sources = []

        for entry in GameStatEventEntry.EntryType:
            occurances = 0
            damage = 0
            for event in events:
                if entry == event.hit_type:
                    occurances += 1
                    damage += event.total_damage
                    if event.juggle_damage > 0:
                        damage_from_juggles += event.total_damage
                        hits_into_juggles += 1
                    else:
                        damage_from_pokes += event.total_damage
                        hits_into_pokes += 1
            sources.append((entry, occurances, damage))

        sources.sort(key=lambda x: x[2], reverse=True)
        types = [(hits_into_juggles, damage_from_juggles), (hits_into_pokes, damage_from_pokes)]
        return sources, types

    def __repr__(self):
        pass


class PunishWindow:
    class Result(Enum):
        NO_WINDOW = 0
        NO_PUNISH = 1
        PERFECT_PUNISH = 2
        NO_LAUNCH_ON_LAUNCHABLE = 3
        LAUNCH_ON_LAUNCHABLE = 4
        JAB_ON_NOT_LAUNCHABLE = 5

        NOT_YET_CLOSED = 99

    def __init__(self, prefix, move_id, string_name, hit_recovery, block_recovery, active_frames):
        self.prefix = prefix
        self.move_id = move_id
        self.name = string_name
        self.hit_recovery = hit_recovery
        self.block_recovery = block_recovery
        self.active_frames = active_frames
        self.is_window_locked = False
        self.original_diff = self.get_frame_advantage()
        self.upcoming_lock = False
        self.frames_locked = 0
        self.result = PunishWindow.Result.NOT_YET_CLOSED

    def get_frame_advantage(self):
        if not self.is_window_locked:
            return self.block_recovery - self.hit_recovery
        else:
            return 0 - self.hit_recovery - self.frames_locked

    def adjust_window(self, hit_recovery, block_recovery):
        # if block_recovery > self.block_recovery:

        self.hit_recovery = hit_recovery

        if self.upcoming_lock:
            self.frames_locked += 1
            self.is_window_locked = True

        if not self.is_window_locked:
            self.block_recovery = block_recovery

        if block_recovery == 0:
            self.upcoming_lock = True

        if self.get_frame_advantage() != self.original_diff:
            print('{} NOW:{}'.format(self.prefix, FrameDataEntry.WithPlusIfNeeded(None, self.get_frame_advantage())))
            self.original_diff = self.get_frame_advantage()

    def close_window(self, result: Result):
        self.result = result
        if result != PunishWindow.Result.NO_WINDOW:
            print("Closing punish window, result: {}".format(self.result.name))
