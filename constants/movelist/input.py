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

from constants.complex_enum import ComplexEnum, ComplexEnumMember

class MovelistInput(ComplexEnum):
    NULL = ComplexEnumMember(0x0)
    DOWN_BACK = ComplexEnumMember(0x2, printable_name='d/b')
    DOWN = ComplexEnumMember(0x4, printable_name='d')
    DOWN_FORWARD = ComplexEnumMember(0x8, printable_name='d/f')
    BACK = ComplexEnumMember(0x10, printable_name='b')
    NEUTRAL = ComplexEnumMember(0x20)
    FORWARD = ComplexEnumMember(0x40, printable_name='f')
    UP_BACK = ComplexEnumMember(0x80, printable_name='u/b')
    UP = ComplexEnumMember(0x100, printable_name='u')
    UP_FORWARD = ComplexEnumMember(0x200, printable_name='u/f')

    #the following codes exist only in the movelist, not in player data
    FULL_CROUCH = ComplexEnumMember(6, printable_name='FC')
    d_df = ComplexEnumMember(0xc, printable_name='') #down or down forward but not down back
    _d = ComplexEnumMember(0xe, printable_name='') #sometimes d as well??
    UNK_12 = ComplexEnumMember(0x12, printable_name='')
    UNK_2e = ComplexEnumMember(0x2e, printable_name='') #guard?
    UNK_48 = ComplexEnumMember(0x48, printable_name='') #crouch turn while holding down?
    UNK_5e = ComplexEnumMember(0x5e, printable_name='') #pitcher glove cancel, B after U+2+3 in TTT2
    UNK_60 = ComplexEnumMember(0x60, printable_name='')
    RUNx = ComplexEnumMember(0x70, printable_name='') #actually BT??? sometimes running???
    _ub = ComplexEnumMember(0x90, printable_name='') # item command? u/b+1 for king
    UNK_92 = ComplexEnumMember(0x92, printable_name='') # possible alternate u/b input?
    UNK_104 = ComplexEnumMember(0x104, printable_name='') #item command?
    FACE_DOWN = ComplexEnumMember(0x120, printable_name='')
    LILI_UP_FORWARD = ComplexEnumMember(0x240, printable_name='u/f')
    UNK_248 = ComplexEnumMember(0x248, printable_name='') #???
    UNK_380 = ComplexEnumMember(0x380, printable_name='') #Vp_sJUMPr00 roll jump?
    UNK_38a = ComplexEnumMember(0x38a, printable_name='')
    UNK_3ae = ComplexEnumMember(0x3ae, printable_name='')
    UNK_3c0 = ComplexEnumMember(0x3c0, printable_name='') #all lead back to standing
    UNK_3de = ComplexEnumMember(0x3de, printable_name='')
    UNK_3ec = ComplexEnumMember(0x3ec, printable_name='')
    UNK_3ee = ComplexEnumMember(0x3ee, printable_name='') #Eliza's sleep cancel, so like, NOT holding b
    WHILE_STANDING = ComplexEnumMember(0x3f0, printable_name='WS') #not standing backturn?
    UNK_402 = ComplexEnumMember(0x402, printable_name='')
    UNK_404 = ComplexEnumMember(0x404, printable_name='')
    UNK_408 = ComplexEnumMember(0x408, printable_name='')
    UNK_40e = ComplexEnumMember(0x40e, printable_name='')

    END = ComplexEnumMember(0x8000, printable_name='')
    DOUBLE_FORWARD = ComplexEnumMember(0x8001, printable_name='ff')
    DOUBLE_BACK = ComplexEnumMember(0x8002, printable_name='bb')
    SIDE_STEP_UP = ComplexEnumMember(0x8003, printable_name='SS')
    SIDE_STEP_DOWN = ComplexEnumMember(0x8004, printable_name='SS')
    UNK_800b = ComplexEnumMember(0x800b, printable_name='') #hit standing? block standing?
    UNK_800c = ComplexEnumMember(0x800c, printable_name='') #only exists on move_id=0?

    ART_OF_PHOENIX_DOWN = ComplexEnumMember(0x8012, printable_name='')

    CLOTHESLINE_PRESS = ComplexEnumMember(0x8016, printable_name='d/b,b,d/b1+2')

    TOMBSTONE_PILE_DRIVER = ComplexEnumMember(0x8018, printable_name='d/b,f2+4')
    UNK_8019 = ComplexEnumMember(0x8019, printable_name='')  # guard
    UNK_801a = ComplexEnumMember(0x801a, printable_name='')  # guard
    UNK_801b = ComplexEnumMember(0x801b, printable_name='')  # guard

    CANNONBALL_BUSTER = ComplexEnumMember(0x801E, printable_name='2,2,1+2')
    POWER_BOMB = ComplexEnumMember(0x801F, printable_name='1,2,3+4')

    MANHATTAN_DROP = ComplexEnumMember(0x8020, printable_name='3+4,1+2,1+2+3')
    VICTORY_BOMB = ComplexEnumMember(0x8021, printable_name='1,2,3+4,1+2')
    MUSCLE_BUSTER_COMBO = ComplexEnumMember(
        0x8022, printable_name='3,1,2,3+4,1+2'
    )

    UNK_803a = ComplexEnumMember(0x803a, printable_name='')  # standing

    GIANT_SWING = ComplexEnumMember(0x804e, printable_name='f,b,d/b,d,d/f,f1')
    TIJUANA_TWISTER = ComplexEnumMember(
        0x804f, printable_name='f,b,d/b,d,d/f,f2'
    )

    BOSTON_CRAB = ComplexEnumMember(0x8064, printable_name='1+2,3,4,1+2')
    DOUBLE_ARM_FACE_BUSTER = ComplexEnumMember(0x8065, printable_name='')

    BACKDROP = ComplexEnumMember(0x8077, printable_name='2,1,1+2')

    GIANT_SWING_COMBO = ComplexEnumMember(0x807A, printable_name='2,1,3,4')
    FLAPJACK = ComplexEnumMember(0x807B, printable_name='1+2,1+2')

    MUSCLE_BUSTER = ComplexEnumMember(0x8090, printable_name='b,d/b,b1+2')

    RUN_CHOP = ComplexEnumMember(0x80ac, printable_name='')  # run chop
    RUN_KICK = ComplexEnumMember(0x80ae, printable_name='')  # run chop

    TOMAHAWK = ComplexEnumMember(0x80AF, printable_name='fff2+4')

    RUN_1 = ComplexEnumMember(0x80b0, printable_name='')  # run lp?
    RUN_2 = ComplexEnumMember(0x80b1, printable_name='')  # run rp?
    RUN_3 = ComplexEnumMember(0x80b2, printable_name='')  # run lk?
    RUN_4 = ComplexEnumMember(0x80b3, printable_name='')  # run rk?

    #qcf states for eliza, all the ways to make a qcf, maybe storing the input
    qcf_fb = ComplexEnumMember(0x80fb, printable_name='') #qcf+1 # this b-f for Kazumi
    # TODO input can also be 1+2,1,2,1+2+4
    REVERSE_SPECIAL_STRECH_BOMB = ComplexEnumMember(
        0x80fc, printable_name='1+2,1,2,1+2+3'
    )
    #qcf_fc = ComplexEnumMember(0x80fc, printable_name='') #qcf+2
    qcf_fd = ComplexEnumMember(0x80fd, printable_name='') #qcf+1
    # TODO Also Geese's Hishou Nichirin Zan f,d,d/f2
    BACKDROP_RSSB = ComplexEnumMember(0x80fe, printable_name='3+4,1+2')
    # qcf_fe = ComplexEnumMember(0x80fe, printable_name='') #qcf+2
    qcf_ff = ComplexEnumMember(0x80ff, printable_name='')  #EX only
    qcf_100 = ComplexEnumMember(0x8100, printable_name='')  # EX only
    qcf_101 = ComplexEnumMember(0x8101, printable_name='')  # No fireball?
    qcf_102 = ComplexEnumMember(0x8102, printable_name='')  # No fireball?
    qcf_103 = ComplexEnumMember(0x8103, printable_name='')  # super (double qcf)
    qcf_104 = ComplexEnumMember(0x8104, printable_name='')  # super (double qcf)

    #dp states
    dp_0b = ComplexEnumMember(0x8010b, printable_name='') #EX
    dp_0c = ComplexEnumMember(0x8010c, printable_name='')  # EX
    dp_0d = ComplexEnumMember(0x8010d, printable_name='')  # 1
    dp_0e = ComplexEnumMember(0x8010e, printable_name='')  # 2
    dp_0f = ComplexEnumMember(0x8010f, printable_name='')  # 1
    dp_10 = ComplexEnumMember(0x80110, printable_name='')  # 2

    #qcb states
    qcb_11 = ComplexEnumMember(0x8011, printable_name='')
    # qcb_12 = ComplexEnumMember(0x8012, printable_name='')
    qcb_13 = ComplexEnumMember(0x8013, printable_name='')
    qcb_14 = ComplexEnumMember(0x8014, printable_name='')
    qcb_15 = ComplexEnumMember(0x8015, printable_name='')
    # qcb_16 = ComplexEnumMember(0x8016, printable_name='')
    qcb_17 = ComplexEnumMember(0x8017, printable_name='')
    # qcb_18 = ComplexEnumMember(0x8018, printable_name='')
    # qcb_19 = ComplexEnumMember(0x8019, printable_name='')
    # qcb_1a = ComplexEnumMember(0x801a, printable_name='')
    #Missing?
    qcb_1c = ComplexEnumMember(0x801c, printable_name='')
    qcb_1d = ComplexEnumMember(0x801d, printable_name='')

    f_qcf_12 = ComplexEnumMember(0x8031, printable_name='') #gigas command throw

    EX_CANCEL_1 = ComplexEnumMember(0x8122, printable_name='')
    EX_CANCEL_2 = ComplexEnumMember(0x8123, printable_name='')

    qcf_129 = ComplexEnumMember(0x8129, printable_name='') #1, seems to be the most common, maybe the 'normal' qcf
    qcf_12a = ComplexEnumMember(0x812a, printable_name='') #2
    qcf_12e = ComplexEnumMember(0x812e, printable_name='')
