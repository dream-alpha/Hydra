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


import os
import importlib
import six
from twisted.internet import threads, reactor
from Components.ActionMap import ActionMap
from Components.config import config
from Components.Label import Label
from Components.Sources.List import List
from Screens.Screen import Screen
from .Debug import logger
from .torr.Utils import getConfig
from .Loading import Loading
from .ConfigInit import search_engines, next_search_engine
from .DelayTimer import DelayTimer
from .TInfos import TInfos
from . import _


class HydraSearch(Screen):
	def __init__(self, session, search_topic):
		Screen.__init__(self, session)
		self.search_topic = search_topic
		self.search_engine = config.plugins.hydra.search_engine.value
		if self.search_engine not in search_engines:
			self.search_engine = "demo"
		self.__setTitle(self.search_topic, self.search_engine)
		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Add torrent"))
		self["key_yellow"] = Label(_("Search"))
		self["key_blue"] = Label(_(">> Search engine"))

		self.loading = Loading(self, None)

		self.thread = None
		self.s_obj = None
		self.menu_list = []
		self["menu"] = self.menu = List(self.menu_list, enableWrapAround=True)
		self["actions"] = ActionMap(
			["HydraActions"],
			{
				"cancel": self.cancel,
				"red": self.cancel,
				"green": self.ok,
				"yellow": self.__onLayoutFinish,
				"blue": self.toggleSearchEngine,
				"ok": self.ok,
				"down": self.menu.selectNext,
				"up": self.menu.selectPrevious,
				"left": self.menu.pageUp,
				"right": self.menu.pageDown,
			},
			-1
		)
		self.onLayoutFinish.append(self.__onLayoutFinish)

	def __setTitle(self, search_topic, search_engine):
		self.setTitle("%s %s: %s" % (_("Search"), search_engine, search_topic if search_topic else _("None")))

	def __onLayoutFinish(self):
		menu_list = []
		self["menu"].setList(menu_list)
		DelayTimer(50, self.searchSetup, self.search_topic)

	def searchSetup(self, search_topic):
		self.auto_configs = []
		self.rts_infos = TInfos()
		self.auto_mode = ""
		auto_config = getConfig(
			os.path.join(
				"/usr/lib/enigma2/python/Plugins/Extensions/Hydra/addons",
				self.search_engine + ".cfg"
			)
		)
		logger.debug("auto_config: %s", auto_config)
		if self.search_engine == "auto":
			self.auto_configs = auto_config.get("search_configs", "")
			self.auto_mode = six.ensure_str(auto_config.get("search_mode", "find_all"))
		else:
			auto_config["name"] = self.search_engine
			self.auto_configs = [auto_config]
		logger.debug("auto_configs: %s", self.auto_configs)
		search_config = self.auto_configs.pop(0)
		logger.debug("search_config: %s", search_config)
		self.search(search_config, search_topic)

	def search(self, search_config, search_topic):
		logger.info("...")
		self.loading.start(-1, _("Searching..."))
		self.__setTitle(search_topic, six.ensure_str(search_config["name"]))
		self.thread = threads.deferToThread(self.searchEngine, search_config, search_topic, self.searchCallback)

	def searchEngine(self, auto_config, search_topic, callback):
		logger.info("auto_config: %s, search_topic: %s", auto_config, search_topic)
		search_engine = auto_config["name"]
		search_config = getConfig(
			os.path.join(
				"/usr/lib/enigma2/python/Plugins/Extensions/Hydra/addons",
				search_engine + ".cfg"
			)
		)
		search_config.update(auto_config)
		logger.debug("search_config: %s", search_config)
		url_prefix = search_config.get("url_prefix", "http://None")
		max_entries = search_config.get("max_entries", 1)
		importlib.import_module(".addons." + search_engine, package="Plugins.Extensions.Hydra")
		exec("from .addons.%s import %s" % (search_engine, search_engine))
		s_obj = eval(search_engine)(url_prefix, max_entries)
		s_obj.query = search_topic
		s_obj.search()
		logger.debug("s_obj.rts_infos: %s", s_obj.rts_infos.info)
		reactor.callFromThread(callback, s_obj.rts_infos)

	def searchCallback(self, rts_infos):
		logger.info("rts_infos.info: %s", rts_infos.info)
		self.loading.stop()
		self.rts_infos.info += rts_infos.info[:]
		if self.thread:
			self.thread.cancel()
		logger.debug("auto_mode: %s, len(self.rts_info): %s", self.auto_mode, len(self.rts_infos.info))
		if self.auto_configs and not (self.auto_mode == "first_find" and len(self.rts_infos.info) > 0):
			search_config = self.auto_configs.pop(0)
			logger.debug("search_config: %s", search_config)
			self.__setTitle(self.search_topic, six.ensure_str(search_config["name"]))
			self.search(search_config, self.search_topic)
		else:
			self.__setTitle(self.search_topic, self.search_engine)
			self.createList()

	def createList(self):
		logger.info("...")
		menu_list = []
		if self.rts_infos:
			for one in self.rts_infos:
				menu_list.append(
					(
						one.name,
						one.magnet,
						one.date,
						one.size,
						"Peers: %s / %s" % (str(one.leechers), str(one.seeders)),
						one.engine,
					)
				)
		else:
			menu_list.append((_("No torrents found."), "", "", "", "", ""))
		self["menu"].setList(menu_list)

	def toggleSearchEngine(self):
		logger.info("...")
		self.search_engine = next_search_engine(self.search_engine)
		config.plugins.hydra.search_engine.value = self.search_engine
		config.plugins.hydra.search_engine.save()
		self.__setTitle(self.search_topic, self.search_engine)
		self.menu_list = []
		self["menu"].setList(self.menu_list)

	def cancel(self):
		if self.thread:
			self.thread.cancel()
		self.close()

	def ok(self):
		current = self["menu"].getCurrent()
		if current and current[1]:
			name = current[0]
			magnet = current[1]
			self.close(name, magnet)
		else:
			self.close()
