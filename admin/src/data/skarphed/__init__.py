#!/usr/bin/python
#-*- coding: utf-8 -*-

###########################################################
# © 2011 Daniel 'grindhold' Brendle and Team
#
# This file is part of Skarphed.
#
# Skarphed is free software: you can redistribute it and/or 
# modify it under the terms of the GNU Affero General Public License 
# as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later 
# version.
#
# Skarphed is distributed in the hope that it will be 
# useful, but WITHOUT ANY WARRANTY; without even the implied 
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public 
# License along with Skarphed. 
# If not, see http://www.gnu.org/licenses/.
###########################################################


from data.Generic import GenericSkarphedObject
from data.Instance import InstanceType
from data.Server import InstallationTarget, Server
from glue.paths import INSTALLER
from os import listdir
from sys import path

o = GenericSkarphedObject()
o.getApplication().registerInstanceType(InstanceType("skarphed","Skarphed"))
o.destroy()

path.append(INSTALLER)
installers = listdir(INSTALLER)
for installer in installers:
    if installer.startswith("_"):
        continue
    try:
        exec "from %s import TARGETNAME, EXTRA_PARAMS, Installer, Destroyer"%installer
    except ImportError:
        print "Failed to load installer: %s"%installer
    else:
        target = InstallationTarget()
        target.setName(TARGETNAME)
        target.setInstaller(Installer)
        target.setDestroyer(Destroyer)
        target.setExtraParams(EXTRA_PARAMS)
        Server.addInstallationTarget(target)



