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


from twisted.internet import threads, reactor
from enigma import eTimer
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import config, configfile, getConfigListEntry
from Components.Label import Label
from Components.Pixmap import Pixmap
from Screens.Screen import Screen
from Screens.LocationBox import LocationBox
from .Debug import logger
from . import _
from .Utils import getStatus
from .torr.torrclient import torrclient
from .Loading import Loading


class HydraConfig(ConfigListScreen, Screen):
	def __init__(self, session):
		logger.info("...")
		Screen.__init__(self, session)
		ConfigListScreen.__init__(self, [], session=session)
		self.session = session
		self["statusbar"] = Label()
		self['key_red'] = Label(_("Cancel"))
		self['key_green'] = Label(_("Save"))
		self["key_yellow"] = Label()
		self["key_blue"] = Label()
		self.setTitle("%s - %s" % ("Hydra", _("Settings")))

		self["pic_loading"] = Pixmap()
		self["int_loading"] = Label()
		self["msg_loading"] = Label()
		self.loading = Loading(self["pic_loading"], self["int_loading"], self["msg_loading"], None)

		self['actions'] = ActionMap(
			["HydraActions"],
			{
				'ok': self.ok,
				'green': self.save,
				'yellow': self.doStartStop,
				"blue": self.installServer,
				'cancel': self.exit,
				'red': self.exit
			},
			-2
		)

		self.torrclient = torrclient.getInstance()
		self.stimer = eTimer()
		self.stimer_conn = self.stimer.timeout.connect(self.getStatus)
		self.onClose.append(self.stimer.stop)
		self.onLayoutFinish.append(self.__onLayoutFinish)

	def __onLayoutFinish(self):
		self.setConfigList()
		self.stimer.start(2000)

	def setConfigList(self, _configElement=None):
		self.list = []
		self.config_path = getConfigListEntry(_("Server config file path:"), config.plugins.hydra.config_path)
		self.list.append(getConfigListEntry(_("Start server when DreamOS starts:"), config.plugins.hydra.autostart))
		self.list.append(self.config_path)
		self.poster_path = getConfigListEntry(_("Poster path:"), config.plugins.hydra.poster_path)
		self.list.append(self.poster_path)
		self.list.append(getConfigListEntry(_("Search engine:"), config.plugins.hydra.search_engine))
		self.list.append(getConfigListEntry(_("Use last search:"), config.plugins.hydra.use_last_search))
		self.list.append(getConfigListEntry(_("Start VPN when plugin starts:"), config.plugins.hydra.vpn_start))
		self.list.append(getConfigListEntry(_("Stop VPN when plugin exits:"), config.plugins.hydra.vpn_stop))
		self['config'].setList(self.list)

	def ok(self):
		logger.info("...")
		if self['config'].getCurrent() == self.config_path:
			self.DirBrowser(config.plugins.hydra.config_path.value, config.plugins.hydra.config_bookmarks)
		elif self['config'].getCurrent() == self.poster_path:
			self.DirBrowser(config.plugins.hydra.poster_path.value, config.plugins.hydra.poster_bookmarks)
		else:
			self.save()

	def DirBrowser(self, path, bookmarks):
		logger.info("path: %s, bookmarks: %s", path, bookmarks)
		inhibitDirs = [
			'/bin', '/boot', '/dev', '/lib', '/proc', '/run', '/sbin', '/sys', '/share'
		]
		try:
			self.session.openWithCallback(
				self.DirBrowserX,
				LocationBox,
				windowTitle=self['config'].getCurrent()[0],
				text=_("Choose Directory"),
				currDir=path,
				bookmarks=bookmarks,
				editDir=True,
				inhibitDirs=inhibitDirs,
				minFree=5
			)

		except Exception as e:
			logger.error('Directory get failed: %s', e)

	def DirBrowserX(self, path):
		if path:
			if self['config'].getCurrent() == self.config_path:
				config.plugins.hydra.config_path.setValue(path)
			else:
				config.plugins.hydra.poster_path.setValue(path)

	def save(self):
		self.torrclient.stop_server()
		config.plugins.hydra.save()
		configfile.save()
		self.torrclient.start_server(config.plugins.hydra.config_path.value)
		self.close()

	def exit(self):
		for x in self['config'].list:
			x[1].cancel()
		self.close()

	def getStatus(self):
		status = getStatus()
		# logger.info("status: %s", status)
		self['statusbar'].setText(status[0])
		self["key_yellow"].setText(status[1])
		self["key_blue"].setText(status[2])

	def installServer(self):
		self.loading.start(-1, _("Installing Server..."))
		threads.deferToThread(self.installUpdate, self.installUpdateCallback)

	def installUpdate(self, callback):
		res = False
		msg = _("Server installed/updated")
		if not self.torrclient.is_server_installed():
			res = self.torrclient.install_server()
			if not res:
				msg = _("Server installation/update failed.")
		else:
			res = self.torrclient.update_server()
			if not res:
				msg = _("No update found for TorrServer")
		reactor.callFromThread(callback, res, msg)

	def installUpdateCallback(self, res, msg):
		self.loading.stop()
		self['statusbar'].setText(msg)
		if res is True:
			self.torrclient.start_server(config.plugins.hydra.config_path.value)
			self["key_blue"].setText(_("Update server"))

	def doStartStop(self):
		if self.torrclient.test_connection():
			self.torrclient.stop_server()
		else:
			self.torrclient.start_server(config.plugins.hydra.config_path.value)
