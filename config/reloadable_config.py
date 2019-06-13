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
import configparser
import distutils.util as util
import sys

class ReloadableConfig():
    def __init__(self, path, parse=False):
        self.path = path
        self.parse = parse
        self.config = ReloadableConfig.__generate_config(path, parse)

    def reload(self):
        self.config = ReloadableConfig.__generate_config(self.path, self.parse)

    def __getitem__(self, key):
        return self.config.get(key)

    @staticmethod
    def __generate_config(path, parse=False):
        input_dict = dict()

        config_data = configparser.ConfigParser(
            inline_comment_prefixes=(';')
        )
        config_data.read(path)
        for section, proxy in config_data.items():
            # if section == 'DEFAULT':
            #     continue
            if section not in input_dict:
                input_dict[section] = dict()
            for key, value in proxy.items():
                if parse:
                    value = ReloadableConfig.__parse_numbers(
                        value
                    )
                input_dict[section][key] = value
        return input_dict

    @staticmethod
    def __parse_numbers(value):
        try:
            # NonPlayerDataAddresses consists of space delimited
            # lists of hex numbers so just ignore strings with
            # spaces in them
            if value.startswith('0x') and ',' in value:
                temp = value
                value = []
                for str_ml_pointer in temp.split(','):
                    value.append(
                        [int(val, 16) for val in str_ml_pointer.split()]
                    )
            elif value.startswith('0x') and ' ' in value:
                value = [int(val, 16) for val in value.split()]
            elif value.startswith('0x'):
                value = int(value, 16)
            else:
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = util.strtobool(value)
                    except ValueError:
                        pass
        except ValueError as exception:
            sys.stderr.write(str(exception))
        return value
