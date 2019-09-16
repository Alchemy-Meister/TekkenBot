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
from distutils.version import StrictVersion
import os
import queue
import threading
import urllib.parse as url_parse
import urllib.request as urllib2
import webbrowser

from patterns.singleton import Singleton

from .no_internet_connection_error import NoInternetConnectionError

class Updater(metaclass=Singleton):
    """
    """

    def __init__(self, current_version, user, repo, download_filename_format):
        self.current_version = StrictVersion(current_version)
        self.github_releases = 'https://github.com/{0}/{1}/releases/'.format(
            user, repo
        )
        self.download_filename_format = download_filename_format

        self.update_version_initialized = False
        self.update_version = None

        self.gui_container = None
        self.queue = queue.Queue()
        self.thread = None
        self.gui_update_running = False

    def __gui_update(self, success_callback, error_callback):
        try:
            message = self.queue.get_nowait()
            if message == NoInternetConnectionError:
                error_callback()
            else:
                success_callback(message)
            self.gui_update_running = False
        except queue.Empty:
            pass
        if self.gui_update_running:
            self.gui_container.after(
                500,
                lambda: self.__gui_update(success_callback, error_callback)
            )

    def get_update_version(self, use_cache=True, timeout=None):
        if use_cache and self.update_version_initialized:
            return self.update_version

        return self.__get_update_version(timeout=timeout)

    def is_update_available(
            self, use_cache=True, run_async=False, success_callback=None,
            error_callback=None, timeout=None
    ):
        if run_async and self.gui_container:
            if not self.gui_update_running:
                self.__async_is_update_available(
                    use_cache, success_callback, error_callback, timeout=timeout
                )
        else:
            return self.__proccess_update_available(use_cache, timeout=timeout)

    def get_download_url(self, use_cache=False, run_async=False, timeout=None):
        if self.is_update_available(use_cache=use_cache, run_async=run_async):
            version = self.get_update_version(use_cache=True, timeout=timeout)
            return url_parse.urljoin(
                self.github_releases,
                'download/{0}/{1}/'.format(
                    version, self.download_filename_format.format(version)
                )
            )
        return None

    def download_update(self, use_cache=False, timeout=None):
        threading.Thread(
            target=self.__open_download_url,
            kwargs={
                'use_cache': use_cache, 'run_async': False, 'timeout': timeout
            }
        ).start()

    def __get_update_version(self, timeout=None):
        latest_release_url = url_parse.urljoin(self.github_releases, 'latest/')

        try:
            if timeout is None:
                response = urllib2.urlopen(latest_release_url)
            else:
                response = urllib2.urlopen(latest_release_url, timeout=timeout)
            response_redirected_url = response.geturl()

            self.update_version_initialized = True

            if 'tag' in response_redirected_url:
                self.update_version = str(
                    os.path.basename(response_redirected_url)
                )
            else:
                self.update_version = None
        except urllib2.HTTPError:
            self.update_version_initialized = False
            self.update_version = None
        except urllib2.URLError:
            raise NoInternetConnectionError

        return self.update_version

    def __async_is_update_available(
            self, cache, success_callback, error_callback, timeout=None
    ):
        self.gui_update_running = True
        self.__gui_update(success_callback, error_callback)
        threading.Thread(
            target=self.__proccess_update_available, args=(cache, True, timeout)
        ).start()

    def __proccess_update_available(self, cache, use_queue=False, timeout=None):
        try:
            version = self.get_update_version(use_cache=cache, timeout=timeout)
            if version and self.current_version < StrictVersion(version):
                if use_queue:
                    self.queue.put(True)
                return True
            if use_queue:
                self.queue.put(False)
            return False
        except NoInternetConnectionError:
            if use_queue:
                self.queue.put(NoInternetConnectionError)
            else:
                raise NoInternetConnectionError

    def __open_download_url(
            self, use_cache=False, run_async=False, timeout=None
    ):
        webbrowser.open(
            self.get_download_url(
                use_cache=use_cache, run_async=run_async, timeout=timeout
            )
        )
