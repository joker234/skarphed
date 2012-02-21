#!/usr/bin/python
#-*- coding:utf-8 -*-

import pygtk
pygtk.require("2.0")
import gtk

from GenericObject import GenericObjectPage
from GenericObject import PageFrame
from GenericObject import FrameLabel
import gui.IconStock

class RolePage(GenericObjectPage):
    def __init__(self,parent,object):
        GenericObjectPage.__init__(self,parent,object)
        self.role = object
        
        self.role.fetchPermissions()
        
        self.headline = gtk.Label()
        self.pack_start(self.headline,False)
        
        self.info = PageFrame(self,"Information", gui.IconStock.ROLE)
        self.infobox = gtk.VBox()
        self.info.add(self.infobox)
        self.pack_start(self.info,False)
        
        self.perm = PageFrame(self,"Permissions", gui.IconStock.PERMISSION)
        self.permbox = gtk.Table(1,2,False)
        self.permbox.set_row_spacings(10)
        self.permbox.set_col_spacings(10)
        self.permbox.set_border_width(10)
        
        self.perm_permlabel = FrameLabel(self,"Please choose the Permissions you want to assign to the user here:", gui.IconStock.PERMISSION)
        
        self.perm_permlistview = gtk.TreeView()
        self.perm_permlist = gtk.ListStore(int, str,str)
        self.perm_permlistview.set_model(self.perm_permlist)
        self.perm_permlist_col_checkbox = gtk.TreeViewColumn('')
        self.perm_permlist_col_identifier = gtk.TreeViewColumn('Permission Identifier')
        self.perm_permlist_col_name = gtk.TreeViewColumn('Permission Name')
        self.perm_permlistview.append_column(self.perm_permlist_col_checkbox)
        self.perm_permlistview.append_column(self.perm_permlist_col_identifier)
        self.perm_permlistview.append_column(self.perm_permlist_col_name)
        self.perm_permlist_renderer_checkbox= gtk.CellRendererToggle()
        self.perm_permlist_renderer_identifier = gtk.CellRendererText()
        self.perm_permlist_renderer_name = gtk.CellRendererText()
        
        self.perm_permlist_col_checkbox.pack_start(self.perm_permlist_renderer_checkbox)
        self.perm_permlist_col_identifier.pack_start(self.perm_permlist_renderer_identifier)
        self.perm_permlist_col_name.pack_start(self.perm_permlist_renderer_name)
        self.perm_permlist_col_checkbox.add_attribute(self.perm_permlist_renderer_checkbox,'active',0)
        self.perm_permlist_col_identifier.add_attribute(self.perm_permlist_renderer_identifier,'text',1)
        self.perm_permlist_col_name.add_attribute(self.perm_permlist_renderer_name,'text',2)
        self.perm_permlist_renderer_checkbox.set_activatable(True)
        self.perm_permlist_renderer_checkbox.connect("toggled",self.toggledRight)
        
        self.permbox.attach(self.perm_permlabel,0,1,0,1)
        self.permbox.attach(self.perm_permlistview,0,1,1,2)
        
        self.perm.add(self.permbox)
        self.pack_start(self.perm,False)
        
        self.show_all()
        
        self.render()
        object.addCallback(self.render)
    
    def render(self):
        self.headline.set_markup("<b>Edit Role: "+self.role.getName()+"</b>")
        
        if self.role.permissiondata is not None:
            self.perm_permlist.clear()
            for permission in self.role.permissiondata:
                self.perm_permlist.append((int(permission['granted']),str(permission['right']),''))
        
    
    def toggledRight(self,renderer = None, path = None):
        iter = self.perm_permlist.get_iter(path)
        perm = self.perm_permlist.get_value(iter,1)
        val = 1-self.perm_permlist.get_value(iter,0)
        print val
        if val == 1:
            self.role.assignPermission(perm)
        else:
            self.role.removePermission(perm)  
        