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

class BattleStages(ComplexEnum):
    """
    """
    MISHIMA_DOJO = ComplexEnumMember(0, printable_name='Mishima Dojo')
    FORGOTTEN_REALM = ComplexEnumMember(1, printable_name='Forgotten Realm')
    JUNGLE_OUTPOST = ComplexEnumMember(2, printable_name='Jungle Outpost')
    ARCTIC_SNOWFALL = ComplexEnumMember(3, printable_name='Arctic Snowfall')
    TWILIGHT_CONFLICT = ComplexEnumMember(4, printable_name='Twilight Conflict')
    DRAGON_NEST = ComplexEnumMember(5, printable_name='Dragon Nest')
    SOUQ = ComplexEnumMember(6, printable_name='Souq')
    DEVILS_PIT = ComplexEnumMember(7, printable_name="Devil's Pit")
    MISHIMA_BUILDING = ComplexEnumMember(8, printable_name='Mishima Building')
    ABANDONED_TEMPLE = ComplexEnumMember(9, printable_name='Abandoned Temple')
    # Not selectable stages ----------------------------------------------------
    GEOMETRIC_PLANE_HIDDEN = ComplexEnumMember(
        10, printable_name='Geometric Plane, Hidden'
    )
    CHARACTER_CUSTOMIZATION = ComplexEnumMember(
        23, printable_name='Character Customization'
    )
    CHARACTER_CUSTOMIZATION_RGB = ComplexEnumMember(
        24, printable_name='Character Customization, RGB'
    )
    # --------------------------------------------------------------------------
    DUOMO_DI_SIRIO = ComplexEnumMember(30, printable_name='Duomo di Sirio')
    ARENA = ComplexEnumMember(31, printable_name='Arena')
    G_CORP_HELIPAD = ComplexEnumMember(32, printable_name='G. Corp Helipad')
    G_CORP_HELIPAD_NIGHT = ComplexEnumMember(
        33, printable_name='G. Corp Helipad Night'
    )
    # Not selectable stage -----------------------------------------------------
    MISHIMA_DOJO_OLD = ComplexEnumMember(
        34, printable_name='Mishima Dojo, Old' # Story mode exclusive
    )
    # --------------------------------------------------------------------------
    BRIMSTONE_AND_FIRE = ComplexEnumMember(
        35, printable_name='Brimstone & Fire'
    )
    PRECIPICE_OF_FATE = ComplexEnumMember(
        36, printable_name='Precipice of Fate'
    )
    VIOLET_SYSTEMS = ComplexEnumMember(37, printable_name='Violet Systems')
    VIOLET_SYSTEMS_HALLWAY = ComplexEnumMember(
        38, printable_name='Violet Systems, Hallway' # Story mode exclusive
    )
    KINDER_GYM = ComplexEnumMember(39, printable_name='Kinder Gym')
    INFINITE_AZURE = ComplexEnumMember(40, printable_name='Infinite Azure')
    GEOMETRIC_PLANE = ComplexEnumMember(41, printable_name='Geometric Plane')
    # Not selectable stages ----------------------------------------------------
    # Online mode exclusive
    ONLINE_WARM_UP = ComplexEnumMember(42, printable_name='Online Warm Up')
    # Story mode exclusives
    SOUQ_2 = ComplexEnumMember(43, printable_name='Souq 2')
    HON_MARU = ComplexEnumMember(44, printable_name='Hon-Maru')
    MISHIMA_DOJO_OLD_2 = ComplexEnumMember(
        45, printable_name='Mishima Dojo, Old 2'
    )
    MISHIMA_BUILDING_TOP = ComplexEnumMember(
        47, printable_name='Mishima Building, Top'
    )
    G_CORP_HELIPAD_UNBREAKABLE = ComplexEnumMember(
        48, printable_name='G. Corp Helipad, Unbreakable'
    )
    VIOLET_SYSTEMS_2 = ComplexEnumMember(50, printable_name='Violet Systems 2')
    # DLC stages ---------------------------------------------------------------
    HOWARD_ESTATE = ComplexEnumMember(51, printable_name='Howard Estate')
    HAMMERHEAD = ComplexEnumMember(52, printable_name='Hammerhead')
    JUNGLE_OUTPOST_2 = ComplexEnumMember(53, printable_name='Jungle Outpost 2')
    TWILIGHT_CONFLICT_2 = ComplexEnumMember(
        54, printable_name='Twilight Conflict 2'
    )
    INFINITE_AZURE_2 = ComplexEnumMember(55, printable_name='Infinite Azure 2')
    LAST_DAY_ON_EARTH = ComplexEnumMember(
        56, printable_name='Last Day on Earth'
    )
    CAVE_OF_ENLIGHTENMENT = ComplexEnumMember(
        57, printable_name='Cave of Enlightenment'
    )
