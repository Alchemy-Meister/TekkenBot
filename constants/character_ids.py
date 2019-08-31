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

from constants.complex_enum import ComplexEnum, ComplexEnumMember

class CharacterIDs(ComplexEnum):
    """
    """
    PAUL = ComplexEnumMember(0, printable_name='Paul')
    LAW = ComplexEnumMember(1, printable_name='Law')
    KING = ComplexEnumMember(2, printable_name='King')
    YOSHIMITSU = ComplexEnumMember(3, printable_name='Yoshimitsu')
    HWOARANG = ComplexEnumMember(4, printable_name='Hwoarang')
    XIAOYU = ComplexEnumMember(5, printable_name='Xiaoyu')
    JIN = ComplexEnumMember(6, printable_name='Jin')
    BRYAN = ComplexEnumMember(7, printable_name='Bryan')
    HEIHACHI = ComplexEnumMember(8, printable_name='Heihachi')
    KAZUYA = ComplexEnumMember(9, printable_name='Kazuya') # + True Devil Kayuza
    STEVE = ComplexEnumMember(10, printable_name='Steve')
    JACK_7 = ComplexEnumMember(11, printable_name='Jack 7')
    ASUKA = ComplexEnumMember(12, printable_name='Asuka')
    DEVIL_JIN = ComplexEnumMember(13, printable_name='Devil Jin')
    FENG = ComplexEnumMember(14, printable_name='Feng')
    LILI = ComplexEnumMember(15, printable_name='Lili')
    DRAGUNOV = ComplexEnumMember(16, printable_name='Dragunov')
    LEO = ComplexEnumMember(17, printable_name='Leo')
    LARS = ComplexEnumMember(18, printable_name='Lars')
    ALISA = ComplexEnumMember(19, printable_name='Alisa')
    CLAUDIO = ComplexEnumMember(20, printable_name='Claudio')
    KATARINA = ComplexEnumMember(21, printable_name='Katarina')
    LUCKY_CHLOE = ComplexEnumMember(22, printable_name='Lucky Chloe')
    SHAHEEN = ComplexEnumMember(23, printable_name='Shaheen')
    JOSIE = ComplexEnumMember(24, printable_name='Josie')
    GIGAS = ComplexEnumMember(25, printable_name='Gigas')
    KAZUMI = ComplexEnumMember(26, printable_name='Kazumi')
    # --- Not selectable character --------------------------------------------
    DEVIL_KAZUMI = ComplexEnumMember(27, printable_name='Devil Kazumi')
    # -------------------------------------------------------------------------
    NINA = ComplexEnumMember(28, printable_name='Nina')
    MASTER_RAVEN = ComplexEnumMember(29, printable_name='Master Raven')
    LEE = ComplexEnumMember(30, printable_name='Lee')
    BOB = ComplexEnumMember(31, printable_name='Bob')
    AKUMA = ComplexEnumMember(32, printable_name='Akuma')
    KUMA = ComplexEnumMember(33, printable_name='Kuma')
    PANDA = ComplexEnumMember(34, printable_name='Panda')
    EDDY = ComplexEnumMember(35, printable_name='Eddy')
    # --- DLC character -------------------------------------------------------
    ELIZA = ComplexEnumMember(36, printable_name='Eliza')
     # -------------------------------------------------------------------------
    MIGUEL = ComplexEnumMember(37, printable_name='Miguel')
    # --- Not selectable characters -------------------------------------------
    TEKKEN_FORCE = ComplexEnumMember(38, printable_name='Tekken Force')
    KID_KAZUYA = ComplexEnumMember(39, printable_name='Kid Kazuya')
    JACK_4 = ComplexEnumMember(40, printable_name='Jack 4')
    YOUNG_HEIHACHI = ComplexEnumMember(41, printable_name='Young Heihachi')
    TRAINING_DUMMY = ComplexEnumMember(42, printable_name='Training Dummy')
    # --- DLC characters ------------------------------------------------------
    GEESE = ComplexEnumMember(43, printable_name='Geese')
    NOCTIS = ComplexEnumMember(44, printable_name='Noctis')
    ANNA = ComplexEnumMember(45, printable_name='Anna')
    LEI = ComplexEnumMember(46, printable_name='Lei')
    MARDUK = ComplexEnumMember(47, printable_name='Marduk')
    ARMOR_KING = ComplexEnumMember(48, printable_name='Armor King')
    JULIA = ComplexEnumMember(49, printable_name='Julia')
    NEGAN = ComplexEnumMember(50, printable_name='Negan')
    # -------------------------------------------------------------------------
    NOT_YET_LOADED = ComplexEnumMember(71, printable_name=None)
    # Value if cursor is not shown
    NO_SELECTION = ComplexEnumMember(255, printable_name=None)
