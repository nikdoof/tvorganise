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


class TvOrganiser():

	_config = {}

	def __init__(self):
		pass

	@property
	def _logger(self):
		if not hasattr(self, "__logger"):
			self.__logger = logging.getLogger(self.__class__.__name__)
			self.__logger.addHandler(logging.StreamHandler())
		return self.__logger

	def _getConfig(self, file):

		config = {}

		configpsr = ConfigParser.RawConfigParser()
		configpsr.read('tvorganise.cfg')

		if configpsr.has_section('main'):
			for k, v in configpsr.items('main'):
				config[k] = v

		if configpsr.has_section('regex'):

			regex_config = {}
			regex = []

			# Load in subs before reading in the regex
			for k, v in configpsr.items('regex'):
				if k[:5] != 'regex':
					regex_config[k] = v

			for k, v in configpsr.items('regex'):
				if k[:5] == 'regex':
					regex.append(re.compile(v % regex_config))

			config['regex'] = regex

		self._config = config
		return config

	def _findFiles(self, args):
		"""
		Takes a list of files/folders, grabs files inside them. Does not recurse
		more than one level (if a folder is supplied, it will list files within)
		"""
		allfiles = []
		for cfile in args:
			if os.path.isdir(cfile):
				for sf in os.listdir(cfile):
					newpath = os.path.join(cfile, sf)
					if os.path.isfile(newpath):
						allfiles.append(newpath)
			elif os.path.isfile(cfile):
				allfiles.append(cfile)
		return allfiles

	def processNames(self, names, verbose=False):
		"""
		Takes list of names, runs them though the regexs
		"""
		allEps = []
		for f in names:
			filepath, filename = os.path.split(f)
			filename, ext = os.path.splitext(filename)

			# Remove leading . from extension
			ext = ext.replace(".", "", 1)

			for r in config['regex']:
				match = r.match(filename)
				if match:
					showname, seasno, epno, epname = match.groups()

					#remove ._- characters from name (- removed only if next to end of line)
					showname = re.sub("[\._]|\-(?=$)", " ", showname).strip()

					seasno, epno = int(seasno), int(epno)

					self._logger.debug("File:", filename)
					self._logger.debug("Pattern:", r.pattern)
					self._logger.debug("Showname:", showname)
					self._logger.debug("Seas:", seasno)
					self._logger.debug("Ep:", epno)

					allEps.append({'file_showname': showname,
									'seasno': seasno,
									'epno': epno,
									'filepath': filepath,
									'filename': filename,
									'ext': ext})
					break # Matched - to the next file!
			else:
				self._logger.warning("Invalid name: %s" % (f))

		return allEps

	def _same_partition(f1, f2):
		return os.stat(f1).st_dev == os.stat(f2).st_dev

	###########################

	def main(self):
		parser = OptionParser(usage="%prog [options] <file or directories>")
		parser.add_option("-a", "--always", dest = "always",
			action = "store_true", default = False, 
			help = "Do not ask for confirmation before copying")
		parser.add_option("-q", "--quiet", dest = "quiet",
			action = "store_true", default = False,
			help = "Silence output")
		parser.add_option("-c", "--config", dest = "config",
			action = "store", default = "tvorganise.cfg",
			help = "Use a custom configuration file")
		parser.add_option("-v", "", dest = "verbose",
			action = "store_true", default = False,
			help = "Verbose output")

		opts, args = parser.parse_args()

		if os.path.exists(opts.config):
			config = self._getConfig(opts.config)
		else:
			self._logger.error('Unable to find configuration file!')
			sys.exit(1)

		files = self._findFiles(args)
		files = self.processNames(files, opts.verbose)

		# Warn if no files are found, then exit
		if len(files) == 0:
			self._logger.error('No files found')
			sys.exit(0)

		for name in files:
			oldfile = os.path.join(name['filepath'], name['filename']) + "." + name['ext']
			newpath = config['target_path'] % name
			newfile = os.path.join(newpath, name['filename']) + "." + name['ext']
		
			self._logger.info("Old path:", oldfile)
			self._logger.info("New path:", newfile)
			
			if opts.always:
				if not os.path.exists(newpath):
					os.mkdirs(newpath)
				if os.path.exists(newfile):
					self._logger.warning("[!] File already exists, not copying")
				else:
					if self._same_partition(oldfile, newpath):
						self._logger.info("[*] Moving file")
						try:
							os.rename(oldfile, newfile)
						except Exception, errormsg:
							self._logger.error("[!] Error moving file! %s" % (errormsg))
					else:
						self._logger.info("[*] Copying file")
						try:
							shutil.copy(oldfile, newfile)
						except Exception, errormsg:
							self._logger.error("[!] Error copying file! %s" % (errormsg))
						else:
							self._logger.info("[*] ..done")
			else:
				self._logger.warning("Skipping file")

if __name__ == '__main__':
	
	t = TvOrganiser()
	t.main()