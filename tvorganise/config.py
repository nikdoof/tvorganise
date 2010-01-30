import ConfigParser
import re

def defaults():
   """
   Creates a ConfigParser instance and fills it with the default settings
   """

   config = ConfigParser.RawConfigParser()

   config.add_section('main')
   config.set('main', 'target_path', '/media/%(showname)s/Season %(seasonnum)s/')

   config.add_section('regex')
   config.set('regex', 'valid_in_names', "[\\w\\(\\).,\\[\\]'\\ \\-?!#:]")

   return config


class Config(dict):
    """
    Config class loads and parses TVOrganiser style config files, presenting
    as a dict with compiled re objects as needed.
    """

    def __init__(self, cfile=None):
        super(Config, self).__init__()

        if cfile:
            self.load(cfile)
        else:
            self.defaults()

    def load(self, cfile=None, cparser=None):
        """
        Parses the TVOrganiser style config file and produces a dict
        with all the elements contained within.

        Also, all regex specified in the file are compiled
        """

        if cparser:
            configpsr = cparser
        else:
            configpsr = ConfigParser.RawConfigParser()
            configpsr.read(cfile)

        if configpsr.has_section('main'):
            for key, value in configpsr.items('main'):
                self[key] = value

        if configpsr.has_section('regex'):

            regex_config = {}
            regex = []

            # Load in subs before reading in the regex
            for key, value in configpsr.items('regex'):
                if key[:5] != 'regex':
                    regex_config[key] = value

            for key, value in configpsr.items('regex'):
                if key[:5] == 'regex':
                    regex.append(re.compile(value % regex_config))

            self['regex'] = regex

    def defaults(self):
        """
        Load default settings
        """
        self.load(cparser=defaults())
