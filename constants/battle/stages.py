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

class BattleStages(PrintableEnum):
    """
    """
    MISHIMA_DOJO = PrintableValue(0, 'Mishima Dojo')
    FORGOTTEN_REALM = PrintableValue(1, 'Forgotten Realm')
    JUNGLE_OUTPOST = PrintableValue(2, 'Jungle Outpost')
    ARCTIC_SNOWFALL = PrintableValue(3, 'Arctic Snowfall')
    TWILIGHT_CONFLICT = PrintableValue(4, 'Twilight Conflict')
    DRAGON_NEST = PrintableValue(5, 'Dragon Nest')
    SOUQ = PrintableValue(6, 'Souq')
    DEVILS_PIT = PrintableValue(7, "Devil's Pit")
    MISHIMA_BUILDING = PrintableValue(8, 'Mishima Building')
    ABANDONED_TEMPLE = PrintableValue(9, 'Abandoned Temple')
    DUOMO_DI_SIRIO = PrintableValue(30, 'Duomo di Sirio')
    ARENA = PrintableValue(31, 'Arena')
    G_CORP_HELIPAD = PrintableValue(32, 'G. Corp Helipad')
    G_CORP_HELIPAD_NIGHT = PrintableValue(33, 'G. Corp Helipad Night')
    BRIMSTONE_AND_FIRE = PrintableValue(35, 'Brimstone & Fire')
    PRECIPICE_OF_FATE = PrintableValue(36, 'Precipice of Fate')
    VIOLET_SYSTEMS = PrintableValue(37, 'Violet Systems')
    KINDER_GYM = PrintableValue(39, 'Kinder Gym')
    INFINITE_AZURE = PrintableValue(40, 'Infinite Azure')
    GEOMETRIC_PLANE = PrintableValue(41, 'Geometric Plane')
    WARM_UP = PrintableValue(42, 'Warm Up') # Not selectable
    HOWARD_ESTATE = PrintableValue(51, 'Howard Estate')
    HAMMERHEAD = PrintableValue(52, 'Hammerhead')
    JUNGLE_OUTPOST_2 = PrintableValue(53, 'Jungle Outpost 2')
    TWILIGHT_CONFLICT_2 = PrintableValue(54, 'Twilight Conflict 2')
    INFINITE_AZURE_2 = PrintableValue(55, 'Infinite Azure 2')
    LAST_DAY_ON_EARTH = PrintableValue(56, 'Last Day on Earth') # DLC
