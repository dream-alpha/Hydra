#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2023 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


import os
from Components.config import config, ConfigOnOff, ConfigText, ConfigSelection, ConfigYesNo, ConfigDirectory, ConfigSubsection, ConfigLocations
from .Debug import logger, log_levels


medialist = [n.split()[1] for n in open('/proc/mounts', 'r').readlines() if any(x in n for x in ('vfat', 'ext4', 'ext3', 'ext2', 'fat32', 'fat16', 'ntfs', 'fuseblk')) and 'media' in n]


def listDir(adir):
	cfg_list = []
	try:
		for afile in os.listdir(adir):
			filename, ext = os.path.splitext(afile)
			if ext == ".cfg":
				cfg_list.append(filename)
	except OSError as e:
		logger.error("failed: e: %s", e)
	return cfg_list


search_engines = listDir("/usr/lib/enigma2/python/Plugins/Extensions/Hydra/addons")


def next_search_engine(search_engine):
	i = search_engines.index(search_engine)
	i = i + 1 if i < len(search_engines) - 1 else 0
	return search_engines[i]


class ConfigInit():

	def __init__(self):
		logger.info("...")
		config.plugins.hydra = ConfigSubsection()
		config.plugins.hydra.debug_log_level = ConfigSelection(default="DEBUG", choices=log_levels.keys())
		config.plugins.hydra.autostart = ConfigOnOff(default=False)
		config.plugins.hydra.remember_last_search = ConfigYesNo()
		config.plugins.hydra.last_search = ConfigText(default="Bond")
		config.plugins.hydra.last_positions = ConfigText(default="{}")
		config.plugins.hydra.config_path = ConfigDirectory("/etc/enigma2")
		config.plugins.hydra.config_bookmarks = ConfigLocations(default=medialist + ["/data"])
		config.plugins.hydra.poster_path = ConfigDirectory("/tmp")
		config.plugins.hydra.poster_bookmarks = ConfigLocations(default=medialist + ["/tmp"])
		config.plugins.hydra.search_engine = ConfigSelection(default="demo", choices=search_engines)
		config.plugins.hydra.vpn_start = ConfigOnOff(default=True)
		config.plugins.hydra.vpn_stop = ConfigOnOff(default=True)
