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
from Components.config import config


instance = None


class LastPositions():
	def __init__(self):
		self.last_positions = {}
		self.load()

	@staticmethod
	def getInstance():
		global instance
		if instance is None:
			instance = LastPositions()
		return instance

	def get(self, episode):
		return self.last_positions.get(episode, (0, 0))

	def put(self, episode, last_position, percent):
		self.last_positions[episode] = (last_position, percent)
		self.save()

	def load(self):
		self.last_positions = json.loads(config.plugins.hydra.last_positions.value)

	def save(self):
		config.plugins.hydra.last_positions.value = json.dumps(self.last_positions)
		config.plugins.hydra.last_positions.save()
