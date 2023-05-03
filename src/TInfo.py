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


class TInfo(object):
	def __init__(self, info, search_obj=None):
		self.info = info  # {"url": "", "date": '', "name": "", "size": "", "seeders": "", "leechers": "", "magnet": '', "file_url": "", "engine": ""}
		self.search_obj = search_obj

	@property
	def detail_url(self):
		return self.info.get("url", "")

	@property
	def date(self):
		return self.info.get("date", "")

	@property
	def name(self):
		return self.info.get("name", "")

	@property
	def size(self):
		return self.info.get("size", "")

	@property
	def magnet(self):
		return self.info.get("magnet", "")

	@property
	def file_url(self):
		return self.info.get("file_url", "")

	@property
	def seeders(self):
		return self.info.get("seeders", "")

	@property
	def leechers(self):
		return self.info.get("leechers", "")

	@property
	def engine(self):
		return self.info.get("engine", "")
