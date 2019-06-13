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
import math
import tkinter.ttk as ttk
import tkinter.font as font

class Combobox(ttk.Combobox):
    """
    """
    def __init__(self, labels, values=None, master=None, **kw):
        super().__init__(master=master, values=labels, **kw)

        self.label_values_dict = Combobox.__generate_value_labels_dict(
            labels, values=values
        )

        if self['values']:
            self.__adapt_width_to_values()

    def set_labels(self, labels, values=None):
        self['values'] = labels
        self.label_values_dict = Combobox.__generate_value_labels_dict(
            labels, values=values
        )
        self.__adapt_width_to_values()

    def configure(self, cnf=None, **kw):
        if isinstance(cnf, str):
            if cnf == 'normal':
                cnf = 'readonly'
        super().configure(cnf=cnf, **kw)

    def __adapt_width_to_values(self):
        widget_font = font.Font(font=self.cget('font'))
        zero_width = widget_font.measure('0')
        width = (
            max([widget_font.measure(i) for i in self['values']]) / zero_width
        )
        self['width'] = math.ceil(width)

    def get_selected(self):
        if self.label_values_dict:
            return self.label_values_dict[self.get()]
        return self.get()

    @staticmethod
    def __generate_value_labels_dict(labels, values=None):
        if values:
            return {k: v for k, v in zip(labels, values)}
        return None
