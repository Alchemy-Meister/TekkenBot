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

from constants.printable_enum import PrintableEnum, PrintableValue

class CharacterIDs(PrintableEnum):
    """
    """
    PAUL = PrintableValue(0, 'Paul')
    LAW = PrintableValue(1, 'Law')
    KING = PrintableValue(2, 'King')
    YOSHIMITSU = PrintableValue(3, 'Yoshimitsu')
    HWOARANG = PrintableValue(4, 'Hwoarang')
    XIAOYU = PrintableValue(5, 'Xiaoyu')
    JIN = PrintableValue(6, 'Jin')
    BRYAN = PrintableValue(7, 'Bryan')
    HEIHACHI = PrintableValue(8, 'Heihachi')
    KAZUYA = PrintableValue(9, 'Kazuya') # Also True Devil Kayuza
    STEVE = PrintableValue(10, 'Steve')
    JACK_7 = PrintableValue(11, 'Jack 7')
    ASUKA = PrintableValue(12, 'Asuka')
    DEVIL_JIN = PrintableValue(13, 'Devil Jin')
    FENG = PrintableValue(14, 'Feng')
    LILI = PrintableValue(15, 'Lili')
    DRAGUNOV = PrintableValue(16, 'Dragunov')
    LEO = PrintableValue(17, 'Leo')
    LARS = PrintableValue(18, 'Lars')
    ALISA = PrintableValue(19, 'Alisa')
    CLAUDIO = PrintableValue(20, 'Claudio')
    KATARINA = PrintableValue(21, 'Katarina')
    LUCKY_CHLOE = PrintableValue(22, 'Lucky Chloe')
    SHAHEEN = PrintableValue(23, 'Shaheen')
    JOSIE = PrintableValue(24, 'Josie')
    GIGAS = PrintableValue(25, 'Gigas')
    KAZUMI = PrintableValue(26, 'Kazumi')
    DEVIL_KAZUMI = PrintableValue(27, 'Devil Kazumi') # Not selectable
    NINA = PrintableValue(28, 'Nina')
    MASTER_RAVEN = PrintableValue(29, 'Master Raven')
    LEE = PrintableValue(30, 'Lee')
    BOB = PrintableValue(31, 'Bob')
    AKUMA = PrintableValue(32, 'Akuma')
    KUMA = PrintableValue(33, 'Kuma')
    PANDA = PrintableValue(34, 'Panda')
    EDDY = PrintableValue(35, 'Eddy')
    ELIZA = PrintableValue(36, 'Eliza') # DLC
    MIGUEL = PrintableValue(37, 'Miguel')
    TEKKEN_FORCE = PrintableValue(38, 'Tekken Force') # Not selectable
    KID_KAZUYA = PrintableValue(39, 'Kid Kazuya') # Not selectable
    JACK_4 = PrintableValue(40, 'Jack 4') # Not selectable
    YOUNG_HEIHACHI = PrintableValue(41, 'Young Heihachi') # Not selectable
    TRAINING_DUMMY = PrintableValue(42, 'Training Dummy') # Not selectable
    GEESE = PrintableValue(43, 'Geese') # DLC
    NOCTIS = PrintableValue(44, 'Noctis') # DLC
    ANNA = PrintableValue(45, 'Anna') # DLC
    LEI = PrintableValue(46, 'Lei') # DLC
    MARDUK = PrintableValue(47, 'Marduk') # DLC
    ARMOR_KING = PrintableValue(48, 'Armor King') # DLC
    JULIA = PrintableValue(49, 'Julia') # DLC
    NEGAN = PrintableValue(50, 'Negan') # DLC
