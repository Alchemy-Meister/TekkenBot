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
import os

from patterns.singleton import Singleton

from .model_based_reloadable_config import ModelBasedReloadableConfig
from .reloadable_config import ReloadableConfig

class ReloadableConfigManager(metaclass=Singleton):
    """
    """
    def __init__(self):
        self.data_folder = 'data'
        self.__configs = dict()
        self.__config_groups = dict()

    def add_config(
            self,
            file_name,
            sub_dir=None,
            parse=False,
            config_model_class=None
    ):
        path = self.__get_file_path(file_name, sub_dir)
        if not os.path.exists(path):
            if config_model_class:
                config_model = config_model_class()
                if config_model.update_required:
                    config_model.write()
            else:
                raise ValueError('{} does not exist'.format(path))
        reloadable_config = self.__configs.get(path)
        if reloadable_config:
            raise ValueError('config already exists')
        if config_model_class:
            reloadable_config = ModelBasedReloadableConfig(config_model_class)
            config_model = config_model_class(
                file_settings=reloadable_config.config
            )
            if config_model.update_required:
                config_model.write()
            reloadable_config.config = config_model.parse(
                config_model.settings
            )
        else:
            reloadable_config = ReloadableConfig(path, parse)
        self.__configs[path] = reloadable_config
        return self.__configs[path]

    def remove_config(self, file_name, sub_dir=None):
        path = self.__get_file_path(file_name, sub_dir)
        config = self.__configs.get(path)
        if not config:
            raise ValueError('config does not exist')
        deleted_config = self.__configs[path]
        del self.__configs[path]
        return deleted_config

    def add_config_group(
            self, group_key, path_function, parse=False
    ):
        if group_key in self.__configs:
            raise ValueError('config group already exists')
        return self.__reload_config_group(
            group_key, path_function, parse
        )['configs']

    def get_config(self, file_name, sub_dir=None):
        path = self.__get_file_path(file_name, sub_dir)
        return self.__configs.get(path)

    def get_config_group(self, group_key):
        group_dict = self.__config_groups.get(group_key)
        if group_dict:
            return group_dict['configs']
        return None

    def __get_file_path(self, file_name, sub_dir=None):
        if sub_dir is None:
            return os.path.join(
                self.data_folder, file_name
            )
        return os.path.join(
            os.path.join(self.data_folder, sub_dir),
            file_name
        )


    def reload_all(self):
        for config in self.__configs.values():
            config.reload()
        for group_key, group_dict in self.__config_groups.items():
            self.__reload_config_group(
                group_key, group_dict['path_function'], group_dict['parse']
            )

    def __reload_config_group(self, group_key, path_function, parse):
        config_group_dict = {
            'configs': list(), 'parse': parse, 'path_function': path_function
        }
        for path in path_function():
            config = ReloadableConfig(path, parse)
            config_group_dict['configs'].append(config)
        self.__config_groups[group_key] = config_group_dict
        return self.__config_groups[group_key]

    def __repr__(self):
        return 'configs: {}\nconfig groups: {}'.format(
            self.__configs, self.__config_groups
        )
