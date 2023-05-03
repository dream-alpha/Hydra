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


from six import text_type
from .torrent import torrent
from .t_data import t_data


class torrents(object):
	def __iter__(self):
		self.counter = 0
		return self

	def __init__(self, trnts_info):
		self.torrents_info = []
		for one in trnts_info:
			trnt = torrent()
			for key, val in one.items():
				trnt.info[key] = val
			trnt.data = t_data(trnt.info.get("data", ""))
			self.torrents_info.append(trnt)
		self.counter = 0

	def set_item(self, old_tinfo, new_tinfo):
		pass

	def next(self):
		if self.counter < len(self.torrents_info):
			trnt = self.torrents_info[self.counter]
			self.counter += 1
			return trnt
		raise StopIteration

	__next__ = next

	def __getitem__(self, index):
		if isinstance(index, text_type):
			retval = self.torrent_by_hash(index)
			if retval is None:
				raise IndexError('list index out of range')
		else:
			retval = self.torrents_info[index]
		return retval

	def __setitem__(self, index, trnt):
		self.torrents_info[index] = trnt

	def __len__(self):
		return len(self.torrents_info)

	def count(self):
		return len(self.torrents_info)

	def append(self, trnt):
		self.torrents_info.append(trnt)

	def insert(self, index, trnt):
		self.torrents_info.insert(index, trnt)

	def index(self, val):
		if isinstance(val, text_type):
			newval = self.torrent_by_hash(val)
			if newval is None:
				raise ValueError('%s is not in list' % val)
		else:
			newval = val
		return self.torrents_info.index(newval)

	def torrent_by_hash(self, ahash):
		trnt = None
		for one in self.torrents_info:
			if one.hash == ahash:
				trnt = one
				break
		return trnt
