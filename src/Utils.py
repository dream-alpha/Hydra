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


from . import _
from .torr.torrclient import torrclient


def getStatus():
	if not torrclient.getInstance().is_server_installed():
		status = "TorrServer: " + _("not installed"), "", _("Install server")
	elif torrclient.getInstance().test_connection():
		status = "TorrServer: " + torrclient.getInstance().torr_version, _("Stop"), _("Update server")
	else:
		status = "TorrServer: " + _("down"), _("Start"), _("Update server")
	# logger.debug("status: %s", status)
	return status


def prettySize(size):
	units = [_("B"), _("KB"), _("MB"), _("GB")]
	unit = 0
	while size >= 1024 and unit < len(units):
		size /= 1024.0
		unit += 1
	return _("%0.2f %s") % (size, units[unit])
