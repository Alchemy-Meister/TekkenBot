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

import configparser
import getopt
from pathlib import Path
import re
import sys

def version_updater(argv):
    is_release = False
    version_increased = False

    try:
        opts, _ = getopt.getopt(argv, 'r', ['release'])
    except getopt.GetoptError:
        print('increase_version.py [-r] [--release]')
        sys.exit(2)

    for opt, _ in opts:
        if opt in ('-r', '--release'):
            is_release = True

    update_config = configparser.ConfigParser(
        inline_comment_prefixes=(';')
    )
    update_config_path = str(Path('data/updater_config.ini').absolute())
    update_config.read(update_config_path)
    version = update_config['DEFAULT']['CURRENT_VERSION']

    version_parts = list(
        re.search(
            r'(^[0-9])+((?:\.[0-9]+)*)((?:a|b|rc)[0-9]+)?'
            r'(\.post[0-9]+)?(\.dev[0-9]+)?$',
            version
        ).groups()
    )

    pre_release = version_parts[2]

    version_parts = [
        version_part for version_part in version_parts if version_part
    ]

    if is_release or not pre_release:
        version_parts = version_parts[0:2]
        if pre_release:
            version_increased = True

    if not version_increased:
        last_version_part = version_parts.pop(-1)
        try:
            last_version_part = str(int(last_version_part) + 1)
        except ValueError:
            last_version_part = [
                version_part
                for version_part in re.split(r'(\d+)', last_version_part)
                if version_part
            ]
            last_version_part[-1] = str(int(last_version_part[-1]) + 1)
            last_version_part = ''.join(last_version_part)

        version_parts.append(last_version_part)

    if not is_release and not pre_release:
        version_parts.insert(2, 'b0')

    version = ''.join(version_parts)
    update_config['DEFAULT']['CURRENT_VERSION'] = version
    with open(update_config_path, 'w') as update_config_file:
        update_config.write(update_config_file)
    print(version)

if __name__ == "__main__":
    version_updater(sys.argv[1:])
