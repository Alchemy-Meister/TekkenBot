#!/usr/bin/env python3

# Copyright (c) 2019, Alchemy Meister
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice,this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""

"""

# pylint: disable=unused-wildcard-import,wildcard-import
from MoveInfoEnums import *  # NOQA

class BotSnapshot:
    """

    """

    def __init__(self, data_dict):
        """

        """
        # self.xyz = (
        #    data_dict['PlayerDataAddress.x'], data_dict['PlayerDataAddress.y'],
        #    data_dict['PlayerDataAddress.z']
        # )
        self.move_id = data_dict['PlayerDataAddress.move_id']
        self.simple_state = SimpleMoveStates(
            data_dict['PlayerDataAddress.simple_move_state'])
        self.attack_type = AttackType(
            data_dict['PlayerDataAddress.attack_type']
        )
        self.startup = data_dict['PlayerDataAddress.attack_startup']
        self.startup_end = data_dict['PlayerDataAddress.attack_startup_end']
        self.attack_damage = data_dict['PlayerDataAddress.attack_damage']
        self.complex_state = ComplexMoveStates(
            data_dict['PlayerDataAddress.complex_move_state'])
        self.damage_taken = data_dict['PlayerDataAddress.damage_taken']
        self.move_timer = data_dict['PlayerDataAddress.move_timer']
        self.recovery = data_dict['PlayerDataAddress.recovery']
        self.char_id = data_dict['PlayerDataAddress.char_id']
        self.throw_flag = data_dict['PlayerDataAddress.throw_flag']
        self.rage_flag = data_dict['PlayerDataAddress.rage_flag']
        self.input_counter = data_dict['PlayerDataAddress.input_counter']
        self.input_direction = InputDirectionCodes(
            data_dict['PlayerDataAddress.input_direction'])
        self.input_button = InputAttackCodes(
            data_dict['PlayerDataAddress.input_attack']
            % InputAttackCodes.xRAGE.value
        )
        self.rage_button_flag = (
            data_dict['PlayerDataAddress.input_attack']
            >= InputAttackCodes.xRAGE.value
        )
        self.stun_state = StunStates(data_dict['PlayerDataAddress.stun_type'])
        self.power_crush_flag = data_dict['PlayerDataAddress.power_crush'] > 0

        cancel_window_bitmask = data_dict['PlayerDataAddress.cancel_window']

        self.is_cancelable = (
            (CancelStatesBitmask.CANCELABLE.value & cancel_window_bitmask)
            == CancelStatesBitmask.CANCELABLE.value
        )
        self.is_bufferable = (
            (CancelStatesBitmask.BUFFERABLE.value & cancel_window_bitmask)
            == CancelStatesBitmask.BUFFERABLE.value
        )
        self.is_parry_1 = (
            (CancelStatesBitmask.PARRYABLE_1.value & cancel_window_bitmask)
            == CancelStatesBitmask.PARRYABLE_1.value
        )
        self.is_parry_2 = (
            (CancelStatesBitmask.PARRYABLE_2.value & cancel_window_bitmask)
            == CancelStatesBitmask.PARRYABLE_2.value
        )
        self.throw_tech = ThrowTechs(data_dict['PlayerDataAddress.throw_tech'])

        #self.highest_y = max(data_dict['PlayerDataAddress.y'])
        # self.lowest_y = min(data_dict['PlayerDataAddress.y'])

        # self.hitboxes = [
        #     data_dict['PlayerDataAddress.hitbox1'],
        #     data_dict['PlayerDataAddress.hitbox2'],
        #     data_dict['PlayerDataAddress.hitbox3'],
        #     data_dict['PlayerDataAddress.hitbox4'],
        #     data_dict['PlayerDataAddress.hitbox5']
        # ]
        self.skeleton = (
            data_dict['PlayerDataAddress.x'], data_dict['PlayerDataAddress.y'],
            data_dict['PlayerDataAddress.z']
        )

        self.active_xyz = (
            data_dict['PlayerDataAddress.activebox_x'],
            data_dict['PlayerDataAddress.activebox_y'],
            data_dict['PlayerDataAddress.activebox_z']
        )

        self.is_jump = (
            data_dict['PlayerDataAddress.jump_flags'] & 
            JumpFlagBitmask.JUMP.value == JumpFlagBitmask.JUMP.value
        )
        self.hit_outcome = HitOutcome(
            data_dict['PlayerDataAddress.hit_outcome']
        )
        self.mystery_state = data_dict['PlayerDataAddress.mystery_state']

        #self.movelist_to_use = data_dict['PlayerDataAddress.movelist_to_use']

        self.wins = data_dict['EndBlockPlayerDataAddress.round_wins']
        self.combo_counter = (
            data_dict['EndBlockPlayerDataAddress.display_combo_counter']
        )
        self.combo_damage = (
            data_dict['EndBlockPlayerDataAddress.display_combo_damage']
        )
        self.juggle_damage = (
            data_dict['EndBlockPlayerDataAddress.display_juggle_damage']
        )

        self.use_opponents_movelist = data_dict['use_opponent_movelist']
        self.movelist_parser = data_dict['movelist_parser']

        try:
            self.character_name = CharacterCodes(
                data_dict['PlayerDataAddress.char_id']
            ).name
        except KeyError:
            self.character_name = "UNKNOWN"

    # def PrintYInfo(self):
    #     print('{:.4f}, {:.4f}, {:.4f}'.format(
    #         self.highest_y, self.lowest_y, self.highest_y - self.lowest_y)
    #     )

    def is_character_name_loaded(self):
        """

        """
        return self.character_name != CharacterCodes.NOT_YET_LOADED.name

    def GetInputState(self):
        return (self.input_direction, self.input_button, self.rage_button_flag)

    def GetTrackingType(self):
        # if self.complex_state.value < 8:
        return self.complex_state
        # else:
        #    return ComplexMoveStates.UNKN

    def IsBlocking(self):
        return self.complex_state == ComplexMoveStates.BLOCK

    def IsGettingCounterHit(self):
        return self.hit_outcome in (
            HitOutcome.COUNTER_HIT_CROUCHING,
            HitOutcome.COUNTER_HIT_STANDING
        )

    def IsGettingGroundHit(self):
        return self.hit_outcome in (
            HitOutcome.GROUNDED_FACE_DOWN, HitOutcome.GROUNDED_FACE_UP
        )

    def IsGettingWallSplatted(self):
        return self.simple_state in (
            SimpleMoveStates.WALL_SPLAT_18, SimpleMoveStates.WALL_SPLAT_19
        )

    def IsGettingHit(self):
        return self.stun_state in (
            StunStates.BEING_PUNISHED, StunStates.GETTING_HIT
        )
        # TODO: make this more accurate
        # return (
        #    not self.is_cancelable
        #    and self.complex_state == ComplexMoveStates.RECOVERING
        #    and self.simple_state == SimpleMoveStates.STANDING_FORWARD
        #    and self.attack_damage == 0
        #    and self.startup == 0
        # )

    def IsHitting(self):
        return self.stun_state == StunStates.DOING_THE_HITTING

    def IsPunish(self):
        return self.stun_state == StunStates.BEING_PUNISHED

    def IsAttackMid(self):
        return self.attack_type == AttackType.MID

    def IsAttackUnblockable(self):
        return self.attack_type in {
            AttackType.HIGH_UNBLOCKABLE,
            AttackType.LOW_UNBLOCKABLE,
            AttackType.MID_UNBLOCKABLE
        }

    def IsAttackAntiair(self):
        return self.attack_type == AttackType.ANTIAIR_ONLY

    def IsAttackThrow(self):
        return self.throw_flag == 1

    def IsAttackLow(self):
        return self.attack_type == AttackType.LOW

    def IsInThrowing(self):
        return self.attack_type == AttackType.THROW

    def GetActiveFrames(self):
        return self.startup_end - self.startup + 1

    def IsAttackWhiffing(self):
        return self.complex_state in {
            ComplexMoveStates.END1,
            ComplexMoveStates.F_MINUS,
            ComplexMoveStates.RECOVERING,
            ComplexMoveStates.UN17,
            ComplexMoveStates.SS,
            ComplexMoveStates.WALK
        }

    def IsOnGround(self):
        return self.simple_state in {
            SimpleMoveStates.GROUND_FACEDOWN,
            SimpleMoveStates.GROUND_FACEUP
        }

    def IsBeingJuggled(self):
        return self.simple_state == SimpleMoveStates.JUGGLED

    def IsAirborne(self):
        return self.simple_state == SimpleMoveStates.AIRBORNE

    def IsHoldingUp(self):
        return self.input_direction == InputDirectionCodes.u

    def IsHoldingUpBack(self):
        return self.input_direction == InputDirectionCodes.ub

    def IsTechnicalCrouch(self):
        return self.simple_state in (
            SimpleMoveStates.CROUCH,
            SimpleMoveStates.CROUCH_BACK,
            SimpleMoveStates.CROUCH_FORWARD
        )

    def IsTechnicalJump(self):
        return self.is_jump
        # return self.simple_state in (
        #     SimpleMoveStates.AIRBORNE,
        #     SimpleMoveStates.AIRBORNE_26,
        #     SimpleMoveStates.AIRBORNE_24
        # )

    def IsHoming1(self):
        return self.complex_state == ComplexMoveStates.S_PLUS

    def IsHoming2(self):
        return self.complex_state == ComplexMoveStates.S

    def IsPowerCrush(self):
        return self.power_crush_flag

    def IsBeingKnockedDown(self):
        return self.simple_state == SimpleMoveStates.KNOCKDOWN

    def IsWhileStanding(self):
        return self.simple_state in {
            SimpleMoveStates.CROUCH, SimpleMoveStates.CROUCH_BACK,
            SimpleMoveStates.CROUCH_FORWARD
        }

    def IsWallSplat(self):
        # TODO: use the wall splat states in ComplexMoveStates move ids may
        # be different for 'big' characters
        return (
            self.move_id == 2396 or self.move_id == 2387
            or self.move_id == 2380 or self.move_id == 2382
        )

    def IsInRage(self):
        return self.rage_flag > 0

    def IsAbleToAct(self):
        # print(self.cwb)
        return self.is_cancelable

    def IsParryable1(self):
        return self.is_parry_1

    def IsParryable2(self):
        return self.is_parry_2

    def IsBufferable(self):
        return self.is_bufferable

    def IsAttackStarting(self):
        # return self.complex_state in {
        #     ComplexMoveStates.ATTACK_STARTING_1,
        #     ComplexMoveStates.ATTACK_STARTING_2,
        #     ComplexMoveStates.ATTACK_STARTING_3,
        #     ComplexMoveStates.ATTACK_STARTING_5,
        #     ComplexMoveStates.ATTACK_STARTING_6,
        #     ComplexMoveStates.ATTACK_STARTING_7
        # } #doesn't work on several of Kazuya's moves, maybe others
        if self.startup > 0:
            is_active = self.move_timer <= self.startup
            return is_active
        return False

    def get_movelist_to_use(self):
        """

        """
        return self.get_movelist_to_use
