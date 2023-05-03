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


from .t_files import t_files
from .t_data import t_data


class torrent(object):
	def __init__(self, title=None, poster=None, data=None, link=None):
		self.info = {
			"title": title, "poster": poster, "data": data, "timestamp": None, "name": None,
			"stat": None, "stat_string": None, "torrent_size": 0, "total_peers": None,
			"pending_peers": None, "active_peers": None, "connected_seeders": None,
			"bytes_written": None, "bytes_read": None,
			"file_stats": None, "hash": None, "save_to_db": True, "link": link, "extradata": t_data(data)
		}

	@property
	def title(self):
		return self.info.get("title", None)

	@title.setter
	def title(self, val):
		self.info["title"] = val

	@property
	def poster(self):
		return self.info.get("poster", None)

	@poster.setter
	def poster(self, val):
		self.info["poster"] = val

	@property
	def data(self):
		return self.info.get("extradata", None)

	@data.setter
	def data(self, val):
		if isinstance(val, t_data):
			self.info["extradata"] = val
		else:
			self.info["extradata"] = t_data(val)

	@property
	def save_to_db(self):
		return self.info.get("save_to_db", True)

	@save_to_db.setter
	def save_to_db(self, val):
		self.info["save_to_db"] = val

	@property
	def hash(self):
		return self.info.get("hash", None)

	@property
	def status(self):
		return self.info.get("stat", None)

	@property
	def status_string(self):
		return self.info.get("stat_string", None)

	@property
	def torrent_size(self):
		return self.info.get("torrent_size", 0)

	@property
	def total_peers(self):
		return self.info.get("total_peers", None)

	@property
	def pending_peers(self):
		return self.info.get("pending_peers", None)

	@property
	def active_peers(self):
		return self.info.get("active_peers", None)

	@property
	def connected_seeders(self):
		return self.info.get("connected_seeders", None)

	@property
	def bytes_written(self):
		return self.info.get("bytes_written", None)

	@property
	def bytes_read(self):
		return self.info.get("bytes_read", None)

	@property
	def timestamp(self):
		return self.info.get("timestamp", None)

	@property
	def files(self):
		return t_files(self.info.get("file_stats", []))

	@property
	def link(self):
		return self.info.get("link", None)

	@link.setter
	def link(self, val):
		self.info["link"] = val
