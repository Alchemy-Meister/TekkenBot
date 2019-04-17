"""
Reads in simple config files
"""

from configparser import ConfigParser
import collections


class ConfigReader:
    DATA_FOLDUER = "TekkenData/"

    values = {}

    def __init__(self, filename):
        self.path = ConfigReader.DATA_FOLDUER + filename + ".ini"
        self.parser = ConfigParser()
        try:
            self.parser.read(self.path)
        except:
            print("Error reading config data from " + self.path + ". Using default values.")

    def get_property(self, section, property_string, default_value):
        try:
            if type(default_value) is bool:
                value = self.parser.getboolean(section, property_string)
            else:
                value = self.parser.get(section, property_string)
        except:
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
        with open(self.path, 'w') as fw:
            self.parser.write(fw)


def config_from_path(config_path, input_dict=None, parse_nums=False):
    '''
    Parses the file from config_path with configparser and converts configparser's
    pseudo-dict in to a proper dict.
    Configparser's section proxies and string-only values are unsuitable for our use.

    Overwrites old values in input_dict
    '''
    if input_dict is None:
        input_dict = CaseInsensitiveDict()

    config_data = ConfigParser(inline_comment_prefixes=('#', ';'))
    try:
        config_data.read(config_path)
    except:
        print("Error reading config data from " + config_path)
    else:
        for section, proxy in config_data.items():
            if section == 'DEFAULT':
                continue
            if section not in input_dict:
                input_dict[section] = CaseInsensitiveDict()
            for key, value in proxy.items():
                if parse_nums:
                    try:
                        # NonPlayerDataAddresses consists of space delimited lists of hex numbers
                        # so just ignore strings with spaces in them
                        if value.startswith('0x') and not ' ' in value:
                            value = int(value, 16)
                        else:
                            value = int(value)
                    except ValueError:
                        pass

                input_dict[section][key] = value
    return input_dict


class ReloadableConfig():
    DATA_FOLDER = "TekkenData/"

    # Store configs so we can reload and update them later when needed
    configs = []

    def __init__(self, file_name, parse_nums=False):
        '''
        Configuration class that can reload all class instances with the
        .reload() class method.

        'parse_nums' determines if we keep values as strings or try to convert
        to int/hex
        '''
        self.path = self.DATA_FOLDER + file_name + ".ini"
        self.should_parse = parse_nums
        self.file_name = file_name

        self.config = config_from_path(self.path, parse_nums=parse_nums)

        ReloadableConfig.configs.append(self)

    def __getitem__(self, key):
        if key not in self.config:
            # This is maybe a bit ugly but won't crash the program if the config file
            # is broken or missing entries. Assumes int values.
            # Maybe not needed.
            print('{} section missing from {}.ini'.format(key, self.file_name))
            return collections.defaultdict(lambda: collections.defaultdict(int))
        else:
            return self.config[key]

    @classmethod
    def reload(cls):
        for config in cls.configs:
            config.config = config_from_path(config.path, input_dict=config.config, parse_nums=config.should_parse)
            #print("Reloaded {}.ini".format(config.file_name))


class CaseInsensitiveDict(dict):
    def __contains__(self, key):
        return super().__contains__(key.lower())

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())
