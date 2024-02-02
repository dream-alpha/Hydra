#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2024 by dream-alpha
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


from Components.config import config
from Plugins.Plugin import PluginDescriptor
from . import _
from .HydraMenu import HydraMenu
from .torr.torrclient import torrclient
from .ConfigInit import ConfigInit
from .SkinUtils import loadPluginSkin
from .Debug import logger
from .Version import VERSION


WHERE_SEARCH = -99


def search(session, title, original_title, **__kwargs):
	session.open(HydraMenu, title, original_title)


def main(session, **__kwargs):
	session.open(HydraMenu)


def autoStart(reason, **kwargs):
	if reason == 0:  # startup
		if "session" in kwargs:
			logger.info("+++ Version: %s starts...", VERSION)
			if config.plugins.hydra.autostart.value:
				torrclient.getInstance().start_server(config.plugins.hydra.config_path.value)
			loadPluginSkin("skin.xml")
	elif reason == 1:  # shutdown
		logger.info("--- shutdown")
	else:
		logger.info("reason not handled: %s", reason)


def Plugins(**__kwargs):
	ConfigInit()
	return [
		PluginDescriptor(
			where=[
				PluginDescriptor.WHERE_AUTOSTART,
				PluginDescriptor.WHERE_SESSIONSTART
			],
			fnc=autoStart
		),
		PluginDescriptor(
			name=_("Search movie"),
			where=WHERE_SEARCH,
			fnc=search
		),
		PluginDescriptor(
			name="Hydra",
			where=PluginDescriptor.WHERE_PLUGINMENU,
			icon="Hydra.svg",
			description=_("Hydra Player"),
			fnc=main
		)
	]
