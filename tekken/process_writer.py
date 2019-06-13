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
from .process_identifier import ProcessIO
from .process_memory import ProcessMemory
from .overwriters import AddressOverwriter, MultilevelPointerOverwriter

class TekkenGameWritter(ProcessIO):
    """
    """
    def __init__(self, config, pid, module_address=None):
        super().__init__(config['overwrite'], pid, module_address)
        self.overwriters = list()

        for key, address in self.config.items():
            process_memory = ProcessMemory(
                self.pid, self.module_address, address
            )
            if isinstance(address, list):
                overwriter = MultilevelPointerOverwriter(
                    bool(config['default']['enable_{}'.format(key)]),
                    process_memory,
                    config['default'][key]
                )
            else:
                overwriter = AddressOverwriter(
                    bool(config['default']['enable_{}'.format(key)]),
                    process_memory,
                    config['default'][key]
                )
            self.overwriters.append(overwriter)

            for attr_name, attr_value in overwriter.__dict__.items():
                if isinstance(attr_value, bool):
                    self.__add_boolean_method(
                        attr_name, key, overwriter
                    )
                elif not isinstance(attr_value, ProcessMemory):
                    self.__add_value_method(
                        attr_name, key, overwriter
                    )

    def update_overwriters(self, pid=None, module_address=None):
        if pid is None:
            pid = self.pid
        if module_address is None:
            module_address = self.module_address

        for overwriter in self.overwriters:
            overwriter.process_memory = (
                ProcessMemory(
                    pid,
                    module_address,
                    overwriter.process_memory.address
                )
            )

    def update(self):
        if self.is_pid_valid() and self.module_address is not None:
            self.reacquire_module_address = False
            for overwriter in self.overwriters:
                try:
                    overwriter.update()
                except OSError:
                    self._reacquire_everything()
                    raise
        else:
            raise OSError('invalid PID or module address')

    def __add_method(self, method_name, attr_name, instance):
        def set_attribute(_self, value):
            setattr(instance, attr_name, value)

        def get_attribute(_self):
            return getattr(instance, attr_name)

        setattr(
            self.__class__,
            method_name,
            property(fset=set_attribute, fget=get_attribute)
        )

    def __add_boolean_method(self, attr_name, identifier, index):
        self.__add_method(
            '{}_{}_overwrite'.format(attr_name, identifier), attr_name, index
        )

    def __add_value_method(self, attr_name, identifier, index):
        self.__add_method(
            '{}_overwrite'.format(identifier), attr_name, index
        )
