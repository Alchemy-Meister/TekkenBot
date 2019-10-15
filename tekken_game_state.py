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

from __future__ import annotations

from collections import Counter
import logging
import math
import typing
import sys

# pylint: disable=wildcard-import
from MoveInfoEnums import *  # NOQA
from MoveDataReport import MoveDataReport
import MovelistParser

from constants.event import GameStateEvent
from constants.input import InputAttack, InputDirection
from constants.event import GraphicSettingsChangeEvent
from constants.graphic_settings import ScreenMode

from log import Formatter

from patterns.observer import Publisher

import win32.kernel32 as kernel32
import win32.user32 as user32

from tekken import ProcessIOManager

if typing.TYPE_CHECKING:
    from tekken import GameSnapshot

class TekkenGameState:
    """
    """
    def __init__(self):
        self.game_io_manager = ProcessIOManager()
        self.duplicate_frame_obtained = 0
        self.state_log = []
        self.graphic_settings = None
        self.mirrored_state_log = []
        self.is_mirrored = False
        self.futurestate_log = None

        logging_handler = logging.StreamHandler(sys.stdout)
        logging_handler.setFormatter(Formatter())
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging_handler)

        self.graphic_settings_publisher = Publisher(GraphicSettingsChangeEvent)

    def get_reader(self):
        return self.game_io_manager.process_reader

    def get_writer(self):
        return self.game_io_manager.process_writer

    def is_pid_valid(self):
        return self.game_io_manager.is_pid_valid()

    def update(self, buffer=0):
        """
        """
        game_state = self.game_io_manager.update(buffer)

        game_graphic_settings = game_state[0]
        game_battle_state = game_state[1]

        if game_battle_state is not None:
            # we don't run perfectly in sync, if we get back the same frame,
            # throw it away
            if(
                    not self.state_log
                    or game_battle_state.frame_count
                    != self.state_log[-1].frame_count
            ):
                self.duplicate_frame_obtained = 0

                frames_lost = 0
                if self.state_log:
                    frames_lost = (
                        game_battle_state.frame_count
                        - self.state_log[-1].frame_count - 1
                    )

                for i in range(min(7 - buffer, frames_lost)):
                    dropped_game_state = self.game_io_manager.read_update(
                        min(7, frames_lost + buffer) - i
                    )
                    dropped_game_graphic_settings = dropped_game_state[0]
                    dropped_game_battle_state = dropped_game_state[1]

                    if dropped_game_graphic_settings is not None:
                        self.compare_graphic_settings(
                            dropped_game_graphic_settings
                        )

                    if dropped_game_battle_state is not None:
                        self.append_game_data(dropped_game_battle_state)

                self.append_game_data(game_battle_state)
                return True
            if game_battle_state.frame_count == self.state_log[-1].frame_count:
                self.duplicate_frame_obtained += 1
        if game_graphic_settings is not None:
            self.compare_graphic_settings(game_graphic_settings)
        return False

    def append_game_data(self, game_data: GameSnapshot):
        if not self.is_mirrored:
            self.state_log.append(game_data)
            self.mirrored_state_log.append(game_data.from_mirrored())
        else:
            self.state_log.append(game_data.from_mirrored())
            self.mirrored_state_log.append(game_data)

        if len(self.state_log) > 300:
            self.state_log.pop(0)
            self.mirrored_state_log.pop(0)

    def compare_graphic_settings(self, graphic_settings):
        graphic_settings_changed = False
        if not graphic_settings.equal_screen_mode(self.graphic_settings):
            self.logger.debug(
                'TEKKEN7 screen mode changed from %s to %s',
                self.graphic_settings.screen_mode.name
                if self.graphic_settings else None,
                graphic_settings.screen_mode.name
            )
            graphic_settings_changed = True
            self.graphic_settings_publisher.dispatch(
                GraphicSettingsChangeEvent.SCREEN_MODE,
                graphic_settings.screen_mode
            )
        if(
                not graphic_settings.equal_resolution(self.graphic_settings)
        ):
            self.logger.debug(
                'TEKKEN7 resolution changed from %s to %s',
                getattr(self.graphic_settings, 'resolution', None),
                graphic_settings.resolution
            )
            graphic_settings_changed = True
            self.graphic_settings_publisher.dispatch(
                GraphicSettingsChangeEvent.RESOLUTION,
                graphic_settings.resolution
            )
        if not graphic_settings.equal_position(self.graphic_settings):
            self.logger.debug(
                'TEKKEN7 position changed from %s to %s',
                getattr(self.graphic_settings, 'position', None),
                graphic_settings.position
            )
            graphic_settings_changed = True
            self.graphic_settings_publisher.dispatch(
                GraphicSettingsChangeEvent.POSITION,
                graphic_settings.position
            )
        if graphic_settings_changed:
            self.graphic_settings = graphic_settings

    def flip_mirror(self):
        self.state_log, self.mirrored_state_log = (
            self.mirrored_state_log, self.state_log
        )
        self.is_mirrored = not self.is_mirrored

    def back_to_the_future(self, frames):
        if self.futurestate_log is not None:
            raise AssertionError(
                'Already called BackToTheFuture, '
                'need to return to the present first, Marty'
            )
        self.futurestate_log = self.state_log[0 - frames:]
        self.state_log = self.state_log[:0 - frames]

    def return_to_present(self):
        if self.futurestate_log is None:
            raise AssertionError(
                "We're already in the present, Marty, what are you doing?")
        self.state_log += self.futurestate_log
        self.futurestate_log = None

    def is_game_happening(self):
        return (
            not self.game_io_manager.process_reader
            .is_state_reacquisition_required()
        )

    def is_tekken_visible(self):
        try:
            return user32.is_window(
                self.game_io_manager.process_reader.window_handle
            )
        except OSError:
            return False

    def is_bot_on_left(self):
        is_player_one_on_left = (
            self.game_io_manager.process_reader
            .original_facing == self.state_log[-1].facing_bool
        )
        if not self.is_mirrored:
            return is_player_one_on_left
        return not is_player_one_on_left

    def get_bot_health(self):
        return max(0, 170 - self.state_log[-1].bot.damage_taken)

    def get_dist(self):
        return self.state_log[-1].get_distance()

    def did_opp_combo_counter_just_start_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return (
                self.state_log[0 - frames_ago].opp.combo_counter == 1
                and self.state_log[0 - frames_ago - 1].opp.combo_counter == 0
            )
        return False

    def did_opp_combo_counter_just_end_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return (
                self.state_log[0 - frames_ago].opp.combo_counter == 0
                and self.state_log[0 - frames_ago - 1].opp.combo_counter > 0
            )
        return False

    def get_opp_combo_damage_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return self.state_log[0 - frames_ago].opp.combo_damage
        return 0

    def get_opp_combo_hits_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return self.state_log[0 - frames_ago].opp.combo_counter
        return 0

    def get_opp_juggle_damage_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return self.state_log[0 - frames_ago].opp.juggle_damage
        return 0

    def did_bot_start_getting_punished_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return self.state_log[0 - frames_ago].bot.is_punish()
        else:
            return False

    def did_opp_start_getting_punished_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return self.state_log[0 - frames_ago].opp.is_punish()
        else:
            return False

    def bot_frames_until_recovery_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return (
                self.state_log[0 - frames_ago].bot.recovery
                - self.state_log[0 - frames_ago].bot.move_timer
            )
        else:
            return 99

    def opp_frames_until_recovery_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return (
                self.state_log[0 - frames_ago].opp.recovery
                - self.state_log[0 - frames_ago].opp.move_timer
            )
        else:
            return 99

    def is_bot_blocking(self):
        return self.state_log[-1].bot.is_blocking()

    def is_bot_getting_counter_hit(self):
        return self.state_log[-1].bot.is_getting_counter_hit()

    def is_bot_getting_hit_on_ground(self):
        return self.state_log[-1].bot.is_getting_ground_hit()

    def is_opp_blocking(self):
        return self.state_log[-1].opp.is_blocking()

    def is_opp_getting_hit(self):
        return self.state_log[-1].opp.is_getting_hit()

    def is_bot_getting_hit(self):
        return self.state_log[-1].bot.is_getting_hit()
        # return self.get_frames_since_bot_took_damage() < 15

    def is_opp_hitting(self):
        return self.state_log[-1].opp.is_hitting()

    def is_bot_started_getting_hit(self):
        if len(self.state_log) > 2:
            return (
                self.is_bot_getting_hit() and
                not self.state_log[-2].bot.is_getting_hit()
            )
        return False

    def is_bot_started_being_thrown(self):
        if len(self.state_log) > 2:
            return (
                self.is_bot_being_thrown()
                and not self.state_log[-2].opp.is_in_throwing()
            )
        return False

    def is_bot_coming_out_of_block(self):
        if len(self.state_log) >= 2:
            previous_state = self.state_log[-2].bot.is_blocking()
            current_state = self.state_log[-1].bot.is_blocking()
            return previous_state and not current_state
        return False

    def get_recovery_of_move_id(self, move_id):
        largest_time = -1
        for state in reversed(self.state_log):
            if state.bot.move_id == move_id:
                largest_time = max(largest_time, state.bot.move_timer)
        return largest_time

    def get_last_move_id(self):
        for state in reversed(self.state_log):
            if state.bot.startup > 0:
                return state.bot.move_id
        return -1

    def get_bot_just_move_id(self):
        return self.state_log[-2].bot.move_id

    def did_bot_recently_do_move(self):
        if len(self.state_log) > 5:
            return (
                self.state_log[-1].bot.move_timer
                < self.state_log[-5].bot.move_timer
            )
        return False

    def did_bot_recently_do_damage(self):
        if len(self.state_log) > 10:
            if(
                    self.state_log[-1].opp.damage_taken
                    > self.state_log[-20].opp.damage_taken
            ):
                return True
        return False

    def is_bot_crouching(self):
        return self.state_log[-1].bot.is_technical_crouch()

    def is_opp_attack_mid(self):
        return self.state_log[-1].opp.is_attack_mid()

    def is_opp_attack_unblockable(self):
        return self.state_log[-1].opp.is_attack_unblockable()

    def is_opp_attack_antiair(self):
        return self.state_log[-1].opp.is_attack_antiair()

    def is_opp_attack_throw(self):
        return self.state_log[-1].opp.is_attack_throw()

    def is_opp_attack_low(self):
        return self.state_log[-1].opp.is_attack_low()

    def is_opp_attacking(self):
        return self.state_log[-1].opp.is_attack_starting()

    # only finds landing canceled moves?
    def get_opp_move_interrupted_frames(self):
        if len(self.state_log) > 3:
            if self.state_log[-1].opp.move_timer == 1:
                interrupted_frames = self.state_log[-2].opp.move_timer - (
                    self.state_log[-3].opp.move_timer + 1)
                if interrupted_frames > 0:
                    # landing animation causes move_timer to go *up* to the end
                    # of the move
                    return interrupted_frames
        return 0

    def get_frames_until_out_of_block(self):
        # print(self.state_log[-1].bot.block_flags)
        if not self.is_bot_blocking():
            return 0
        recovery = self.state_log[-1].bot.recovery
        block_frames = self.get_frames_bot_has_been_blocking_attack()
        return (recovery) - block_frames

    def get_frame_progress_of_opp_attack(self):
        most_recent_state_with_attack = None
        frames_since_last_attack = 0
        for state in reversed(self.state_log):
            if most_recent_state_with_attack is None:
                if state['p2_attack_startup'] > 0:
                    most_recent_state_with_attack = state
            elif(
                    state['p2_move_id']
                    == most_recent_state_with_attack.opp.move_id
                    and state.opp.move_timer
                    < most_recent_state_with_attack.opp.move_timer
            ):
                frames_since_last_attack += 1
            else:
                break
        return frames_since_last_attack

    def get_frames_bot_has_been_blocking_attack(self):
        if not self.state_log[-1].bot.is_blocking():
            return 0

        opponent_move_id = self.state_log[-1].opp.move_id
        opponent_move_timer = self.state_log[-1].opp.move_timer

        frames_spent_blocking = 0
        for state in reversed(self.state_log):
            if(
                    state.bot.is_blocking()
                    and state.opp.move_timer <= opponent_move_timer
                    and state.opp.move_id == opponent_move_id
                    and state.opp.move_timer > state.opp.startup
            ):
                frames_spent_blocking += 1
                opponent_move_timer = state.opp.move_timer
            else:
                break
        return frames_spent_blocking

    def is_opp_whiffing_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return self.state_log[0 - frames_ago].opp.is_attack_whiffing()
        else:
            return False

    def is_opp_whiffing(self):
        return self.state_log[-1].opp.is_attack_whiffing()

    def is_bot_whiffing(self):
        return self.state_log[-1].bot.is_attack_whiffing()

    def is_bot_while_standing(self):
        return self.state_log[-1].bot.is_while_standing()

    def get_bot_frames_until_recovery_ends(self):
        return (
            self.state_log[-1].bot.recovery - self.state_log[-1].bot.move_timer
        )

    def is_bot_move_changed(self):
        if len(self.state_log) > 2:
            return (
                self.state_log[-1].bot.move_id
                != self.state_log[-2].bot.move_id
            )
        return False

    def is_bot_whiffing_alt(self):
        current_bot = self.state_log[-1].bot
        if current_bot.startup == 0:  # we might still be in recovery
            for _, state in enumerate(reversed(self.state_log)):
                if state.bot.startup > 0:
                    pass
        else:
            return current_bot.is_attack_whiffing()

    def get_opponent_move_id_with_character_marker(self):
        character_marker = self.state_log[-1].opp.char_id
        return self.state_log[-1].opp.move_id + character_marker * 10000000

    def get_opp_startup(self):
        return self.state_log[-1].opp.startup

    def get_bot_startup_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return self.state_log[0 - frames_ago].bot.startup
        return False

    def get_opp_active_frames(self):
        return self.state_log[-1].opp.get_active_frames()

    def get_last_active_frame_hit_was_on(self, frames):
        return_next_state = False
        for state in reversed(self.state_log[-(frames + 2):]):
            if return_next_state:
                return (state.opp.move_timer - state.opp.startup) + 1
            if state.bot.move_timer == 1:
                return_next_state = True
        return 0

    def get_opp_active_frames_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return self.state_log[0 - frames_ago].opp.get_active_frames()
        return 0

    def get_opp_recovery(self):
        return self.state_log[-1].opp.recovery

    def get_opp_frames_till_next_move(self):
        return self.get_opp_recovery() - self.get_opp_move_timer()

    def get_bot_frames_till_next_move(self):
        return self.get_bot_recovery() - self.get_bot_move_timer()

    def get_bot_recovery(self):
        return self.state_log[-1].bot.recovery

    def get_opp_move_id(self):
        return self.state_log[-1].opp.move_id

    def get_opp_attack_type(self):
        return self.state_log[-1].opp.attack_type

    def get_opp_attack_type_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return self.state_log[0 - frames_ago].opp.attack_type
        return False

    def get_bot_move_id(self):
        return self.state_log[-1].bot.move_id

    def get_bot_startup(self):
        return self.state_log[-1].bot.startup

    def get_bot_move_timer(self):
        return self.state_log[-1].bot.move_timer

    def get_opp_move_timer(self):
        return self.state_log[-1].opp.move_timer

    def is_bot_attack_starting(self):
        return (self.get_bot_startup() - self.get_bot_move_timer()) > 0

    def get_opp_time_until_impact(self):
        return (
            self.get_opp_startup() - self.state_log[-1].opp.move_timer
            + self.state_log[-1].opp.get_active_frames()
        )

    def get_bot_time_until_impact(self):
        return (
            self.get_bot_startup() - self.state_log[-1].bot.move_timer
            + self.state_log[-1].bot.get_active_frames()
        )

    def is_bot_on_ground(self):
        return self.state_log[-1].bot.is_on_ground()

    def is_bot_being_knocked_down(self):
        return self.state_log[-1].bot.is_being_knocked_down()

    def is_bot_being_wall_splatted(self):
        return self.state_log[-1].bot.is_getting_wall_splatted()

    def get_opp_damage(self):
        return self.state_log[-1].opp.attack_damage

    def get_most_recent_opp_damage(self):
        if self.state_log[-1].opp.attack_damage > 0:
            return self.state_log[-1].opp.attack_damage

        current_health = self.state_log[-1].bot.damage_taken

        for state in reversed(self.state_log):
            if state.bot.damage_taken < current_health:
                return current_health - state.bot.damage_taken
        return 0

    def get_opp_latest_non_zero_startup_and_damage(self):
        for state in reversed(self.state_log):
            damage = state.opp.attack_damage
            startup = state.opp.startup
            if damage > 0 or startup > 0:
                return (startup, damage)
        return (0, 0)

    def is_bot_just_grounded(self):
        if len(self.state_log) > 2:
            return (
                self.state_log[-1].bot.is_on_ground()
                and not self.state_log[-2].bot.is_on_ground()
                and not self.state_log[-2].bot.is_being_juggled()
                and not self.state_log[-2].bot.is_being_knocked_down()
            )
        return False

    def is_bot_being_juggled(self):
        return self.state_log[-1].bot.is_being_juggled()

    def is_bot_started_being_juggled(self):
        if len(self.state_log) > 2:
            return (
                self.state_log[-1].bot.is_being_juggled()
                and not self.state_log[-2].bot.is_being_juggled()
            )
        return False

    def is_bot_being_thrown(self):
        return self.state_log[-1].opp.is_in_throwing()

    def is_opp_wall_splat(self):
        return self.state_log[-1].opp.is_wall_splat()

    def did_bot_just_take_damage(self, frames_ago=1):
        if len(self.state_log) > frames_ago:
            return max(
                0,
                self.state_log[0 - frames_ago].bot.damage_taken
                - self.state_log[0 - frames_ago - 1].bot.damage_taken
            )
        return 0

    def did_opp_just_take_damage(self, frames_ago=1):
        if len(self.state_log) > frames_ago:
            return max(
                0,
                self.state_log[0 - frames_ago].opp.damage_taken
                - self.state_log[0 - frames_ago - 1].opp.damage_taken
            )
        return 0

    def did_opp_take_damage_during_startup(self):
        current_damage_taken = self.state_log[-1].opp.damage_taken
        current_move_timer = self.state_log[-1].opp.move_timer
        for state in reversed(self.state_log):
            if state.opp.damage_taken < current_damage_taken:
                return True
            if current_move_timer < state.opp.move_timer:
                return False
            current_move_timer = state.opp.move_timer
        return False

    def did_bot_timer_interrupt_x_moves_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return (
                self.state_log[0 - frames_ago].bot.move_timer
                < self.state_log[0 - frames_ago - 1].bot.move_timer
            )
        return False

    def did_bot_start_getting_hit_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return (
                self.state_log[0 - frames_ago].bot.is_getting_hit()
                and not self.state_log[0 - frames_ago - 1].bot.is_getting_hit()
            )
        return False

    def did_opp_start_getting_hit_x_frames_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return (
                self.state_log[0 - frames_ago].opp.is_getting_hit()
                and not self.state_log[0 - frames_ago - 1].opp.is_getting_hit()
            )
        return False

    def did_bot_id_change_x_moves_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return (
                self.state_log[0 - frames_ago].bot.move_id
                != self.state_log[0 - frames_ago - 1].bot.move_id
            )
        return False

    def did_opp_id_change_x_moves_ago(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return (
                self.state_log[0 - frames_ago].opp.move_id
                != self.state_log[0 - frames_ago - 1].opp.move_id
            )
        return False

    def get_bot_elapsed_frames_of_rage_move(self, rage_move_startup):
        frozenFrames = 0
        last_move_timer = -1
        for state in reversed(self.state_log[-rage_move_startup:]):
            if state.bot.move_timer == last_move_timer:
                frozenFrames += 1
            last_move_timer = state.bot.move_timer
        return rage_move_startup - frozenFrames

    def is_opp_in_rage(self):
        return self.state_log[-1].opp.is_in_rage()

    def did_opponent_use_rage_recently(self, recentlyFrames):
        if not self.is_opp_in_rage():
            for state in reversed(self.state_log[-recentlyFrames:]):
                if state.opp.is_in_rage():
                    return True
        return False

    def get_frames_since_bot_took_damage(self):
        damage_taken = self.state_log[-1].bot.damage_taken
        for i, state in enumerate(reversed(self.state_log)):
            if state.bot.damage_taken < damage_taken:
                return i
        return 1000

    def get_last_opp_snapshot_with_different_move_id(self):
        moveId = self.state_log[-1].opp.move_id
        for state in reversed(self.state_log):
            if state.opp.move_id != moveId:
                return state
        return self.state_log[-1]

    def get_last_opp_with_different_move_id(self):
        return self.get_last_opp_snapshot_with_different_move_id().opp

    def get_opp_last_move_input(self):
        oppMoveId = self.state_log[-1].opp.move_id
        input = []
        for state in reversed(self.state_log):
            if (
                    state.opp.move_id != oppMoveId
                    and state.opp.get_input_state()[1] != InputAttack.NULL
            ):
                input.append(state.opp.get_input_state())
                return input

        return [(InputDirectionCodes.N, InputAttack.NULL, False)]

    def get_current_opp_move_string(self):
        if self.state_log[-1].opp.movelist_parser != None:
            move_id = self.state_log[-1].opp.move_id
            previous_move_id = -1

            input_array = []

            i = len(self.state_log)

            while True:
                next_move, last_move_was_empty_cancel = (
                    self.get_opp_move_string(
                        move_id, previous_move_id
                    )
                )
                next_move = str(next_move)

                if last_move_was_empty_cancel:
                    input_array[-1] = ''

                input_array.append(next_move)

                if(
                        self.state_log[-1].opp.movelist_parser
                        .can_be_done_from_neutral(move_id)
                ):
                    break

                while True:
                    i -= 1
                    if i < 0:
                        break
                    if self.state_log[i].opp.move_id != move_id:
                        previous_move_id = move_id
                        move_id = self.state_log[i].opp.move_id
                        break
                if i < 0:
                    break

            clean_input_array = reversed(
                [a for a in input_array if len(a) > 0])
            return ','.join(clean_input_array)
        else:
            return 'N/A'

    def get_opp_move_string(self, move_id, previous_move_id):
        return self.state_log[-1].opp.movelist_parser.input_for_move(
            move_id, previous_move_id
        )

    def has_opp_returned_to_neutral_from_move_id(self, move_id):
        for state in reversed(self.state_log):
            if state.opp.move_id == move_id:
                return False
            if state.opp.movelist_parser.can_be_done_from_neutral(
                    state.opp.move_id
            ):
                return True
        return True

    def get_frame_data_of_current_opp_move(self):
        if self.state_log[-1].opp.startup > 0:
            opp = self.state_log[-1].opp
        else:
            game_state = self.get_last_opp_snapshot_with_different_move_id()
            if game_state != None:
                opp = game_state.opp
            else:
                opp = self.state_log[-1].opp
        return self.get_frame_data(self.state_log[-1].bot, opp)

    def get_frame_data_of_current_bot_move(self):
        return self.get_frame_data(
            self.state_log[-1].opp, self.state_log[-1].bot
        )

    def get_frame_data(self, defendingPlayer, attackingPlayer):
        return (
            (defendingPlayer.recovery + attackingPlayer.startup)
            - attackingPlayer.recovery
        )

    def get_bot_char_id(self):
        char_id = self.state_log[-1].bot.char_id
        print("Character: " + str(char_id))
        return char_id

    def is_fulfill_jump_fallback_conditions(self):
        if len(self.state_log) > 10:
            if (
                    self.state_log[-7].bot.is_airborne()
                    and self.state_log[-7].opp.is_airborne()
            ):
                if (
                        not self.state_log[-8].bot.is_airborne()
                        or not self.state_log[-8].opp.is_airborne()
                ):
                    for state in self.state_log[-10:]:
                        if not(
                                state.bot.is_holding_up()
                                or state.opp.is_holding_up()
                        ):
                            return False
                    return True
        return False

    def is_opp_able_to_act(self):
        return self.state_log[-1].opp.is_cancelable

    def get_bot_input_state(self):
        return self.state_log[-1].bot.get_input_state()

    def get_opp_input_state(self):
        return self.state_log[-1].opp.get_input_state()

    def get_bot_name(self):
        return self.state_log[-1].bot.character_name

    def get_opp_name(self):
        return self.state_log[-1].opp.character_name

    def get_bot_throw_tech(self, activeFrames):
        for state in reversed(self.state_log[-activeFrames:]):
            tech = state.bot.throw_tech
            if tech != ThrowTechs.NONE:
                return tech
        return ThrowTechs.NONE

    def get_opp_tracking_type(self, startup):
        if len(self.state_log) > startup:
            complex_states = [ComplexMoveStates.UNKN]
            for state in reversed(self.state_log[-startup:]):
                if -1 < state.opp.get_traicking_type().value < 8:
                    complex_states.append(state.opp.get_traicking_type())
            return Counter(complex_states).most_common(1)[0][0]
        else:
            return ComplexMoveStates.F_MINUS

    def get_opp_technical_states(self, startup):

        #opp_id = self.state_log[-1].opp.move_id
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

        previous_state = None
        skipped_frames_counter = 0
        frozen_frames_counter = 0
        for i, state in enumerate(reversed(self.state_log[-startup:])):
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
                tc_frames.append(state.opp.is_technical_crouch())
                tj_frames.append(state.opp.is_technical_jump())
                cancel_frames.append(state.opp.is_cancelable)
                buffer_frames.append(state.opp.is_bufferable)
                pc_frames.append(state.opp.is_power_crush)
                homing_frames1.append(state.opp.is_homing1())
                homing_frames2.append(state.opp.is_homing2())
                parryable_frames1.append(state.opp.is_parry1)
                parryable_frames2.append(state.opp.is_parry2)
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

    def is_fight_over(self):
        return self.duplicate_frame_obtained > 5

    def was_timer_reset(self):
        if len(self.state_log) > 2:
            return (
                self.state_log[-1].timer_frames_remaining
                > self.state_log[-2].timer_frames_remaining
            )
        return False

    def did_timer_start_ticking(self, buffer):
        return self.state_log[-1].timer_frames_remaining == 3600 - 1 - buffer

    def was_fight_reset(self):
        false_reset_buffer = 0
        if len(self.state_log) > 2:
            return (
                self.state_log[-1].frame_count < self.state_log[-2].frame_count
                and self.state_log[-2].frame_count > false_reset_buffer
            )
        return False

    def get_timer(self, frames_ago):
        if len(self.state_log) > frames_ago:
            return self.state_log[-frames_ago].timer_frames_remaining
        return False

    def get_round_number(self):
        return self.state_log[-1].opp.wins + self.state_log[-1].bot.wins + 1

    def get_opp_round_summary(self, frames_ago):
        if len(self.state_log) > frames_ago:
            opp = self.state_log[-frames_ago].opp
            bot = self.state_log[-frames_ago].bot
            return (opp.wins, bot.damage_taken)
        return (0, 0)

    def get_range_of_move(self):
        move_timer = self.state_log[-1].opp.move_timer
        opp_id = self.state_log[-1].opp.move_id
        for state in reversed(self.state_log):
            starting_skeleton = state.opp.skeleton
            bot_skeleton = state.bot.skeleton
            old_dist = state.get_distance()
            if move_timer < state.opp.move_timer:
                break
            if opp_id != state.opp.move_id:
                break
            move_timer = state.opp.move_timer
        ending_skeleton = self.state_log[-1].opp.skeleton

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

    def is_bot_using_opp_movelist(self):
        return self.state_log[-1].bot.use_opponents_movelist

    def get_current_bot_move_name(self):
        move_id = self.state_log[-1].bot.move_id
        return self.get_opp_move_name(
            move_id, self.state_log[-1].bot.use_opponents_movelist,
            is_for_bot=True
        )

    def get_current_opp_move_name(self):
        move_id = self.state_log[-1].opp.move_id
        return self.get_opp_move_name(
            move_id, self.state_log[-1].opp.use_opponents_movelist,
            is_for_bot=False
        )

    def get_opp_move_name(
            self, move_id, use_opponents_movelist, is_for_bot=False
    ):
        if move_id > 30000:
            return 'Universal_{}'.format(move_id)

        try:
            if (
                    not self.is_mirrored and not is_for_bot
                    or self.is_mirrored and is_for_bot
            ):
                if not use_opponents_movelist:
                    movelist = (
                        self.game_io_manager.process_reader.p2_movelist_names
                    )
                else:
                    movelist = (
                        self.game_io_manager.process_reader.p1_movelist_names
                    )
            else:
                if not use_opponents_movelist:
                    movelist = (
                        self.game_io_manager.process_reader.p1_movelist_names
                    )
                else:
                    movelist = (
                        self.game_io_manager.process_reader.p2_movelist_names
                    )

            return movelist[(move_id * 2) + 4].decode('utf-8')
        except:
            return "ERROR"

    def is_tekken_foreground_wnd(self):
        return self.game_io_manager.process_reader.is_tekken_foreground_wnd()

    def is_in_battle(self):
        return self.game_io_manager.process_reader.is_in_battle
