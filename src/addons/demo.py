#!/usr/bin/python
# -*- coding: UTF-8 -*


import os
import six
from six.moves.urllib.parse import quote, unquote
from bs4 import BeautifulSoup
from ..Debug import logger
from ..TInfos import TInfos
from ..WebRequests import WebRequests


class demo(WebRequests, object):
	def __init__(self, url_prefix, max_entries=10):
		WebRequests.__init__(self)
		# self.rts_search_url = "/search/{item}/{page}/"
		self.rts_search_url = ""
		self.url_prefix = url_prefix
		self.max_entries = max_entries
		self.rts_search_page = 0
		self.t_info_dict = {"url": "", "date": '', "name": "", "size": "", "seeders": "", "leechers": "", "magnet": '', "file_url": "", "engine": os.path.splitext(os.path.basename(__file__))[0]}
		self.rts_infos = None
		self.rts_search_query = ""

	@property
	def search_url(self):
		url = (self.url_prefix + self.rts_search_url).format(
			item=self.rts_search_query,
			page=self.rts_search_page,
		)
		logger.debug("search_url: %s", url)
		return url

	@property
	def query(self):
		return unquote(self.rts_search_query)

	@query.setter
	def query(self, val):
		self.rts_search_query = quote(val)

	def parse_page_urls(self, html):
		logger.info("...")
		retval = []
		soup = BeautifulSoup(html, "html.parser")
		divs = soup.find_all("div", {"class": "pagination"})
		for div in divs:
			anchors = div.find_all("a", href=True)
			for anchor in anchors:
				logger.debug("anchor: %s", anchor)
				href = anchor["href"]
				retval.append(six.ensure_str(self.url_prefix + href))
		logger.debug("retval: %s", retval)
		return retval

	def parse_torrs_info(self, html):
		logger.info("...")
		demo_active = True
		if not demo_active:
			# this needs to be adapted for your specific directory
			soup = BeautifulSoup(html, "html.parser")
			table = soup.find("table", {"class": "table"})
			logger.debug("%s", table)
			if table:
				trs = table.find_all("tr")
				for i, tr in enumerate(trs):
					logger.debug("%s ===>\n", i)
					logger.debug("%s", tr)
					info = self.t_info_dict.copy()
					cols = tr.find_all("td")
					for j, col in enumerate(cols):
						logger.debug("%s ---> %s", j, col)
						logger.debug("%s", col)
						# fill info fields here...
					logger.debug("info: %s", info)
					if info["url"]:
						self.parse_torrs_movie(info["url"], info)
						self.rts_infos.append(info)
		else:  # demo data
			info = self.t_info_dict.copy()
			info["url"] = ""
			info["name"] = "Demo Movie"
			info["seeders"] = "88"
			info["leechers"] = "23"
			info["date"] = "1783"
			info["size"] = "2.5 GB"
			self.rts_infos.append(info)

		return self.rts_infos > 0

	def parse_torrs_movie(self, url, info):
		logger.info("url: %s", url)
		html = self.getContent(url)
		magnet = ""
		soup = BeautifulSoup(html, "html.parser")
		links = soup.find_all("a", href=True)
		for link in links:
			href = link["href"]
			if href.startswith("magnet"):
				magnet = six.ensure_str(href)
				logger.debug("magnet: %s", magnet)
				break
		info["magnet"] = magnet
		logger.debug("info: %s", info)

	def search(self):
		logger.info("...")
		self.rts_infos = TInfos(info=None, search_obj=self)
		logger.debug("search_url: %s", self.search_url)
		html = self.getContent(self.search_url)
		logger.debug("%s", html)
		if html:
			if self.parse_torrs_info(html):
				nexts = self.parse_page_urls(html)
				logger.debug("nexts: %s", nexts)
				for oneurl in nexts:
					html = self.getContent(oneurl)
					if html:
						self.parse_torrs_info(html)
		return len(self.rts_infos) > 0
