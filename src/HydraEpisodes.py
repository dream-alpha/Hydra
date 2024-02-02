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


from twisted.internet import threads
from enigma import eServiceReference
from Components.ActionMap import ActionMap
from Components.config import config
from Components.Label import Label
from Components.Sources.List import List
from Screens.Screen import Screen
from .torr.torrclient import torrclient
from . import _
from .HydraPlayer import HydraPlayer
from .Utils import prettySize
from .Debug import logger
from .LastPositions import LastPositions
from .Loading import Loading


class HydraEpisodes(Screen):
	def __init__(self, session, ahash):
		logger.info("ahash: %s", ahash)
		self.ahash = ahash
		Screen.__init__(self, session)
		self.last_positions_instance = LastPositions.getInstance()
		self.torrclient = torrclient.getInstance()
		self.torrent = self.torrclient.srv_torrents[ahash]
		title = str(self.torrent.data.title)
		logger.debug("title: %s", title)
		self.setTitle("%s - %s - %s" % ("Hydra", _("Episodes"), title if title else _("None")))
		self.loading = Loading(self, None)
		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Play"))
		self["key_yellow"] = Label(_("Preload buffer"))
		self["key_blue"] = Label(_("Reset progress"))
		self.thread = None
		self.menu_list = []
		self["menu"] = self.menu = List(self.menu_list, enableWrapAround=True)
		self["menu"].onSelectionChanged.append(self.__selectionChanged)
		self["actions"] = ActionMap(
			["HydraActions"],
			{
				"cancel": self.cancel,
				"red": self.cancel,
				"green": self.play,
				"back": self.cancel,
				"yellow": self.preload,
				"ok": self.play,
				"blue": self.clear,
			},
			-1
		)
		self.onLayoutFinish.append(self.__onLayoutFinish)

	def __onLayoutFinish(self):
		self.menu_list = []
		# self.menu_list.append(("", "", "", "", "", ""))
		self["menu"].setList(self.menu_list)
		self.loading.start(-1, _("Loading..."))
		self.thread = threads.deferToThread(self.torrclient.get_torrent, self.torrent, self.createList)

	def __selectionChanged(self):
		logger.info("...")

	def createList(self, trnt):
		logger.info("...")
		self.loading.stop()
		self.thread = None
		self.trnt = trnt
		self.menu_list = []
		if trnt:
			self.last_positions_instance.load()
			logger.debug("trnt.info: %s", trnt.info)
			for real_id, one in enumerate(trnt.files):
				logger.debug("real_id: %s, one: %s", real_id, one)
				stream_info = self.torrclient.get_stream_url(trnt, one.id)
				stream = stream_info["stream"]
				torrepisode = str(one.path)
				torrepisode = torrepisode.split("/")[-1]
				episode = stream.split("?")[1].replace("&play", "")
				_last_position, percent = self.last_positions_instance.get(episode)
				percent_string = "%02d%%" % percent
				self.menu_list.append((torrepisode, stream, prettySize(one.length), real_id, percent_string, percent))
		if not self.menu_list:
			self.menu_list.append(("", "", "", "", "", ""))
		self["menu"].setList(self.menu_list)

	def cancel(self):
		self.loading.stop()
		if self.thread:
			self.thread.cancel()
		self.close()

	def clear(self):
		current = self["menu"].getCurrent()
		if current and current[1]:
			stream = current[1]
			episode = stream.split("?")[1].replace("&play", "")
			self.last_positions_instance.put(episode, 0, 0)
			self.createList(self.trnt)

	def preload(self):
		logger.info("...")
		current = self["menu"].getCurrent()
		if not self.thread and current and current[1]:
			self.loading.start(90, _("Preloading buffer..."))
			self.thread = threads.deferToThread(self.torrclient.preload_torrent, self.trnt, self.trnt.files[current[3]].id, self.preloadCallback)

	def preloadCallback(self, retval):
		logger.info("retval: %s", retval)
		msg = _("Preload timed out, but you can still start playback.") if not retval else ""
		self.loading.stop(msg)

	def play(self):
		self.loading.stop()
		if self.thread:
			self.thread.cancel()
		current = self["menu"].getCurrent()
		if current and current[1]:
			stream = str(current[1])
			logger.debug("stream: %s", stream)
			if stream:
				episode = stream.split("?")[-1].replace("&play", "")
				logger.debug("episode: %s", episode)
				service = eServiceReference(int(config.plugins.hydra.player.value), 0, stream)
				service.setName(current[0])
				self.session.openWithCallback(self.playCallback, HydraPlayer, service=service, episode=episode)

	def playCallback(self):
		logger.info("...")
		self.createList(self.trnt)
