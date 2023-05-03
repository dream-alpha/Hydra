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


import os
import time
import subprocess
# from .Debug import logger


def stopVPN():
	open_vpn_stop = subprocess.Popen(['systemctl', 'stop', 'vpn_openvpn.service'])
	open_vpn_stop.wait()
	open_vpn_stop = subprocess.Popen(['killall', 'openvpn'])
	open_vpn_stop.wait()


def startVPN():
	open_vpn_start = subprocess.Popen(['systemctl', 'start', 'vpn_openvpn.service'])
	open_vpn_start.wait()
	time.sleep(1)


def isVPNActive():
	pid = os.popen('pidof openvpn').read()
	# logger.debug("pid: %s", pid)
	return pid
