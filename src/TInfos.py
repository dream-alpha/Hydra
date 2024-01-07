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


from .TInfo import TInfo


class TInfos(object):
	def __init__(self, info=None, search_obj=None):
		self.info = []
		self.search_obj = search_obj
		if info:
			self.info = info
		self.counter = 0

	def __iter__(self):
		self.counter = 0
		return self

	def item(self, index):
		return TInfo(self.info[index], self.search_obj)

	def next(self):
		if self.counter < len(self.info):
			ti = self.item(self.counter)
			self.counter += 1
			return ti
		raise StopIteration

	__next__ = next

	def __getitem__(self, index):
		return self.item(index)

	def __len__(self):
		return len(self.info)

	def count(self):
		return len(self.info)

	def append(self, info):
		self.info.append(info)
