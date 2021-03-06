#!/bin/bash
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

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
find $DIR/../src/ | grep .py$ > $DIR/localeinput.dat
xgettext -p $DIR -d skarphed -n -f $DIR/localeinput.dat
rm $DIR/localeinput.dat
mv $DIR/skarphed.po $DIR/skarphed.pot