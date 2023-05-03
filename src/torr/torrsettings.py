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


import copy


class torrsettings(object):
	def __init__(self, sets=None):
		if sets is None:
			sets = {}
		self.sets = sets
		self.init_sets = copy.deepcopy(sets)

	def get_changed(self):
		flag = False
		for key, val in self.sets.items():
			if (key in self.init_sets.keys()) and self.init_sets[key] != val:
				flag = True
		return self.sets if flag else {}

	@property
	def CacheSize(self):
		#  int64 // in byte, def 200 mb
		return self.sets.get("CacheSize", None)

	@CacheSize.setter
	def CacheSize(self, val):
		self.sets["CacheSize"] = val

	@property
	def PreloadBuffer(self):
		# bool
		return self.sets.get("PreloadBuffer", None)

	@PreloadBuffer.setter
	def PreloadBuffer(self, val):
		if self.sets.get("PreloadBuffer", None):
			self.sets["PreloadBuffer"] = val

	@property
	def PreloadCache(self):
		# int
		return self.sets.get("PreloadCache", None)

	@PreloadCache.setter
	def PreloadCache(self, val):
		if self.sets.get("PreloadCache", None):
			self.sets["PreloadCache"] = val

	@property
	def ReaderReadAHead(self):
		# int // in percent, 5%-100%,
		return self.sets.get("ReaderReadAHead", None)

	@ReaderReadAHead.setter
	def ReaderReadAHead(self, val):
		self.sets["ReaderReadAHead"] = val

	@property
	def UseDisk(self):
		# bool
		return self.sets.get("UseDisk", None)

	@UseDisk.setter
	def UseDisk(self, val):
		self.sets["UseDisk"] = val

	@property
	def TorrentsSavePath(self):
		# string
		return self.sets.get("TorrentsSavePath", None)

	@TorrentsSavePath.setter
	def TorrentsSavePath(self, val):
		self.sets["TorrentsSavePath"] = val

	@property
	def RemoveCacheOnDrop(self):
		# bool
		return self.sets.get("RemoveCacheOnDrop", None)

	@RemoveCacheOnDrop.setter
	def RemoveCacheOnDrop(self, val):
		self.sets["RemoveCacheOnDrop"] = val

	@property
	def ForceEncrypt(self):
		# bool
		return self.sets.get("ForceEncrypt", None)

	@ForceEncrypt.setter
	def ForceEncrypt(self, val):
		self.sets["ForceEncrypt"] = val

	@property
	def RetrackersMode(self):
		# int  // 0 - don`t add, 1 - add retrackers (def), 2 - remove retrackers 3 - replace retrackers
		return self.sets.get("RetrackersMode", None)

	@RetrackersMode.setter
	def RetrackersMode(self, val):
		self.sets["RetrackersMode"] = val

	@property
	def TorrentDisconnectTimeout(self):
		# int  // in seconds
		return self.sets.get("TorrentDisconnectTimeout", )

	@TorrentDisconnectTimeout.setter
	def TorrentDisconnectTimeout(self, val):
		self.sets["TorrentDisconnectTimeout"] = val

	@property
	def EnableDebug(self):
		# bool // print logs
		return self.sets.get("EnableDebug", None)

	@EnableDebug.setter
	def EnableDebug(self, val):
		self.sets["EnableDebug"] = val

	@property
	def EnableIPv6(self):
		# bool
		return self.sets.get("EnableIPv6", None)

	@EnableIPv6.setter
	def EnableIPv6(self, val):
		self.sets["EnableIPv6"] = val

	@property
	def DisableTCP(self):
		# bool
		return self.sets.get("DisableTCP", None)

	@DisableTCP.setter
	def DisableTCP(self, val):
		self.sets["DisableTCP"] = val

	@property
	def DisableUTP(self):
		# bool
		return self.sets.get("DisableUTP", None)

	@DisableUTP.setter
	def DisableUTP(self, val):
		self.sets["DisableUTP"] = val

	@property
	def DisableUPNP(self):
		# bool
		return self.sets.get("DisableUPNP", None)

	@DisableUPNP.setter
	def DisableUPNP(self, val):
		self.sets["DisableUPNP"] = val

	@property
	def DisableDHT(self):
		# bool
		return self.sets.get("DisableDHT", None)

	@DisableDHT.setter
	def DisableDHT(self, val):
		self.sets["DisableDHT"] = val

	@property
	def DisablePEX(self):
		# bool
		return self.sets.get("DisablePEX", None)

	@DisablePEX.setter
	def DisablePEX(self, val):
		self.sets["DisablePEX"] = val

	@property
	def DisableUpload(self):
		# bool
		return self.sets.get("DisableUpload", None)

	@DisableUpload.setter
	def DisableUpload(self, val):
		self.sets["DisableUpload"] = val

	@property
	def DownloadRateLimit(self):
		# int // in kb, 0 - inf
		return self.sets.get("DownloadRateLimit", None)

	@DownloadRateLimit.setter
	def DownloadRateLimit(self, val):
		self.sets["DownloadRateLimit"] = val

	@property
	def UploadRateLimit(self):
		# int // in kb, 0 - inf
		return self.sets.get("UploadRateLimit", None)

	@UploadRateLimit.setter
	def UploadRateLimit(self, val):
		self.sets["UploadRateLimit"] = val

	@property
	def ConnectionsLimit(self):
		# int
		return self.sets.get("ConnectionsLimit", None)

	@ConnectionsLimit.setter
	def ConnectionsLimit(self, val):
		self.sets["ConnectionsLimit"] = val

	@property
	def DhtConnectionLimit(self):
		# int
		return self.sets.get("DhtConnectionLimit", None)

	@DhtConnectionLimit.setter
	def DhtConnectionLimit(self, val):
		self.sets["DhtConnectionLimit"] = val

	@property
	def PeersListenPort(self):
		# int
		return self.sets.get("PeersListenPort", None)

	@PeersListenPort.setter
	def PeersListenPort(self, val):
		self.sets["PeersListenPort"] = val

	@property
	def Strategy(self):
		# int // 0 - RequestStrategyDuplicateRequestTimeout, 1 - RequestStrategyFuzzing, 2 - RequestStrategyFastest
		return self.sets.get("Strategy", None)

	@Strategy.setter
	def Strategy(self, val):
		self.sets["Strategy"] = val
