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

class User(GenericSkarphedObject):
    def __init__(self,parent, data = {}):
        GenericSkarphedObject.__init__(self)
        self.par = parent
        self.data = data
        self.roledata = None
        self.permissiondata = None
        self.updated()
    
    def getName(self):
        if self.data.has_key('name'):
            return self.data['name']
        else:
            return "Unknown User"
    
    def refresh(self,data):
        self.data = data
        self.updated()
    
    def getId(self):
        if self.data.has_key('id'):
            return self.data['id']
        else:
            return None
        
    def fetchRightsDataCallback(self,data):
        self.permissiondata = data
        self.updated()
    
    def fetchRightsData(self):
        self.getApplication().doRPCCall(self.getUsers().getSkarphed(),
                                      self.fetchRightsDataCallback,
                                      "getRightsForUserPage",
                                      [self.getId()]
                                      )
    
    def fetchRoleDataCallback(self,data):
        self.roledata = data
        self.updated()
    
    def fetchRoleData(self):
        self.getApplication().doRPCCall(self.getUsers().getSkarphed(),
                                      self.fetchRoleDataCallback,
                                      "getRolesForUserPage",
                                      [self.getName()]
                                      )
    
    def assignRoleCallback(self,data):
        self.fetchRightsData()
        self.fetchRoleData()
    
    def assignRole(self,role):
        self.getApplication().doRPCCall(self.getUsers().getSkarphed(),
                                      self.assignRoleCallback,
                                      "assignRoleToUser",
                                      [self.getName(),role]
                                      )
    
    def removeRoleCallback(self,data):
        self.fetchRightsData()
        self.fetchRoleData()
    
    def removeRole(self,role):
        self.getApplication().doRPCCall(self.getUsers().getSkarphed(),
                                      self.removeRoleCallback,
                                      "revokeRoleFromUser",
                                      [self.getName(),role]
                                      )
    
    def assignPermissionCallback(self,data):
        self.fetchRightsData()
    
    def assignPermission(self,right):
        self.getApplication().doRPCCall(self.getUsers().getSkarphed(),
                                      self.assignPermissionCallback,
                                      "grantRightToUser",
                                      [self.getId(),right]
                                      )
    
    def removePermissionCallback(self,data):
        self.fetchRightsData()
    
    def removePermission(self,role):
        self.getApplication().doRPCCall(self.getUsers().getSkarphed(),
                                      self.removePermissionCallback,
                                      "revokeRightFromUser",
                                      [self.getId(),role]
                                      )
    def deleteCallback(self,json):
        self.destroy()
    
    def delete(self):
        self.getApplication().doRPCCall(self.getUsers().getSkarphed(),
                                      self.deleteCallback,
                                      "deleteUser",
                                      [self.getId()]
                                      )

    def alterPasswordCallback(self, json):
        return True
    
    def alterPassword(self, new_password, old_password=None):
        self.getApplication().doRPCCall(self.getUsers().getSkarphed(),
                                        self.alterPasswordCallback,
                                        "alterPassword",
                                        [self.getId(), new_password, old_password])

    def getPar(self):
        return self.par
    
    def getUsers(self):
        return self.getPar()