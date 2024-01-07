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


import json


class t_data(object):
	keynode = "E2TorrPlayer"

	def __init__(self, input_json=""):
		self.data_dict = {t_data.keynode: {}}
		self.load_json(input_json)

	def load_json(self, input_json):
		if not input_json:
			input_json = ""
		start = '{"%s' % t_data.keynode
		if input_json.startswith(start):
			self.data_dict = json.loads(input_json)
		elif input_json.startswith("{"):
			try:
				self.data_dict = {t_data.keynode: {"extradata": json.loads(input_json)}}
			except Exception:
				pass
		else:
			self.data_dict = {t_data.keynode: {"description": input_json}}

	@property
	def json(self):
		return json.dumps(self.data_dict)

	@json.setter
	def json(self, val):
		self.load_json(val)

	@property
	def description(self):
		return self.data_dict[t_data.keynode].get("description", "")

	@description.setter
	def description(self, val):
		self.data_dict[t_data.keynode]["description"] = val

	@property
	def name(self):
		return self.data_dict[t_data.keynode].get("name", "")

	@name.setter
	def name(self, val):
		self.data_dict[t_data.keynode]["name"] = val

	@property
	def original_title(self):
		return self.data_dict[t_data.keynode].get("original_title", "")

	@original_title.setter
	def original_title(self, val):
		self.data_dict[t_data.keynode]["original_title"] = val

	@property
	def title(self):
		return self.data_dict[t_data.keynode].get("title", "")

	@title.setter
	def title(self, val):
		self.data_dict[t_data.keynode]["title"] = val

	@property
	def vote_average(self):
		return self.data_dict[t_data.keynode].get("vote_average", 0)

	@vote_average.setter
	def vote_average(self, val):
		self.data_dict[t_data.keynode]["vote_average"] = val

	@property
	def vote_count(self):
		return self.data_dict[t_data.keynode].get("vote_count", 0)

	@vote_count.setter
	def vote_count(self, val):
		self.data_dict[t_data.keynode]["vote_count"] = val

	@property
	def extrajson(self):
		return json.dumps(self.data_dict[t_data.keynode].get("extradata", {}))

	@extrajson.setter
	def extrajson(self, val):
		self.data_dict[t_data.keynode]["extradata"] = json.loads(val) if val else {}

	@property
	def extradata(self):
		return self.data_dict[t_data.keynode].get("extradata", {})

	@extradata.setter
	def extradata(self, val):
		self.data_dict[t_data.keynode]["extradata"] = val
