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


import glob
from enigma import eTimer, gPixmapPtr
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from .Debug import logger
from .SkinUtils import getSkinPath


ACTIVITY_TIMER_DELAY = 250


class Loading():

	def __init__(self, pic_loading, int_loading, msg_loading, summaries):
		logger.debug("...")
		self.activity_timer = eTimer()
		self.activity_timer_conn = self.activity_timer.timeout.connect(self.doActivityTimer)
		self.pic_index = 0
		self.pic_loading = pic_loading
		self.int_loading = int_loading
		self.msg_loading = msg_loading
		self.summaries = summaries
		self.pics = len(glob.glob(resolveFilename(SCOPE_PLUGINS, "Extensions/Hydra/skin/images/spinner/*.png")))
		logger.debug("self.pics: %s", self.pics)

	def start(self, seconds=-1, msg=""):
		logger.debug("...")
		self.seconds = seconds
		self.activity_timer.start(ACTIVITY_TIMER_DELAY, False)
		self.pic_loading.instance.setShowHideAnimation("")
		if self.seconds > -1:
			self.int_loading.setText("%2d" % seconds)
		self.msg_loading.setText(msg)
		if self.summaries:
			self.summaries[0]["background"].instance.setPixmap(LoadPixmap(getSkinPath("skin_default/display_bg.png"), cached=False))
			self.summaries[0]["lcd_pic_loading"].setShowHideAnimation("")
			self.summaries[0]["lcd_pic_loading"].show()

	def stop(self, msg=""):
		logger.debug("...")
		self.activity_timer.stop()
		self.pic_loading.instance.setPixmap(gPixmapPtr())
		self.int_loading.instance.setText("")
		self.msg_loading.instance.setText(msg)
		if self.summaries:
			self.summaries[0]["background"].hide()
			self.summaries[0]["lcd_pic_loading"].hide()

	def doActivityTimer(self):
		path = getSkinPath("images/spinner/wait%s.png" % (self.pic_index + 1))
		# logger.debug("pic_index: %s", self.pic_index)
		pixmap = LoadPixmap(path, cached=False)
		self.pic_loading.instance.setPixmap(pixmap)
		if self.pic_index % 4 == 0 and self.seconds > -1:
			self.int_loading.setText("%2d" % self.seconds)
			self.seconds -= 1 if self.seconds else 0
		if self.summaries:
			self.summaries[0]["lcd_pic_loading"].instance.setPixmap(pixmap)
		self.pic_index = (self.pic_index + 1) % self.pics
