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
import os

class ConfigReader:
    DATA_FOLDER = 'data'

    values = {}

    def __init__(self, filename):
        self.path = os.path.join(ConfigReader.DATA_FOLDER, filename)
        self.parser = configparser.ConfigParser()
        try:
            self.parser.read(self.path)
        except configparser.Error as exception:
            print(
                'Error reading config data from {}. Error: {}'.format(
                    self.path, exception
                )
            )

    def get_property(self, section, property_string, default_value):
        try:
            if isinstance(default_value, bool):
                value = self.parser.getboolean(section, property_string)
            else:
                value = self.parser.get(section, property_string)
        except configparser.Error:
            value = default_value

        if section not in self.parser.sections():
            self.parser.add_section(section)
        self.parser.set(section, property_string, str(value))
        return value

    def set_property(self, section, property_string, value):
        self.parser.set(section, property_string, str(value))

    def add_comment(self, comment):
        if 'Comments' not in self.parser.sections():
            self.parser.add_section('Comments')
        self.parser.set('Comments', '; ' + comment, "")

    def write(self):
        with open(self.path, 'w') as w_file:
            self.parser.write(w_file)
