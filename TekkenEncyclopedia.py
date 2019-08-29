"""
Collects information from tekken_game_state over time in hopes of synthesizing
it and presenting it in a more useful way.

"""
from enum import Enum
import sys
import time

from constants.battle import PunishResult
from MoveInfoEnums import AttackType
from MoveInfoEnums import ThrowTechs
from MoveInfoEnums import ComplexMoveStates
from tekken_game_state import TekkenGameState

class TekkenEncyclopedia:
    def __init__(self, is_player_one=False, print_extended_frame_data=False):
        self.frame_data = {}
        self.game_events = []
        self.current_game_event = None
        self.is_player_one = is_player_one
        self.print_extended_frame_data = print_extended_frame_data

        self.active_frame_wait = 1
        self.punish_window_counter = 0

        self.was_fight_being_reacquired = True
        self.is_match_recorded = False

        self.stat_filename = "TekkenData/matches.txt"
        if self.is_player_one:
            self.load_stats()

        self.current_punish_window = None
        self.punish_windows = []
        self.current_frame_data_entry = None
        self.previous_frame_data_entry = None

    def load_stats(self):
        self.stat_dict = {}
        self.stat_dict['char_stats'] = {}
        self.stat_dict['matchup_stats'] = {}
        self.stat_dict['opponent_stats'] = {}
        try:
            with open(self.stat_filename, 'r') as r_file:
                lines = r_file.readlines()
            for line in lines:
                if '|' in line:
                    args = line.split('|')
                    result = args[0].strip()
                    player_char = args[2].strip()
                    opponent_name = args[4].strip()
                    opponent_char = args[5].strip()
                    self.add_stat(
                        result, player_char, opponent_name, opponent_char
                    )
        except FileNotFoundError:
            pass

    def add_stat(self, result, player_char, opponent_name, opponent_char):
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

    def record_from_stat(self, catagory, lookup):
        try:
            stats = self.stat_dict[catagory][lookup]
            wins = stats[0]
            losses = stats[1]
            draws = stats[2]
        except KeyError:
            wins = 0
            losses = 0
            draws = 0

        if draws <= 0:
            return '{} - {}'.format(wins, losses)
        return '{} - {} - {}'.format(wins, losses, draws)

    def get_player_string(self, reverse=False):
        if (
                (self.is_player_one and not reverse)
                or (not self.is_player_one and reverse)
        ):
            return "p1: "
        return "p2: "

    def get_frame_advantage(self, move_id, is_on_block=True):
        if move_id in self.frame_data:
            if is_on_block:
                return self.frame_data[move_id].onBlock
            return self.frame_data[move_id].onNormalHit
        return None

    def check_jumpframe_data_fallback(self, game_state: TekkenGameState):
        #Set the dummy to jump and hold up and this prints the frame difference.
        if not self.is_player_one:
            if game_state.is_fulfill_jump_fallback_conditions():
                sys.stdout.write(
                    'p1 jump frame diff: {}'.format(
                        game_state.get_bot_move_timer()
                        - game_state.get_opp_move_timer()
                    )
                )

    def update(self, game_state: TekkenGameState):
        if self.is_player_one:
            game_state.flip_mirror()

        # self.check_jumpframe_data_fallback(game_state)
        self.determine_frame_data(game_state)
        self.determine_game_stats(game_state)
        self.determine_coaching_tips(game_state)

        if self.is_player_one:
            game_state.flip_mirror()

    def determine_coaching_tips(self, game_state: TekkenGameState):
        if self.previous_frame_data_entry != self.current_frame_data_entry:
            self.previous_frame_data_entry = self.current_frame_data_entry

            if self.current_punish_window is not None:
                self.close_punish_window(
                    PunishResult.NO_WINDOW,
                    do_close_frame_data_entries=False
                )

            # if(
            #       int(self.current_frame_data_entry.currentFrameAdvantage)
            #       <= 999999
            # ):
            self.current_punish_window = (
                PunishWindow(
                    self.current_frame_data_entry.prefix,
                    self.current_frame_data_entry.move_id,
                    self.current_frame_data_entry.input,
                    int(self.current_frame_data_entry.hitRecovery),
                    int(self.current_frame_data_entry.blockRecovery),
                    int(self.current_frame_data_entry.activeFrames)
                )
            )
            self.punish_windows.append(self.current_punish_window)
            self.punish_window_counter = 0

        if self.current_punish_window is not None:
            self.punish_window_counter += 1
            #if self.punish_window_counter > self.current_punish_window.size:

            was_block_punish = (
                game_state.did_opp_start_getting_punished_x_frames_ago(1)
                or game_state.did_opp_start_getting_hit_x_frames_ago(1)
            )

            if was_block_punish:
                leeway = (
                    game_state.opp_frames_until_recovery_x_frames_ago(2) - 1
                )
                # TODO these constants should go to a Enum
                LAUNCH_PUNISHIBLE = 15
                BAD_PUNISH_THRESHOLD = 13
                # if leeway == 0:
                    # self.close_punish_window(
                    #   PunishWindow.Result.PERFECT_PUNISH
                    # )
                # else:
                frame_advantage = (
                    -1 * self.current_punish_window.get_frame_advantage()
                )
                startup = frame_advantage - leeway
                if(
                        frame_advantage >= LAUNCH_PUNISHIBLE
                        and startup <= BAD_PUNISH_THRESHOLD
                ):
                    self.close_punish_window(
                        PunishResult.NO_LAUNCH_ON_LAUNCHABLE
                    )
                elif frame_advantage >= LAUNCH_PUNISHIBLE:
                    self.close_punish_window(PunishResult.LAUNCH_ON_LAUNCHABLE)
                else:
                    self.close_punish_window(PunishResult.JAB_ON_NOT_LAUNCHABLE)
            elif(
                    game_state.has_opp_returned_to_neutral_from_move_id(
                        self.current_punish_window.move_id
                    ) and self.punish_window_counter
                    >= self.current_punish_window.hit_recovery
                ):
                if self.current_punish_window.get_frame_advantage() <= -10:
                    self.close_punish_window(PunishResult.NO_PUNISH)
                else:
                    self.close_punish_window(PunishResult.NO_WINDOW)
            if self.current_punish_window is not None:
                self.current_punish_window.adjust_window(
                    game_state.get_opp_frames_till_next_move(),
                    game_state.get_bot_frames_till_next_move()
                )

            # perfect_punish = False
            # if was_block_punish:
                # perfect_punish = (
                #   game_state.was_bot_move_on_last_frame_x_frames_ago(2)
                # )

    def close_punish_window(self, result, do_close_frame_data_entries=True):
        self.current_punish_window.close_window(result)
        self.current_punish_window = None
        if do_close_frame_data_entries:
            self.previous_frame_data_entry = None
            self.current_frame_data_entry = None

    def determine_game_stats(self, game_state: TekkenGameState):
        frames_ago = 4
        if self.current_game_event is None:
            if(
                    game_state.did_opp_combo_counter_just_start_x_frames_ago(
                        frames_ago
                    )
            ):
                game_state.back_to_the_future(frames_ago)

                combo_counter_damage = (
                    game_state.get_opp_combo_damage_x_frames_ago(1)
                )

                if game_state.is_opp_attack_unblockable():
                    hit = GameStatEventEntry.EntryType.UNBLOCKABLE
                elif game_state.is_opp_attack_antiair():
                    hit = GameStatEventEntry.EntryType.ANTIAIR
                elif game_state.is_bot_being_thrown():
                    hit = GameStatEventEntry.EntryType.THROW
                elif game_state.did_opp_take_damage_during_startup():
                    hit = GameStatEventEntry.EntryType.POWER_CRUSHED
                elif game_state.did_bot_start_getting_punished_x_frames_ago(1):
                    perfect_punish = (
                        game_state.bot_frames_until_recovery_x_frames_ago(2)
                        == 1
                    )
                    hit = GameStatEventEntry.EntryType.PUNISH
                elif game_state.is_bot_getting_counter_hit():
                    hit = GameStatEventEntry.EntryType.COUNTER
                elif game_state.is_bot_getting_hit_on_ground():
                    hit = GameStatEventEntry.EntryType.GROUND
                elif game_state.get_bot_startup_x_frames_ago(2) > 0:
                    hit = GameStatEventEntry.EntryType.WHIFF_PUNISH
                elif game_state.is_opp_attack_low():
                    hit = GameStatEventEntry.EntryType.LOW
                elif(
                        game_state.is_opp_attack_mid()
                        and game_state.is_bot_crouching()
                    ):
                    hit = GameStatEventEntry.EntryType.MID
                else:
                    hit = GameStatEventEntry.EntryType.NO_BLOCK

                game_state.return_to_present()
                self.current_game_event = (
                    GameStatEventEntry(
                        game_state.state_log[-1].timer_frames_remaining,
                        self.get_player_string(True),
                        hit,
                        combo_counter_damage
                    )
                )
                # print("event open")
            else:
                bot_damage_taken = (
                    game_state.did_bot_just_take_damage(frames_ago + 1)
                )
                if bot_damage_taken > 0:
                    #print('armored')
                    # FIXME this is probably gonna break for Yoshimitsu's 
                    # self damage moves
                    game_event = GameStatEventEntry(
                        game_state.state_log[-1].timer_frames_remaining,
                        self.get_player_string(True),\
                        GameStatEventEntry.EntryType.ARMORED,
                        0
                    )
                    game_event.close_entry(
                        game_state.state_log[-1].timer_frames_remaining,
                        1,
                        bot_damage_taken,
                        0,
                        len(self.game_events)
                    )
                    self.game_events.append(game_event)
        else:
            if(
                    game_state.did_opp_combo_counter_just_end_x_frames_ago(
                        frames_ago
                    ) or game_state.was_fight_reset()
            ):
                hits = game_state.get_opp_combo_hits_x_frames_ago(
                    frames_ago + 1
                )
                damage = game_state.get_opp_combo_damage_x_frames_ago(
                    frames_ago + 1
                )
                juggle = game_state.get_opp_juggle_damage_x_frames_ago(
                    frames_ago + 1
                )
                self.current_game_event.close_entry(
                    game_state.state_log[-1].timer_frames_remaining,
                    hits,
                    damage,
                    juggle,
                    len(self.game_events)
                )
                self.game_events.append(self.current_game_event)
                self.current_game_event = None
                #print("event closed")

        if game_state.was_fight_reset():
            #print("p1: NOW:0")
            #print("p2: NOW:0")
            if self.is_player_one:
                if(
                        not game_state.get_reader().reacquire_names
                        and self.was_fight_being_reacquired
                ):
                    self.is_match_recorded = False
                    for entry in self.get_matchup_record(game_state):
                        sys.stdout.write(entry)

                round_number = game_state.get_round_number()
                sys.stdout.write('!ROUND | {} | HIT'.format(round_number))
                if(
                        (
                            game_state.state_log[-1].bot.wins == 3
                            or game_state.state_log[-1].opp.wins == 3
                        ) and not self.is_match_recorded
                ):
                    self.is_match_recorded = True

                    player_name = "You"
                    p1_char_name = game_state.state_log[-1].opp.character_name
                    p1_wins = game_state.state_log[-1].opp.wins

                    opponent_name = game_state.state_log[-1].opponent_name
                    p2_char_name = game_state.state_log[-1].bot.character_name
                    p2_wins = game_state.state_log[-1].bot.wins

                    if game_state.state_log[-1].is_player_player_one:
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

                    match_result = (
                        '{} | {} | {} | vs | {} | {} | {}-{} | {}'.format(
                            result, player_name, player_char, opponent_name,
                            opponent_char, player_wins, opponent_wins,
                            time.strftime('%Y_%m_%d_%H.%M')
                        )
                    )
                    sys.stdout.write('{}'.format(match_result))
                    self.add_stat(
                        result, player_char, opponent_name, opponent_char
                    )
                    with open(self.stat_filename, 'a') as a_file:
                        a_file.write(match_result + '\n')
            if game_state.get_timer(frames_ago) < 3600 and self.game_events:
                summary = RoundSummary(
                    self.game_events,
                    game_state.get_opp_round_summary(frames_ago)
                )
            self.game_events = []

        self.was_fight_being_reacquired = (
            game_state.get_reader().reacquire_names
        )

    def get_matchup_record(self, game_state):
        if game_state.state_log[-1].is_player_player_one:
            opponent_char = game_state.state_log[-1].bot.character_name
            player_char = game_state.state_log[-1].opp.character_name
        else:
            opponent_char = game_state.state_log[-1].opp.character_name
            player_char = game_state.state_log[-1].bot.character_name
        opponent_name = game_state.state_log[-1].opponent_name
        return [
            '!RECORD | vs {}: {}'.format(
                opponent_char,
                self.record_from_stat('char_stats', opponent_char)
            ),
            '!RECORD | vs {}: {}'.format(
                opponent_name,
                self.record_from_stat('opponent_stats', opponent_name)
            ),
            '!RECORD | {} vs {}: {}'.format(
                player_char, opponent_char,
                self.record_from_stat(
                    'matchup_stats', '{} vs {}'.format(
                        player_char, opponent_char
                    )
                )
            )
        ]

    def determine_frame_data(self, game_state):
        if(
                game_state.is_bot_blocking()
                or game_state.is_bot_getting_hit()
                or game_state.is_bot_being_thrown()
                or game_state.is_bot_being_knocked_down()
                or game_state.is_bot_being_wall_splatted()
                # or game_state.is_bot_using_opp_movelist()
                # or game_state.is_bot_started_being_juggled()
                # or game_state.is_bot_just_grounded()
        ):
            # print(game_state.state_log[-1].bot.move_id)
            # print(game_state.state_log[-1].bot.move_timer)
            # print(game_state.state_log[-1].bot.recovery)
            # print(
            #   game_state.did_bot_id_change_x_moves_ago(
            #       self.active_frame_wait
            #   )
            # )

            if(
                    game_state.did_bot_id_change_x_moves_ago(
                        self.active_frame_wait
                    ) or game_state.did_bot_timer_interrupt_x_moves_ago(
                        self.active_frame_wait
                    )
                    # or game_state.did_opp_id_change_x_moves_ago(
                    #   self.active_frame_wait
                    # )
            ):
                is_recovering_before_long_active_frame_move_completes = (
                    game_state.get_bot_recovery()
                    - game_state.get_bot_move_timer() == 0
                )
                game_state.back_to_the_future(self.active_frame_wait)

                #print(game_state.get_opp_active_frames())
                if(
                        not self.active_frame_wait
                        >= game_state.get_opp_active_frames() + 1
                        and not
                        is_recovering_before_long_active_frame_move_completes
                ):
                    self.active_frame_wait += 1
                else:
                    game_state.return_to_present()
                    currentActiveFrame = (
                        game_state.get_last_active_frame_hit_was_on(
                            self.active_frame_wait
                        )
                    )
                    game_state.back_to_the_future(self.active_frame_wait)
                    opp_id = game_state.get_opp_move_id()

                    if opp_id in self.frame_data:
                        frame_data_entry = self.frame_data[opp_id]
                    else:
                        frame_data_entry = FrameDataEntry(
                            self.print_extended_frame_data
                        )
                        self.frame_data[opp_id] = frame_data_entry

                    frame_data_entry.currentActiveFrame = currentActiveFrame

                    frame_data_entry.currentFrameAdvantage = '??'
                    frame_data_entry.move_id = opp_id
                    # frame_data_entry.damage =
                    frame_data_entry.damage = game_state.get_opp_damage()
                    frame_data_entry.startup = game_state.get_opp_startup()

                    if(
                            frame_data_entry.damage == 0
                            and frame_data_entry.startup == 0
                    ):
                        frame_data_entry.startup, frame_data_entry.damage = (
                            game_state
                            .get_opp_latest_non_zero_startup_and_damage()
                        )

                    frame_data_entry.activeFrames = (
                        game_state.get_opp_active_frames()
                    )
                    frame_data_entry.hitType = AttackType(
                        game_state.get_opp_attack_type()
                    ).name
                    if game_state.is_opp_attack_throw():
                        frame_data_entry.hitType += "_THROW"

                    frame_data_entry.recovery = game_state.get_opp_recovery()

                    # frame_data_entry.input = (
                    #   frame_data_entry.InputTupleToInputString(
                    #       game_state.get_opp_last_move_input()
                    #   )
                    # )
                    frame_data_entry.input = (
                        game_state.get_current_opp_move_string()
                    )

                    frame_data_entry.technical_state_reports = (
                        game_state.get_opp_technical_states(
                            frame_data_entry.startup - 1
                        )
                    )
                    frame_data_entry.tracking = (
                        game_state.get_opp_tracking_type(
                            frame_data_entry.startup
                        )
                    )
                    # print(game_state.get_range_of_move())
                    game_state.return_to_present()

                    # frame_data_entry.throwTech = (
                    #   game_state.get_bot_throw_tech(
                    #       frame_data_entry.activeFrames
                    #       + frame_data_entry.startup
                    #   )
                    # )
                    frame_data_entry.throwTech = game_state.get_bot_throw_tech(
                        1
                    )

                    time_till_recovery_opp = (
                        game_state.get_opp_frames_till_next_move()
                    )
                    time_till_recovery_bot = (
                        game_state.get_bot_frames_till_next_move()
                    )
                    new_frame_advantage_calc = (
                        time_till_recovery_bot - time_till_recovery_opp
                    )
                    frame_data_entry.currentFrameAdvantage = (
                        frame_data_entry.WithPlusIfNeeded(
                            new_frame_advantage_calc
                        )
                    )

                    if game_state.is_bot_blocking():
                        frame_data_entry.onBlock = new_frame_advantage_calc
                    else:
                        if game_state.is_bot_getting_counter_hit():
                            frame_data_entry.onCounterHit = (
                                new_frame_advantage_calc
                            )
                        else:
                            frame_data_entry.onNormalHit = (
                                new_frame_advantage_calc
                            )

                    frame_data_entry.hitRecovery = time_till_recovery_opp
                    frame_data_entry.blockRecovery = time_till_recovery_bot

                    frame_data_entry.move_str = (
                        game_state.get_current_opp_move_name()
                    )
                    frame_data_entry.prefix = self.get_player_string()

                    sys.stdout.write(frame_data_entry)

                    self.current_frame_data_entry = frame_data_entry

                    game_state.back_to_the_future(self.active_frame_wait)

                    self.active_frame_wait = 1
                game_state.return_to_present()

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

        if self.throwTech != None and self.throwTech != ThrowTechs.NONE:
            notes += self.throwTech.name + " "

        self.calculated_startup = self.startup
        for report in self.technical_state_reports:
            #if not self.print_extended:
            if 'TC' in report.name and report.is_present():
                notes += str(report)
            elif 'TJ' in report.name and report.is_present():
                notes += str(report)
            elif 'PC' in report.name and report.is_present():
                notes += str(report)
            elif 'SKIP' in report.name and report.is_present():
                #print(report)
                self.calculated_startup -= report.total_present()
            elif 'FROZ' in report.name and report.is_present():
                #print(report)
                self.calculated_startup -= report.total_present()
            elif self.print_extended:
                if report.is_present():
                    notes += str(report)
        nerd_string = ""
        if self.print_extended:
            pass
            #notes += ' stun {}'.format(self.blockRecovery)
            #notes += ' a_recovery {}'.format(self.hitRecovery)
            #notes += "Total:" + str(self.recovery) + "f "

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
        if notes_string:
            now_string = 'NOW:{}'.format(self.currentFrameAdvantage)
        else:
            now_string = ' NOW:{}'.format(self.currentFrameAdvantage)
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

        #Not implemented
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

        print('{} {} | {} | {} | {} | {} | HIT'.format(self.player_string, self.hit_type.name, self.total_damage, self.total_hits, self.start_time, self.end_time))



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
        types = [
            (hits_into_juggles, damage_from_juggles),
            (hits_into_pokes, damage_from_pokes)
        ]
        return sources, types

    def __repr__(self):
        pass

class PunishWindow:
    """
    """
    def __init__(
            self, prefix, move_id, string_name, hit_recovery, block_recovery,
            active_frames
        ):
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
        self.result = PunishResult.NOT_YET_CLOSED

    def get_frame_advantage(self):
        if not self.is_window_locked:
            return self.block_recovery - self.hit_recovery
        return 0 - self.hit_recovery - self.frames_locked

    def adjust_window(self, hit_recovery, block_recovery):
        #if block_recovery > self.block_recovery:
        self.hit_recovery = hit_recovery

        if self.upcoming_lock:
            self.frames_locked += 1
            self.is_window_locked = True

        if not self.is_window_locked:
            self.block_recovery = block_recovery

        if block_recovery == 0:
            self.upcoming_lock = True

        if self.get_frame_advantage() != self.original_diff:
            sys.stdout.write(
                '{}NOW:{}'.format(
                    self.prefix,
                    FrameDataEntry.WithPlusIfNeeded(
                        None,
                        self.get_frame_advantage()
                    )
                )
            )
            self.original_diff = self.get_frame_advantage()

    def close_window(self, result: PunishResult):
        self.result = result
        if result != PunishResult.NO_WINDOW:
            sys.stdout.write(
                'Closing punish window, result: {}'.format(self.result.name)
            )
