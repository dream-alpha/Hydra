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


import json
import re
import time
import os
import copy
import subprocess
import base64
import six
from twisted.internet import reactor
from six.moves.urllib.request import urlopen, Request
from six.moves.urllib.parse import quote
from .torrent import torrent
from .torrents import torrents
from .torrsettings import torrsettings
from .Utils import encodeUtf8, get_pid, getConfig
from ..WebRequests import WebRequests
from ..Debug import logger


instance = None
torrserver_path = '/usr/bin/TorrServer'
MEDIA_FORMATS = (
	".mpg", ".vob", ".m4v", ".mkv", ".avi", ".divx", ".dat", ".flv", ".mp4", ".mov", ".wmv",
	".asf", ".3gp", ".3g2", ".mpeg", ".mpe", ".rm", ".rmvb", ".ogm", ".ogv", ".m2ts", ".mts", ".webm",
	".pva", ".wtv", ".ts", ".iso", ".img", ".nrg", ".dts", ".mp3", ".wav", ".wave", ".wv", ".oga", ".ogg",
	".flac", ".m4a", ".mp2", ".m2a", ".wma", ".ac3", ".mka", ".aac", ".ape", ".alac", ".amr", ".au", ".mid"
)


def base64encodestring(x):
	return base64.encodebytes(x.encode('utf-8')).decode('utf-8').replace('\n', '') if six.PY3 else base64.encodestring(x).replace('\n', '')


class torrclient(object):
	def __init__(self):
		self.srv_protocol = "http"
		self.srv_host = "127.0.0.1"
		self.srv_port = 8090
		self.srv_torrents = torrents({})
		self.srv_settings = torrsettings()
		self.srv_timeout = 90
		self.srv_login = None
		self.srv_password = None
		self.filter_ext = MEDIA_FORMATS

	@staticmethod
	def getInstance():
		global instance
		if instance is None:
			instance = torrclient()
			instance.url = getConfig().get("server_url", "http://127.0.0.1:8090")
		return instance

	@property
	def url(self):
		return "{protocol}://{host}:{port}".format(protocol=self.srv_protocol, host=self.srv_host, port=self.srv_port)

	@url.setter
	def url(self, val):
		try:
			tmp = re.split(r'://|:|/', val)
			self.srv_protocol = tmp[0]
			self.srv_host = tmp[1]
			self.srv_port = int(tmp[2])
		except Exception:
			pass

	@property
	def torr_version(self):
		retval = "None"
		cmd = self.url + '/echo'
		tmp = self.request_url(cmd, {})
		if tmp["result"]:
			retval = tmp["data"]
		# logger.debug("retval: %s", retval)
		return retval

	@property
	def settings(self):
		return self.srv_settings

	def request_url(self, url, values, timeout=0):
		# logger.info("url: %s, values: %s", url, values)
		retval = {"result": False, "data": '', "error": None}
		try:
			if values:
				req = Request(url, bytes(json.dumps(values), encoding="utf-8") if six.PY3 else json.dumps(values))
			else:
				req = Request(url)
			if not timeout:
				timeout = self.srv_timeout
			resp = urlopen(req, timeout=timeout)
			retval["data"] = resp.read()
			if six.PY3:
				retval["data"] = retval["data"].decode()
			retval["result"] = True
		except Exception as e:
			retval["error"] = e
			logger.error("exception: %s, url: %s, values: %s", e, url, values)
		return retval

	def read_torrents(self):
		""" read info about all torrents (doesn't fill file_stats info) """
		cmd = self.url + '/torrents'
		params = {'action': "list"}
		tmp = self.request_url(cmd, params)
		if tmp["data"]:
			self.srv_torrents = torrents(json.loads(tmp["data"]))
		return tmp["result"]

	def get_torrent(self, trnt, callback):
		""" read extended info of one torrent """
		retval = None
		cmd = '{url}/stream/fname?link={lnk}&stat'.format(url=self.url, lnk=trnt.hash)
		response = self.request_url(cmd, {})
		if response["result"]:
			trnt.info.update(json.loads(response["data"]))
			trnt.info["file_stats"] = [file for file in trnt.info.get("file_stats", []) if os.path.splitext(file.get("path", ""))[1] in self.filter_ext]
			retval = trnt
		reactor.callFromThread(callback, retval)

	def add_torrent(self, trnt):
		""" add torrent to server's list """
		cmd = self.url + '/torrents'
		params = {
			'action': "add",
			"link": trnt.link,
			"title": trnt.title,
			"poster": trnt.poster,
			"data": trnt.data.json,
			"save_to_db": trnt.save_to_db
		}
		tmp = self.request_url(cmd, params)
		if tmp["data"]:
			trnt.info.update(json.loads(tmp["data"]))
		logger.debug("trnt: %s", trnt)
		logger.debug("trnt.info: %s", trnt.info)
		return tmp["result"]

	def remove_torrent(self, trnt):
		""" delete torrent from TorrServer """
		cmd = self.url + '/torrents'
		params = {'action': "rem", "hash": trnt.hash, "save_to_db": trnt.save_to_db}
		tmp = self.request_url(cmd, params)
		return tmp["result"]

	def update_torrent(self, trnt):
		""" update torent info """
		cmd = self.url + '/torrents'
		params = {
			'action': "set",
			'hash': trnt.hash,
			"title": trnt.title,
			"poster": trnt.poster,
			"data": trnt.data.json,
			"save_to_db": trnt.save_to_db
		}
		tmp = self.request_url(cmd, params)
		if tmp["data"]:
			trnt.info.update(json.loads(tmp["data"]))
		logger.debug("trnt: %s", trnt)
		logger.debug("trnt.info: %s", trnt.info)
		return tmp["result"]

	def get_stream_url(self, trnt, file_id):
		""" return stream dictionary: (name, path, stream) """
		f_obj = trnt.files.file_by_id(file_id) if isinstance(file_id, int) else file_id
		file_path = quote(encodeUtf8(f_obj.path))
		retval = {
			"name": trnt.title,
			"file": f_obj.path,
			"stream": '{url}/stream/{path}?link={link}&index={id}&play'.format(url=self.url, path=file_path, link=trnt.hash, id=f_obj.id)
		}
		return retval

	def get_onlyplay_url(self, trnt, file_id=1):
		link = trnt.link if isinstance(trnt, torrent) else trnt
		return '{url}/stream/fname?link={lnk}&index={idx}&play'.format(url=self.url, lnk=quote(encodeUtf8(link)), idx=file_id)

	def preload_torrent(self, trnt, file_id, callback):
		""" preload torrent, returns the stream url """
		retval = ""
		f_obj = trnt.files.file_by_id(file_id) if isinstance(file_id, int) else file_id
		# file_path = quote(f_obj.path)
		file_path = quote(encodeUtf8(f_obj.path))
		cmd = '{url}/stream/{path}?link={link}&index={id}&preload'.format(url=self.url, path=file_path, link=trnt.hash, id=f_obj.id)
		tmp = self.request_url(cmd, {})
		if tmp["result"]:
			retval = self.get_stream_url(trnt, file_id)["stream"]
		logger.debug("retval: %s", retval)
		reactor.callFromThread(callback, retval)

	def torrent_by_hash(self, ahash):
		trnt = None
		for one in self.srv_torrents:
			if one.info["hash"] == ahash:
				trnt = torrent()
				trnt.info = copy.deepcopy(one.info)
				break
		return trnt

	def read_torr_settings(self):
		retval = False
		cmd = self.url + "/settings"
		params = {'action': "get"}
		tmp = self.request_url(cmd, params)
		if tmp["result"]:
			self.srv_settings = torrsettings(json.loads(tmp["data"]))
			retval = True
		return retval

	def save_torr_settings(self, reread=True):
		retval = False
		cmd = self.url + "/settings"
		changed = self.srv_settings.get_changed()
		if changed:
			params = {'action': "set", "sets": changed}
			tmp = self.request_url(cmd, params)
			if tmp["result"]:
				retval = True
				if reread:
					self.read_torr_settings()
		else:
			retval = True
		return retval

	def test_connection(self):
		return self.torr_version != "None"

	def start_server(self, config_path):
		retval = False
		if os.path.isfile(torrserver_path) and not get_pid("TorrServer"):
			os.system('export GODEBUG=madvdontneed=1')
			cmd = "%s --port %s --path %s &" % (torrserver_path, self.srv_port, config_path)
			os.system(cmd)
			for _i in range(10):
				time.sleep(1)
				if self.test_connection():
					break
			else:
				retval = False
		return retval

	def stop_server(self):
		cmd = self.url + '/shutdown'
		tmp = self.request_url(cmd, {})
		if not tmp["result"]:
			os.popen("killall -9 TorrServer").read()

	def is_server_installed(self):
		return os.path.exists(torrserver_path)

	def get_server_download_url(self):
		url = ""
		version = ""
		repolist = getConfig().get("repolist", "https://releases.yourok.ru/torr/server_release.json")
		logger.debug("repolist: %s", repolist)
		arch = subprocess.check_output('uname -m; exit 0', shell=True)
		arch = six.ensure_str(arch.strip())
		content = WebRequests().getContent(repolist)
		repo_json = json.loads(content)
		version = repo_json.get('version')
		if repo_json:
			if arch == 'armv7l':
				url = repo_json.get('links').get('linux-arm7')
			elif arch == 'mips':
				url = repo_json.get('links').get('linux-mipsle')
			elif arch == "aarch64":
				url = repo_json.get("links").get("linux-arm64")
		return version, url

	def install_server(self, url=""):
		logger.info("url: %s", url)
		if not url:
			_version, url = self.get_server_download_url()
		retval = WebRequests().downloadFile(url, torrserver_path)
		subprocess.call(["chmod", "u=rwx,g=rx,o=rx", torrserver_path])
		return retval

	def update_server(self):
		retval = False
		version, url = self.get_server_download_url()
		installed_version = self.torr_version
		logger.debug("version: %s, installed_version: %s", version, installed_version)
		if version != installed_version:
			self.stop_server()
			self.install_server(url)
			retval = True
		return retval
