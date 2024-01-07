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


import os
import json
import subprocess
import base64
import six
from six import PY3
from ..FileUtils import readFile
from ..Debug import logger


def encodeUtf8(x):
	# return x.encode("utf-8", "ignore") if six.PY2 else x
	return six.binary_type(x.encode("utf-8"))


def decodeUtf8(x):
	# return x.decode("utf-8", "ignore") if six.PY2 else x
	return six.text_type(x, encoding="utf-8")


def base64encodestring(x):
	return base64.encodebytes(x.encode('utf-8')).decode('utf-8').replace('\n', '') if PY3 else base64.encodestring(x).replace('\n', '')


def get_pid(name):
	try:
		return subprocess.check_output(['pidof', name])
	except subprocess.CalledProcessError:
		return False


def get_text_between(txt, s_delim, e_delim, s_position=0):
	res = {"text": "", "position": -1}
	first = txt.find(s_delim, s_position)
	if first >= 0:
		first += len(s_delim)
		end = txt.find(e_delim, first)
		if end:
			res["text"] = txt[first: (end if end >= 0 else None)]
			res["position"] = end + len(e_delim)
	return res


def hash_from_magnet(magnet):
	return get_text_between(magnet, ':btih:', '&')["text"]


def is_magnet(magnet):
	return magnet.startswith('magnet:?xt=urn:btih:')


def getConfig(cfg_path=""):
	hydra_config = {}
	if os.path.isfile(cfg_path):
		data = readFile(cfg_path)
		hydra_config = json.loads(data)
	logger.debug("hydra_config: %s", hydra_config)
	return hydra_config
