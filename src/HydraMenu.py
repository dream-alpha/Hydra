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
from twisted.internet import threads, reactor
from enigma import eTimer, gPixmapPtr
from Components.ActionMap import ActionMap
from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
from Components.Sources.List import List
from Components.PluginComponent import plugins
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.LoadPixmap import LoadPixmap
from .torr.torrclient import torrclient
from .torr.torrent import torrent
from .Debug import logger
from . import _
from .HydraEpisodes import HydraEpisodes
from .HydraConfig import HydraConfig
from .HydraSearch import HydraSearch
from .Utils import getStatus, prettySize
from .DelayTimer import DelayTimer
from .About import about
from .WebRequests import WebRequests
from .HydraVPN import isVPNActive, startVPN, stopVPN
from .Loading import Loading


WHERE_TMDB_INFOS = -98


class HydraMenu(Screen):
	def __init__(self, session, title="", original_title=""):
		self.search = original_title if original_title else title
		logger.info("search: %s", self.search)
		Screen.__init__(self, session)
		self.setTitle("%s - %s" % ("Hydra", _("Overview")))

		self["pic_loading"] = Pixmap()
		self["int_loading"] = Label()
		self["msg_loading"] = Label()
		self.loading = Loading(self["pic_loading"], self["int_loading"], self["msg_loading"], None)

		self["title"] = Label()
		self["overview"] = Label()
		self["vote_average"] = Label()
		self["key_red"] = Label(_("Delete"))
		self["key_green"] = Label(_("Search torrent"))
		self["key_yellow"] = Label(_("Update torrent"))
		self["key_blue"] = Label(_("Settings"))
		self["statusbar"] = Label()
		self["poster"] = Pixmap()
		self["stars"] = ProgressBar()
		self["starsbg"] = Pixmap()
		self["stars"].hide()
		self["starsbg"].hide()
		self.ratingstars = 0
		self["vpn"] = Pixmap()
		self.trnt = None
		self.menu_list = []
		self["menu"] = self.menu = List(self.menu_list, enableWrapAround=True)
		self.current_index = 0
		self.status_timer = eTimer()
		self.status_timer_conn = self.status_timer.timeout.connect(self.getStatus)
		self.torrclient = torrclient.getInstance()
		self.dt_show_tmdb_infos = None
		self['actions'] = ActionMap(
			["HydraActions"],
			{
				"cancel": self.cancel,
				"red": self.deleteMovie,
				"green": self.openVirtualKeyBoard,
				"yellow": self.updateList,
				"blue": self.openConfig,
				"menu": self.openConfig,
				"ok": self.ok,
				"down": self.menu.selectNext,
				"up": self.menu.selectPrevious,
				"left": self.menu.pageUp,
				"right": self.menu.pageDown,
				"info": self.about,
			},
			-1
		)

		self["menu"].onSelectionChanged.append(self.__selectionChanged)
		self.onLayoutFinish.append(self.__onLayoutFinish)
		self.onShow.append(self.__onShow)
		self.onHide.append(self.__onHide)

	def __onLayoutFinish(self):
		logger.info("...")
		self.loading.start(-1, _("Loading..."))
		threads.deferToThread(self.setupHydra, self.start)

	def __onShow(self):
		logger.info("...")
		self.status_timer.start(2000)

	def __onHide(self):
		logger.info("...")
		self.status_timer.stop()

	def about(self):
		about(self.session)

	def setupHydra(self, callback):
		if config.plugins.hydra.vpn_start.value:
			startVPN()
		self.torrclient.start_server(config.plugins.hydra.config_path.value)
		reactor.callFromThread(callback)

	def start(self):
		self.loading.stop()
		if self.search:
			search = self.search
			DelayTimer(50, self.searchTorrent, search)
			self.search = ""
		else:
			self.createList()

	def __selectionChanged(self):
		logger.info("...")
		if self.dt_show_tmdb_infos:
			self.dt_show_tmdb_infos.stop()
		self.dt_show_tmdb_infos = DelayTimer(300, self.showTMDBInfos)

	def showTMDBInfos(self):
		current = self.menu.getCurrent()
		logger.info("current: %s", current)
		if current:
			self.current_index = self.menu.getIndex()
			self.showPoster(str(current[3]))
			self["overview"].setText(str(current[4]))
			self.showVote(current[5], current[6])
			self["title"].setText(str(current[7]))
		else:
			self["poster"].instance.setPixmap(gPixmapPtr())
			self.hideVote()
			self["overview"].setText("")
			self["title"].setText("")

	def getStatus(self):
		# logger.info("status: %s", getStatus()[0])
		self['statusbar'].setText(getStatus()[0])
		self.showVPNStatus()

	def createList(self, ahash=None):
		self.menu_list = []
		self.torrclient.read_torrents()
		for one in self.torrclient.srv_torrents:
			self.menu_list.append(
				(
					str(one.title),
					one.hash,
					prettySize(one.torrent_size),
					one.poster,
					one.data.description,
					one.data.vote_average,
					one.data.vote_count,
					one.data.title,
					one.data.original_title,
				)
			)
		self.menu_list.sort(key=lambda x: x[1])
		if ahash:
			for i, trnt in enumerate(self.menu_list):
				# logger.debug("comparing: %s ? %s", ahash, trnt[1])
				if trnt[1] == ahash:
					self.current_index = i
		logger.debug("current_index: %s", self.current_index)
		self["menu"].setList(self.menu_list)
		self.menu.setIndex(self.current_index)
		self.showTMDBInfos()

	def cancel(self):
		if self.dt_show_tmdb_infos:
			self.dt_show_tmdb_infos.stop()
		self["menu"].onSelectionChanged = []
		self.torrclient.stop_server()
		if config.plugins.hydra.vpn_stop.value:
			stopVPN()
		self.close()

	def openVirtualKeyBoard(self):
		text = ""
		current = self.menu.getCurrent()
		logger.info("current: %s", current)
		if current and not config.plugins.hydra.use_last_search.value:
			text = str(current[7])
		else:
			text = config.plugins.hydra.last_search.value
		self.session.openWithCallback(self.searchTorrent, VirtualKeyBoard, title=_("Enter torrent to search"), text=text)

	def searchTorrent(self, search):
		logger.info("search: %s", search)
		if search:
			config.plugins.hydra.last_search.value = search
			config.plugins.hydra.last_search.save()
			self.session.openWithCallback(self.searchCallback, HydraSearch, search_topic=search)

	def searchCallback(self, title=None, magnet=None):
		if title and magnet:
			logger.info("title: %s", title)
			self.trnt = torrent()
			self.trnt.title = title
			self.trnt.link = magnet
			self.torrclient.add_torrent(self.trnt)
			self.getTMDBData(title)
			threads.deferToThread(self.torrclient.get_torrent, self.trnt, self.gotTorrent)
			self.createList(self.trnt.hash)
		else:
			self.createList()

	def gotTorrent(self, _retval):
		logger.info("...")
		self.currentIndex = self.menu.getIndex()
		self.createList()

	def getTMDBData(self, search):
		logger.info("search: %s", search)
		for plugin in plugins.getPlugins(where=WHERE_TMDB_INFOS):
			logger.debug("plugin.name: %s", plugin.name)
			if plugin.name == "TMDB":
				plugin(search, self.gotTMDBData)

	def gotTMDBData(self, res):
		logger.info("res: %s", res)
		if res:
			self.trnt.poster = res["cover_url"]
			self.trnt.data.description = res["overview"]
			self.trnt.data.vote_average = res["vote_average"]
			self.trnt.data.vote_count = res["vote_count"]
			self.trnt.data.title = res["title"]
			self.torrclient.update_torrent(self.trnt)
		self.createList()

	def deleteMovie(self):
		if self["menu"].getCurrent():
			message = _("Do you really want to delete this torrent?")
			self.session.openWithCallback(self.removeTorrent, MessageBox, message, timeout=0, default=True)

	def removeTorrent(self, answer):
		if answer:
			self.torrclient.remove_torrent(self.torrclient.srv_torrents[self["menu"].getCurrent()[1]])
			self.createList()

	def ok(self):
		current = self["menu"].getCurrent()
		if current:
			self.session.open(HydraEpisodes, current[1])

	def updateList(self):
		logger.info("...")
		current = self["menu"].getCurrent()
		if current:
			logger.debug("title: %s", current[0])
			self.trnt = self.torrclient.srv_torrents[current[1]]
			self.getTMDBData(current[0])
		else:
			self.createList()

	def showVPNStatus(self):
		vpn_pic = "/usr/lib/enigma2/python/Plugins/Extensions/Hydra/skin/images/vpn_inactive.png"
		if isVPNActive():
			vpn_pic = "/usr/lib/enigma2/python/Plugins/Extensions/Hydra/skin/images/vpn_active.png"
		self["vpn"].instance.setPixmap(LoadPixmap(vpn_pic))

	def showVote(self, vote_average, vote_count):
		rating_text = "%s: %0.1f (%s: %s)" % (_("Rating"), vote_average, _("Votes"), str(vote_count))
		self["vote_average"].setText(rating_text)
		self.ratingstars = int(10 * (float(str(vote_average))))
		self["starsbg"].show()
		self["stars"].setValue(self.ratingstars)
		self["stars"].show()

	def hideVote(self):
		self["vote_average"].setText("")
		self["starsbg"].hide()
		self["stars"].hide()

	def showPoster(self, url):
		if not url:
			path = "/usr/lib/enigma2/python/Plugins/Extensions/Hydra/skin/images/poster_none.png"
		else:
			path = os.path.join(config.plugins.hydra.poster_path.value, url.split("/")[-1])
			if not os.path.isfile(path):
				retval = WebRequests().downloadFile(url, path)
				if not retval:
					path = "/usr/lib/enigma2/python/Plugins/Extensions/Hydra/skin/images/poster_none.png"
		logger.debug("path: %s", path)
		self["poster"].instance.setPixmap(LoadPixmap(path))

	def openConfig(self):
		logger.info("...")
		self.session.openWithCallback(self.openConfigCallback, HydraConfig)

	def openConfigCallback(self):
		self.createList()
