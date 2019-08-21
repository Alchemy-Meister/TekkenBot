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
import time
import queue
import threading

class StdStreamRedirector():
    """
    """
    INITIAL_SHORT_DELAY = 2

    def __init__(
            self, widget, widget_config, file_config=None, callback=None
    ):
        self.widget = widget
        self.tag = widget_config.get('tag')
        self.auto_scroll = widget_config.get('auto_scroll', True)

        self.save_to_file = False
        self.file = None
        if file_config:
            self.file_path = file_config.get('file_path')
            if self.file_path:
                self.save_to_file = file_config.get('save_to_file', True)
                if self.save_to_file:
                    self.file = open(
                        self.file_path,
                        file_config.get('write_mode', 'w'),
                        encoding='utf-8'
                    )
        self.callback = callback

        self.queue = queue.Queue()
        self.__run_queue_checker = False
        self.widget_updater = None

        self.last_executed_time = None
        self.delay = StdStreamRedirector.INITIAL_SHORT_DELAY

    def write(self, *args):
        if args:
            if self.__run_queue_checker:
                self.__async_write(*args)
            else:
                self.__sync_write(*args)

    def write_file(self, file_path, callback=None):
        def _read_file(file_path):
            with open(file_path, 'r') as r_file:
                for line in r_file:
                    self.queue.put(line)
                self.queue.put('\n')
            self.queue.put(False)

        self.__run_queue_checker = True
        self.__update_widget(callback=callback)
        threading.Thread(target=_read_file, args=(file_path,)).start()

    def flush(self):
        pass

    def close(self):
        if self.file:
            self.file.close()

    def set_file_path(self, path):
        self.file_path = path

    def enable_save_to_file(self, enable):
        self.save_to_file = enable
        if enable and not self.file:
            if not self.file_path:
                raise Exception('save to file enabled, but file path is None')
            self.file = open(self.file_path, 'w')

    def enable_auto_scroll(self, enable):
        self.auto_scroll = enable

    def __async_write(self, *args):
        def _write(args):
            if len(args) == 1:
                string = str(args[0])
            else:
                string = str(args)
            if string and string[-1] != '\n':
                self.queue.put(''.join([string, '\n']))
            elif string:
                self.queue.put(string)

        threading.Thread(target=_write, args=(args,)).start()

    def __sync_write(self, *args):
        if len(args) == 1:
            string = str(args[0])
        else:
            string = str(args)
        if string and string[-1] != '\n':
            self.__write_on_widget(''.join([string, '\n']))
        elif string:
            self.__write_on_widget(string)

    def __write_to_file(self, string):
        self.file.write(string)
        self.file.flush()

    def __write_on_widget(self, message):
        self.widget.configure(state='normal')
        self.widget.insert('end', message, (self.tag,))
        self.widget.configure(state='disabled')
        if self.auto_scroll:
            self.widget.see('end')
        if self.save_to_file:
            threading.Thread(
                target=self.__write_to_file,
                args=(message,)
            ).start()
        if self.callback:
            self.callback(message)

    def __update_widget(self, callback=None):
        try:
            message = self.queue.get_nowait()
            if isinstance(message, str):
                self.__write_on_widget(message)
                self.__update_delay()
            else:
                self.__run_queue_checker = False
        except queue.Empty:
            pass
        if self.__run_queue_checker:
            self.widget.after(
                self.delay,
                lambda: self.__update_widget(callback=callback)
            )
        elif callback:
            callback()

    def __update_delay(self):
        if self.last_executed_time is None:
            self.last_executed_time = time.time()
        else:
            now = time.time()
            elapsed_time = 1000 * (now - self.last_executed_time)
            avg_delay = (self.delay * 0.8 + elapsed_time * 0.2) / 2
            if avg_delay > StdStreamRedirector.INITIAL_SHORT_DELAY:
                self.delay = int(avg_delay)
            self.last_executed_time = now
