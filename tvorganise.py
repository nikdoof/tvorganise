#!/usr/bin/env python
#encoding:utf-8
"""
tvorganise.py

This parses "Show Name - [01x23] - Episode Name.avi"
filenames and automatically copies them to
the location format defined in the configuration file.
"""

import os
import sys
import re
from optparse import OptionParser
import shutil
import ConfigParser
import logging

def same_partition(path1, path2):
    """
    Checks to see if two paths are on the same device, returns a
    bool to indicate
    """
    return os.stat(path1).st_dev == os.stat(path2).st_dev

def find_files(args):
    """
    Take a singular path or a list of paths and provides a list of all files in
    that directory structure.
    """
    filelist = []
    
    if isinstance(args, list):
        for path in args:
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    filelist.append(os.path.join(root, name))
    else:
        for root, dirs, files in os.walk(args, topdown=False):
            for name in files:
                filelist.append(os.path.join(root, name))

    return filelist


class TvOrganiser():
    """
    TvOrganiser takes a list of files and validates them against known filename
    formats, then moves the files to a specified tree layout.
    """

    _config = {}
    __logger = None

    def __init__(self):
        pass

    @property
    def _logger(self):
        """
        Returns the class logger instance
        """
        if not hasattr(self, "__logger"):
            self.__logger = logging.getLogger(self.__class__.__name__)
            self.__logger.addHandler(logging.StreamHandler())
        return self.__logger

    def _get_config(self, cfile):
        """
        Parses the TVOrganiser style config file and produces a dict
        with all the elements contained within.
 
        Also, all regex specified in the file are compiled
        """

        config = {}

        configpsr = ConfigParser.RawConfigParser()
        configpsr.read(cfile)

        if configpsr.has_section('main'):
            for key, value in configpsr.items('main'):
                config[key] = value

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

            config['regex'] = regex

        self._config = config
        return config

    def process(self, names):
        """
        Takes list of names, runs them though the regexs
        """
        episodelist = []
        for efile in names:
            filepath, filename = os.path.split(efile)
            filename, ext = os.path.splitext(filename)

            # Remove leading . from extension
            ext = ext.replace(".", "", 1)

            for regex in self._config['regex']:
                match = regex.match(filename)
                if match:
                    showname, seasno, epno, epname = match.groups()

                    #remove ._- characters from name
                    showname = re.sub("[\._]|\-(?=$)", " ", showname).strip()

                    seasno, epno = int(seasno), int(epno)

                    self._logger.debug("File:", filename)
                    self._logger.debug("Pattern:", regex.pattern)
                    self._logger.debug("Showname:", showname)
                    self._logger.debug("Seas:", seasno)
                    self._logger.debug("Ep:", epno)

                    episodelist.append({'file_showname': showname,
                                    'seasno': seasno,
                                    'epno': epno,
                                    'filepath': filepath,
                                    'filename': filename,
                                    'epname': epname,
                                    'ext': ext})
                    break # Matched - to the next file!
            else:
                self._logger.warning("Invalid name: %s" % (efile))

        return episodelist

    def main(self):
        """
        TVOrganiser, provide a path or file to process
        """

        parser = OptionParser(usage="%prog [options] <file or directories>")
        parser.add_option("-a", "--always", dest="always",
            action="store_true", default=False,
            help="Do not ask for confirmation before copying")
        parser.add_option("-q", "--quiet", dest="quiet",
            action="store_true", default=False,
            help="Silence output")
        parser.add_option("-c", "--config", dest="config",
            action="store", default="tvorganise.cfg",
            help="Use a custom configuration file")
        parser.add_option("-v", "", dest="verbose",
            action="store_true", default=False,
            help="Verbose output")

        opts, args = parser.parse_args()

        if os.path.exists(opts.config):
            config = self._get_config(opts.config)
        else:
            self._logger.error('Unable to find configuration file!')
            sys.exit(1)

        files = find_files(args)
        files = self.process(files)

        self._logger.debug(files)

        # Warn if no files are found, then exit
        if len(files) == 0:
            self._logger.error('No files found')
            sys.exit(0)

        for name in files:
            filename = "%s.%s" % (name['filename'], name['ext'])
            oldfile = os.path.join(name['filepath'], filename)
            newpath = config['target_path'] % name
            newfile = os.path.join(newpath, filename)

            self._logger.info("Old path:", oldfile)
            self._logger.info("New path:", newfile)

            if opts.always:
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                if os.path.exists(newfile):
                    self._logger.warning("[!] File already exists, not copying")
                else:
                    if same_partition(oldfile, newpath):
                        self._logger.info("[*] Moving file")
                        try:
                            os.rename(oldfile, newfile)
                        except OSError, errormsg:
                            self._logger.error("[!] Error moving file! %s" % (errormsg))
                    else:
                        self._logger.info("[*] Copying file")
                        try:
                            shutil.copy(oldfile, newfile)
                        except IOError, errormsg:
                            self._logger.error("[!] Error copying file! %s" % (errormsg))
                        else:
                            self._logger.info("[*] ..done")
            else:
                self._logger.warning("Skipping file: %s" % filename)

def main():
    t = TvOrganiser()
    t.main()
