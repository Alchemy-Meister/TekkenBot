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

from win32.defines import CHAR, DWORD, Structure, QWORD

class PlayersDataStruct(Structure):
    """
    """
    _fields_ = [
        ('__pad_0000', CHAR * 812),  # 0x0000
        ('p1_move_id', DWORD),  # 0x032C
        ('__pad_0330', CHAR * 72),  # 0x0330
        ('p1_recovery', DWORD),  # 0x0378
        ('__pad_037C', CHAR * 56),  # 0x037C
        ('p1_hit_outcome', DWORD),  # 0x03B4
        ('__pad_03B8', CHAR * 52),  # 0x03B8
        ('p1_attack_type', DWORD),  # 0x03EC
        ('p1_simple_move_state', DWORD),  # 0x03F0
        ('p1_stun_type', DWORD),  # 0x03F4
        ('__pad_03F8', CHAR * 12),  # 0x03F8
        ('p1_throw_tech', DWORD),  # 0x0404
        ('__pad_0408', CHAR * 16),  # 0x0408
        ('p1_complex_move_state', DWORD),  # 0x0418
        ('__pad_041C', CHAR * 262),  # 0x041C
        ('p1_power_crush', DWORD),  # 0x0522
        ('__pad_0526', CHAR * 142),  # 0x0526
        ('p1_jump_flags', DWORD),  # 0x05B4
        ('__pad_05B8', CHAR * 32),  # 0x05B8
        ('p1_cancel_window', DWORD),  # 0x05D8
        ('__pad_05DC', CHAR * 340),  # 0x05DC
        ('p1_dword_cycling_frame_count', DWORD),  # 0x0730
        ('__pad_0734', CHAR * 56),  # 0x0734
        ('p1_damage_taken', DWORD),  # 0x076C
        ('__pad_0770', CHAR * 28),  # 0x0770
        ('p1_dword_frame_count', DWORD),  # 0x078C
        ('__pad_0790', CHAR * 272),  # 0x0790
        ('p1_qword_frame_count', QWORD),  # 0x08A0
        ('__pad_08A8', CHAR * 2452),  # 0x08A8
        ('p1_current_side', DWORD),  # 0x123C
        ('__pad_1240', CHAR * 22),  # 0x1240
        ('p1_health', DWORD),  # 0x1256
        ('__pad_125A', CHAR * 1282),  # 0x125A
        ('p1_input_attack', DWORD),  # 0x175C
        ('p1_input_direction', DWORD),  # 0x1760
        ('__pad_1764', CHAR * 22300),  # 0x1764
        ('p1_attack_startup', DWORD),  # 0x6E80
        ('p1_attack_startup_end', DWORD),  # 0x6E84
        ('__pad_6E88', CHAR * 896),  # 0x6E88
        ('p2_recovery', DWORD),  # 0x7208
        ('__pad_720C', CHAR * 56),  # 0x720C
        ('p2_hit_outcome', DWORD),  # 0x7244
        ('__pad_7248', CHAR * 52),  # 0x7248
        ('p2_attack_type', DWORD),  # 0x727C
        ('p2_simple_move_state', DWORD),  # 0x7280
        ('p2_stun_type', DWORD),  # 0x7284
        ('__pad_7288', CHAR * 12),  # 0x7288
        ('p2_throw_tech', DWORD),  # 0x7294
        ('__pad_7298', CHAR * 16),  # 0x7298
        ('p2_complex_move_state', DWORD),  # 0x72A8
        ('__pad_72AC', CHAR * 262),  # 0x72AC
        ('p2_power_crush', DWORD),  # 0x73B2
        ('__pad_73B6', CHAR * 142),  # 0x73B6
        ('p2_jump_flags', DWORD),  # 0x7444
        ('__pad_7448', CHAR * 32),  # 0x7448
        ('p2_cancel_window', DWORD),  # 0x7468
        ('__pad_746C', CHAR * 340),  # 0x746C
        ('p2_dword_cycling_frame_count', DWORD),  # 0x75C0
        ('__pad_75C4', CHAR * 56),  # 0x75C4
        ('p2_damage_taken', DWORD),  # 0x75FC
        ('__pad_7600', CHAR * 28),  # 0x7600
        ('p2_dword_frame_count', DWORD),  # 0x761C
        ('__pad_7620', CHAR * 272),  # 0x7620
        ('p2_qword_frame_count', QWORD),  # 0x7730
        ('__pad_7738', CHAR * 2452),  # 0x7738
        ('p2_current_side', DWORD),  # 0x80CC
        ('__pad_80D0', CHAR * 22),  # 0x80D0
        ('p2_health', DWORD),  # 0x80E6
        ('__pad_80EA', CHAR * 1282),  # 0x80EA
        ('p2_input_attack', DWORD),  # 0x85EC
        ('p2_input_direction', DWORD),  # 0x85F0
        ('__pad_85F4', CHAR * 22300),  # 0x85F4
        ('p2_attack_startup', DWORD),  # 0xDD10
        ('p2_attack_startup_end', DWORD),  # 0xDD14
        ('__pad_DD18', CHAR * 56660),  # 0xDD18
        ('p1_rounds_win', DWORD),  # 0x1BA6C
        ('__pad_1BA70', CHAR * 220),  # 0x1BA70
        ('p2_rounds_win', DWORD),  # 0x1BB4C
        ('__pad_1BB50', CHAR * 1232)  # 0x1BB50
    ]  # Size: 0x1C020

    def __repr__(self):
        return (
            ', '.join(
                [
                    '{}: {}'.format(
                        attribute[0],
                        getattr(self, attribute[0])
                    )
                    for attribute in self._fields_
                    if not attribute[0].startswith('_')
                ]
            )
        )
