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


from enigma import iPlayableService
from Components.ServiceEventTracker import ServiceEventTracker
from Screens.InfoBar import InfoBar, MoviePlayer
from Screens.MessageBox import MessageBox
from .Debug import logger
from .LastPositions import LastPositions
from . import _


class HydraPlayer(MoviePlayer):
	def __init__(self, session, service, episode):
		logger.info("name: %s", service.getName())
		logger.info("path: %s", service.getPath())
		MoviePlayer.__init__(self, session, service)  # , episode)
		self.skinName = 'MoviePlayer'
		self.episode = episode
		self.servicelist = InfoBar.instance and InfoBar.instance.servicelist
		ServiceEventTracker(
			screen=self,
			eventmap={
				iPlayableService.evStart: self.__startTorrent,
				iPlayableService.evVideoSizeChanged: self.__startTorrent
			}
		)
		self.started = False
		self.last_positions_instance = LastPositions.getInstance()

	def __startTorrent(self):
		if not self.started:
			self.started = True
			self.last_position, _percent = self.last_positions_instance.get(self.episode)
			logger.debug("last_position: %s", self.last_position)
			if self.last_position:
				self.session.openWithCallback(
					self.messageBoxCallback,
					MessageBox,
					text=_("Resume playback from previous position?"),
					timeout=5,
					default=False
				)

	def messageBoxCallback(self, answer):
		if answer:
			service = self.session.nav.getCurrentService()
			seek = service and service.seek()
			if seek:
				seek.seekTo(self.last_position)

	def leavePlayerOnExit(self):
		self.is_closing = True
		self.leavePlayer()

	def leavePlayer(self):
		service = self.session.nav.getCurrentService()
		seek = service and service.seek()
		if seek:
			playposition = seek.getPlayPosition()[1]
			length = seek.getLength()[1]
			logger.debug("length: %s", length)
			percent = int(float(playposition) / float(length) * 100) if length else 0
			logger.debug("episode: %s, position: %s, percent: %s", self.episode, playposition, percent)
			self.last_positions_instance.put(self.episode, playposition, percent)
		self.close()

	def doEofInternal(self, playing):
		if self.execing and playing:
			self.leavePlayer()

	def showMovies(self):
		pass
