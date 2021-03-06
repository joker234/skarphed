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

from ViewPasswordButton import ViewPasswordButton
from data.Server import DNSError
from gui.MessagePage import MessagePage

from gui.DefaultEntry import DefaultEntry

from glue.lng import _

class InstancePage(gtk.Frame):
    def __init__(self,parent, server=None, instance = None):
        gtk.Frame.__init__(self)
        self.par = parent
        self.serverId = None
        if server is not None:
            self.serverId = server.getLocalId()
        self.instanceId = None
        if instance is not None:
            self.instanceId = instance.getLocalId()
        self.instanceTypes = self.getApplication().getInstanceTypes()
        
        self.set_label(_("Skarphed Admin :: Configure Instance"))
        self.vbox = gtk.VBox()
        self.label = gtk.Label(_("Please configure the Instance"))
        self.vspace = gtk.Label("")
        self.vbox.pack_start(self.label,False)
        self.vbox.pack_start(self.vspace,True)
        
        self.table = gtk.Table(2,4,False)
        self.typeLabel = gtk.Label(_("InstanceType:"))
        
        self.typeStore = gtk.ListStore(str)
        self.typeCombo = gtk.ComboBox(self.typeStore)
        self.typeRenderer = gtk.CellRendererText()
        self.typeCombo.pack_start(self.typeRenderer, True)
        self.typeCombo.add_attribute(self.typeRenderer, 'text', 0)  
        for instanceType in self.instanceTypes:
            self.typeStore.append((instanceType.displayName,))
        self.typeCombo.set_active(0)
        self.urlLabel = gtk.Label(_("URL:"))
        self.urlEntry = DefaultEntry(default_message="http://instance.org")
        self.urlEntry.set_text("http://")
        self.userLabel = gtk.Label(_("Username:"))
        self.userEntry = DefaultEntry(default_message=_("username"))
        self.passLabel = gtk.Label(_("Password:"))
        self.passEntry = gtk.Entry()
        self.passEntry.set_visibility(False)
        self.passEntry.set_invisible_char("●")
        self.table.attach(self.typeLabel,0,1,0,1)
        self.table.attach(self.typeCombo,1,2,0,1)
        self.table.attach(self.urlLabel,0,1,1,2)
        self.table.attach(self.urlEntry,1,2,1,2)
        self.table.attach(self.userLabel,0,1,2,3)
        self.table.attach(self.userEntry,1,2,2,3)
        self.table.attach(self.passLabel,0,1,3,4)
        self.table.attach(self.passEntry,1,2,3,4)
        self.vbox.pack_start(self.table,False)
        
        self.buttonBox = gtk.HBox()
        self.ok = gtk.Button(stock=gtk.STOCK_OK)
        self.cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.viewpass = ViewPasswordButton()
        self.viewpass.addEntry(self.passEntry)
        self.space = gtk.Label("")
        self.buttonBox.pack_start(self.space,True)
        self.buttonBox.pack_start(self.viewpass,False)
        self.buttonBox.pack_start(self.cancel,False)
        self.buttonBox.pack_start(self.ok,False)
        self.ok.connect("clicked",self.cb_Ok)
        self.cancel.connect("clicked",self.cb_Cancel)
        self.vbox.pack_start(self.buttonBox,False)
        
        self.add(self.vbox)
        self.getApplication().getMainWindow().openDialogPane(self)
        if instance is not None:
            self.urlEntry.set_sensitive(False)
            self.render()
    
    def render(self):
        try:
            instance = self.getApplication().getLocalObjectById(self.instanceId)
        except GenericObjectStoreException:
            self.getApplication().getMainWindow().closeDialogPane(self)
            return
    
        self.urlEntry.set_text(instance.getUrl())
        self.userEntry.set_text(instance.getUsername())
        self.passEntry.set_text(instance.getPassword())
    
    def getInstanceType(self,text):
        for instanceType in self.instanceTypes:
            if instanceType.displayName == text:
                return instanceType
        return None
    
    def cb_Cancel(self, widget=None, data=None):
        self.getApplication().getMainWindow().closeDialogPane()
    
    def cb_Ok (self, widget=None, data=None):
        def errorMessage(msgId):
            msgs = (_("This URL cannot be resolved"),
                    )
            dia = gtk.MessageDialog(parent=self.getPar().getPar(), flags=0, type=gtk.MESSAGE_WARNING, \
                                  buttons=gtk.BUTTONS_OK, message_format=msgs[msgId])
            dia.run()
            dia.destroy()
        
        instance = None
        if self.instanceId is not None:
            instance = self.getApplication().getLocalObjectById(self.instanceId)
        server = self.getApplication().getLocalObjectById(self.serverId)
        
        if instance is not None:
            instance.setUsername(self.userEntry.get_text())
            instance.setPassword(self.passEntry.get_text())
            instance.establishConnections()
        else:
            url = self.urlEntry.get_text()
            if server is None:
                try:
                    server = self.getApplication().createServerFromInstanceUrl(url)
                except DNSError:
                    errorMessage(0)
                    return
            
            selection = self.typeStore[self.typeCombo.get_active()][0]  
            instanceType = self.getInstanceType(selection)
            
            username = self.userEntry.get_text()
            password = self.passEntry.get_text()
            try:
                if not server.createInstance(instanceType, url, username, password):
                    MessagePage(self, _("This URL resolves to another server. You can't add that here."))
                    return
            except None:
                return
        self.getApplication().getMainWindow().closeDialogPane()

        
    def getPar(self):
        return self.par

    def getApplication(self):
        return self.par.getApplication()
    
