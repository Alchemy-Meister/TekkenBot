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
from distutils.version import LooseVersion
import os
import urllib.parse as url_parse
import urllib.request as urllib2
import webbrowser

from patterns.singleton import Singleton

class Updater(metaclass=Singleton):
    """
    """
    def __init__(self, current_version, user, repo, download_filename_format):
        self.current_version = LooseVersion(current_version)
        self.github_releases = 'https://github.com/{0}/{1}/releases/'.format(
            user, repo
        )
        self.download_filename_format = download_filename_format

        self.update_version = None

    def get_update_version(self, use_cache=True):
        if use_cache and self.update_version:
            return self.update_version

        latest_release_url = url_parse.urljoin(self.github_releases, 'latest/')

        try:
            response = urllib2.urlopen(latest_release_url)
            response_redirected_url = response.geturl()

            if 'tag' in response_redirected_url:
                self.update_version = str(
                    os.path.basename(response_redirected_url)
                )
                return self.update_version
        except urllib2.HTTPError:
            return None

    def is_update_available(self, use_cache=True):
        version = self.get_update_version(use_cache=use_cache)
        if version and self.current_version < LooseVersion(version):
            return True
        return False

    def get_download_url(self, use_cache=False):
        if self.is_update_available(use_cache=use_cache):
            version = self.get_update_version(use_cache=True)
            return url_parse.urljoin(
                self.github_releases,
                'download/{0}/{1}/'.format(
                    version, self.download_filename_format.format(version)
                )
            )
        return None

    def download_update(self, use_cache=False):
        webbrowser.open(self.get_download_url(use_cache=use_cache))
