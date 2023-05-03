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


from .t_file import t_file


class t_files(object):
	def __iter__(self):
		self.counter = 0
		return self

	def __init__(self, file_stats):
		self.files = file_stats
		self.counter = 0

	def next(self):
		if self.counter < len(self.files):
			f_s = t_file(
				ident=self.files[self.counter]["id"],
				path=self.files[self.counter].get("path", ""),
				length=self.files[self.counter].get("length", 0)
			)
			self.counter += 1
			return f_s
		raise StopIteration

	__next__ = next

	def __getitem__(self, index):
		return t_file(
			ident=self.files[index]["id"],
			path=self.files[index].get("path", ""),
			length=self.files[index].get("length", 0)
		)

	def __len__(self):
		return len(self.files)

	def count(self):
		return len(self.files)

	def file_by_id(self, ident):
		for idx, val in enumerate(self.files):
			if val["id"] == ident:
				retval = self.__getitem__(idx)
				break
		else:
			retval = None
		return retval
