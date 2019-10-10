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
from enum import Enum
import struct
from win32.defines import SIZE_OF, Structure, Union
from win32.utils import type_limits

class StructWrapper():
    """
    """
    def __init__(self, structure, block_bytes=None):
        self.__structure = structure
        if block_bytes:
            offset = 0
            for field in StructWrapper.__flatten(
                    StructWrapper.__get_all_structure_primitive_fields(
                        structure
                    )
            ):
                size = offset + SIZE_OF(field[1])
                t_bytes = block_bytes[offset:size]
                struct_format = type_limits.C_ALL_TYPES_FORMAT[field[1]]
                setattr(
                    self,
                    field[0],
                    struct.unpack(struct_format, t_bytes)[0]
                )
                offset = size
        else:
            self.__default_attributes_initialization(
                StructWrapper.__get_all_structure_primitive_fields(structure),
                structure()
            )

    def __eq__(self, wrapper):
        if isinstance(wrapper, self.__class__):
            return all(
                getattr(wrapper, attr_name) == attr_value
                for attr_name, attr_value in vars(self).items()
            )
        return NotImplemented

    def __ne__(self, wrapper):
        return not self == wrapper

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(
                [
                    '{}: {}'.format(
                        attribute,
                        getattr(self, attribute).name
                        if isinstance(getattr(self, attribute), Enum)
                        else getattr(self, attribute)
                    )
                    for attribute in vars(self) if not attribute.startswith('_')
                ]
            )
        )

    def get_structure_size(self):
        return SIZE_OF(self.__structure)

    def __default_attributes_initialization(self, dictionary, structure=None):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.__default_attributes_initialization(
                    value, getattr(structure, key)
                )
            elif isinstance(value, list):
                for sub_value in value:
                    self.__default_attributes_initialization(
                        sub_value, getattr(structure, key)
                    )
            else:
                setattr(self, key, getattr(structure, key))

    @staticmethod
    def __flatten(dictionary):
        flatten_list = []
        for key, value in dictionary.items():
            if isinstance(value, dict):
                flatten_list.extend(StructWrapper.__flatten(value))
            elif isinstance(value, list):
                for sub_value in value:
                    flatten_list.extend(StructWrapper.__flatten(sub_value))
            else:
                flatten_list.append((key, value,))
        return flatten_list

    @staticmethod
    def __get_all_structure_primitive_fields(structure):
        structure_attribures = {}
        for field in getattr(structure, '_fields_'):
            if issubclass(field[1], (Structure, Union)):
                structure_attribures[field[0]] = (
                    StructWrapper.__get_all_structure_primitive_fields(
                        field[1]
                    )
                )
            else:
                structure_attribures[field[0]] = field[1]
        return structure_attribures
