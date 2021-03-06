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

import pygtk
pygtk.require("2.0")
import gtk

from data.Generic import GenericObjectStoreException
from gui.DefaultEntry import DefaultEntry

from glue.lng import _

class RegisterSchemaPage(gtk.Frame):
    def __init__(self, par, database):
        self.par = par
        gtk.Frame.__init__(self, _("Skarphed Admin :: Register Schema"))

        self.databaseId = database.getLocalId()

        self.table = gtk.Table(4,2,False)
        self.instruction = gtk.Label(_("Please enter Credentials here:"))
        self.name_label = gtk.Label(_("Schema-Name"))
        self.user_label = gtk.Label(_("Schema-User:"))
        self.pass_label = gtk.Label(_("Schema-Password:"))
        self.user_entry = DefaultEntry(default_message=_("user"))
        self.pass_entry = DefaultEntry(default_message=_("password"))
        self.name_entry = DefaultEntry(default_message=_("schema"))
        self.buttonhbox = gtk.HBox()
        self.cancel = gtk.Button(stock=gtk.STOCK_CLOSE)
        self.ok = gtk.Button(stock=gtk.STOCK_OK)
        self.buttonhbox.add(self.cancel)
        self.buttonhbox.add(self.ok)
        
        self.table.attach(self.instruction,0,2,0,1)
        self.table.attach(self.name_label,0,1,1,2)
        self.table.attach(self.name_entry,1,2,1,2)
        self.table.attach(self.user_label,0,1,2,3)
        self.table.attach(self.user_entry,1,2,2,3)
        self.table.attach(self.pass_label,0,1,3,4)
        self.table.attach(self.pass_entry,1,2,3,4)
        self.table.attach(self.buttonhbox,1,2,4,5)

        self.ok.connect("clicked", self.cb_Ok)
        self.cancel.connect("clicked", self.cb_Cancel)
        self.connect("delete-event", self.cb_Cancel)

        database.addCallback(self.render)

        self.table.set_border_width(10)
        self.add(self.table)
        self.getApplication().getMainWindow().openDialogPane(self)


    def cb_Ok(self,widget=None,data=None):
        database = self.getApplication().getLocalObjectById(self.databaseId)
        database.registerSchema(self.name_entry.get_text(),
                                self.user_entry.get_text(), 
                                self.pass_entry.get_text())
        self.getApplication().getMainWindow().closeDialogPane()

    def cb_Cancel(self, widget=None, data=None):
        self.getApplication().getMainWindow().closeDialogPane()

    def render(self):
        try:
            self.getApplication().getLocalObjectById(self.databaseId)
        except GenericObjectStoreException:
            self.getApplication().getMainWindow().closeDialogPane()

    def getPar(self):
        return self.par

    def getApplication(self):
        return self.par.getApplication()
