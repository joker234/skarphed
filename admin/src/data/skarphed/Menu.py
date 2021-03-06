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

class Menu(GenericSkarphedObject):
    def __init__(self,par, data = {}):
        GenericSkarphedObject.__init__(self)
        self.par = par
        self.data = data
        self.updated()
        self.loadMenuItems()
        
    def getName(self):
        if self.data.has_key('name'):
            return self.data['name']
        else:
            return "Unknown Menu"
    
    def update(self,data):
        self.data = data
        self.updated()
        
    def getId(self):
        if self.data.has_key('id'):
            return self.data['id']
        else:
            return None    
    
    def getMenuItemById(self,menuItemId):
        for menuItem in self.children:
            if menuItem.getId() == menuItemId:
                return menuItem
        return None
    
    def loadMenuItemsCallback(self,json):
        menuItemIds = [mi.getId() for mi in self.children]
        for menuItem in json:
            if menuItem['id'] not in menuItemIds:
                self.children.append(MenuItem(self,menuItem))
            else:
                self.getMenuItemById(menuItem['id']).update(menuItem)
                menuItemIds.remove(menuItem['id'])
        for mi in self.children:
            if mi.getId() in menuItemIds:
                self.children.remove(mi)
                mi.destroy()
        self.updated()
    
    def loadMenuItems(self):
        self.getApplication().doRPCCall(self.getSite().getSites().getSkarphed(),
                                        self.loadMenuItemsCallback,"getMenuItemsOfMenu",[self.getId()])
        
    def getMenuItemsRecursive(self):
        ret = [c.getLocalId() for c in self.children]
        for menuItem in self.children:
            ret.extend(menuItem.getMenuItemsRecursive())
        return ret
        
    def getMenuItems(self):
        return self.children
    
    def deleteCallback(self,json):
        self.destroy()
        
    def delete(self):
        self.getApplication().doRPCCall(self.getSite().getSites().getSkarphed(),
                                        self.deleteCallback,"deleteMenu",[self.getId()])
    
    def createMenuItemCallback(self,json):
        self.loadMenuItems()
        
    def createMenuItem(self):
        self.getApplication().doRPCCall(self.getSite().getSites().getSkarphed(),
                                        self.createMenuItemCallback,"createMenuItem",[self.getId(),'menu'])
    
    def deleteMenuItemCallback(self,json):
        self.loadMenuItems()
    
    def deleteMenuItem(self,menuItem):
        if menuItem in self.children:
            self.getApplication().doRPCCall(self.getSite().getSites().getSkarphed(),
                                        self.deleteMenuItemCallback,"deleteMenuItem",[menuItem.getId()])
    
    
    def renameCallback(self,json):
        self.getSite().loadMenus()
    
    def rename(self,name):
        self.getApplication().doRPCCall(self.getSite().getSites().getSkarphed(),
                                        self.renameCallback,"renameMenu",[self.getId(),name])
    
    def getPar(self):
        return self.par
    
    def getSite(self):
        return self.getPar()
    
class MenuItem(GenericSkarphedObject):
    def __init__(self,par, data = {}):
        GenericSkarphedObject.__init__(self)
        self.par = par
        self.data = data
        self.actionList = None
        self.updated()
        self.loadActionList()
        self.loadMenuItems()
        
    def getName(self):
        if self.data.has_key('name'):
            return self.data['name']
        else:
            return "Unknown MenuItem"
    
    def update(self,data):
        self.data = data
        self.updated()
        
    def getId(self):
        if self.data.has_key('id'):
            return self.data['id']
        else:
            return None  
    
    def getOrder(self):
        if self.data.has_key('order'):
            return self.data['order']
        else:
            return -1
    
    def getMenuItemById(self,menuItemId):
        for menuItem in self.children:
            if menuItem.getId() == menuItemId:
                return menuItem
        return None
    
    def loadMenuItemsCallback(self,json):
        menuItemIds = [mi.getId() for mi in self.children]
        for menuItem in json:
            if menuItem['id'] not in menuItemIds:
                self.children.append(MenuItem(self,menuItem))
            else:
                self.getMenuItemById(menuItem['id']).update(menuItem)
                menuItemIds.remove(menuItem['id'])
        for mi in self.children:
            if mi.getId() in menuItemIds:
                self.children.remove(mi)
                mi.destroy()
        self.updated()
        self.getMenu().updated()
        
    def loadMenuItems(self):
        self.getApplication().doRPCCall(self.getMenu().getSite().getSites().getSkarphed(),
                                        self.loadMenuItemsCallback,"getMenuItemsOfMenuItem",[self.getId()])
    
    def getMenuItemsRecursive(self):
        ret = [c.getLocalId() for c in self.children]
        for menuItem in self.children:
            ret.extend(menuItem.getMenuItemsRecursive())
        return ret
    
    def orderCallback(self,json):
        self.getPar().loadMenuItems()
    
    def increaseOrder(self):
        self.getApplication().doRPCCall(self.getMenu().getSite().getSites().getSkarphed(),
                                        self.orderCallback,"increaseMenuItemOrder",[self.getId()])
    
    def decreaseOrder(self):
        self.getApplication().doRPCCall(self.getMenu().getSite().getSites().getSkarphed(),
                                        self.orderCallback,"decreaseMenuItemOrder",[self.getId()])
    
    def moveToTop(self):
        self.getApplication().doRPCCall(self.getMenu().getSite().getSites().getSkarphed(),
                                        self.orderCallback,"moveToTopMenuItemOrder",[self.getId()])
    
    def moveToBottom(self):
        self.getApplication().doRPCCall(self.getMenu().getSite().getSites().getSkarphed(),
                                        self.orderCallback,"moveToBottomMenuItemOrder",[self.getId()])
    
    def getMenuItems(self):
        return self.children
    
    def deleteCallback(self, json):
        for child in self.children:
            child.destroy()
        self.getPar().loadMenuItems()
        
    
    def delete(self):
        self.getApplication().doRPCCall(self.getMenu().getSite().getSites().getSkarphed(),
                                        self.deleteCallback,"deleteMenuItem",[self.getId()])

    def createMenuItemCallback(self,json):
        self.loadMenuItems()
        
    
    def createMenuItem(self):
        self.getApplication().doRPCCall(self.getMenu().getSite().getSites().getSkarphed(),
                                        self.createMenuItemCallback,"createMenuItem",[self.getId(),'menuItem'])
    
    def renameCallback(self, json):
        self.getPar().loadMenuItems()

    def rename(self, name):
        self.getApplication().doRPCCall(self.getMenu().getSite().getSites().getSkarphed(),
                                        self.renameCallback,"renameMenuItem",[self.getId(),name])
    
    def getActionList(self):
        return self.actionList
    
    def loadActionListCallback(self,json):
        if self.actionList is None:
            self.actionList = ActionList(self,json)
        else:
            self.actionList.update(json)
        self.updated()
    
    def loadActionList(self):
        self.getApplication().doRPCCall(self.getMenu().getSite().getSites().getSkarphed(),
                                        self.loadActionListCallback,"getActionListForMenuItem",[self.getId()])
    
    def deleteMenuItemCallback(self,json):
        self.loadMenuItems()
    
    def deleteMenuItem(self,menuItem):
        if menuItem in self.children:
            self.getApplication().doRPCCall(self.getMenu().getSite().getSites().getSkarphed(),
                                        self.deleteMenuItemCallback,"deleteMenuItem",[menuItem.getId()])
    
    def getPar(self):
        return self.par

    def getMenu(self):
        if self.getPar().__class__.__name__ == 'Menu':
            return self.getPar()
        else:
            return self.getPar().getMenu()

class Action(GenericSkarphedObject):
    def __init__(self,par, data = {}):
        GenericSkarphedObject.__init__(self)
        self.par = par
        self.data = data
        self.updated()
    
    def update(self,data):
        self.data=data
        self.updated()
    
    def getId(self):
        if self.data.has_key('id'):
            return self.data['id']
        else:
            return None
    
    def getName(self):
        if self.data.has_key('name'):
            return self.data['name']
        else:
            return None
    
    def getOrder(self):
        if self.data.has_key('order'):
            return self.data['order']
        else:
            return None
    
    
    def orderCallback(self,json):
        self.getPar().loadActions()
    
    def increaseOrder(self):
        self.getApplication().doRPCCall(self.getActionList().getMenuItem().getMenu().getSite().getSites().getSkarphed(),
                                        self.orderCallback,"increaseActionOrder",[self.getId()])
    
    def decreaseOrder(self):
        self.getApplication().doRPCCall(self.getActionList().getMenuItem().getMenu().getSite().getSites().getSkarphed(),
                                        self.orderCallback,"decreaseActionOrder",[self.getId()])
    
    def moveToTop(self):
        self.getApplication().doRPCCall(self.getActionList().getMenuItem().getMenu().getSite().getSites().getSkarphed(),
                                        self.orderCallback,"moveToTopActionOrder",[self.getId()])
    
    def moveToBottom(self):
        self.getApplication().doRPCCall(self.getActionList().getMenuItem().getMenu().getSite().getSites().getSkarphed(),
                                        self.orderCallback,"moveToBottomActionOrder",[self.getId()])
    
    
    def setNewTargetCallback(self,json):
        self.getPar().loadActions()
    
    def setUrl(self,url):
        self.getApplication().doRPCCall(self.getActionList().getMenuItem().getMenu().getSite().getSites().getSkarphed(),
                                        self.setNewTargetCallback,"setActionUrl",[self.getId(),url])
    
    def setWidgetSpaceConstellation(self, widgetId, space):
        widget = self.getApplication().getLocalObjectById(widgetId)
        self.getApplication().doRPCCall(self.getActionList().getMenuItem().getMenu().getSite().getSites().getSkarphed(),
                                        self.setNewTargetCallback,"setActionWidgetSpaceConstellation",[self.getId(),widget.getId(),space])
    
    def setView(self,viewId):
        view = self.getApplication().getLocalObjectById(viewId)
        self.getApplication().doRPCCall(self.getActionList().getMenuItem().getMenu().getSite().getSites().getSkarphed(),
                                        self.setNewTargetCallback,"setActionView",[self.getId(),view.getId()])
    

    def getSpaceId(self):
        return self.data['space']
    
    def getWidgetId(self):
        return self.data['widgetId']

    def getWidget(self):
        return self.getActionList().getMenuItem().getMenu().getSite().getSkarphed().getModules().getWidgetById(self.getWidgetId())
    
    def getViewId(self):
        return self.data['viewId']

    def getView(self):
        return self.getActionList().getMenuItem().getMenu().getSite().getSkarphed().getViews().getViewById(self.getViewId())

    def getPar(self):
        return self.par
    
    def getActionList(self):
        return self.getPar()
    

class ActionList(GenericSkarphedObject):
    def __init__(self,par, data = {}):
        GenericSkarphedObject.__init__(self)
        self.par = par
        self.data = data
        self.updated()
        self.loadActions()
    
    def update(self,data):
        self.data = data
        self.updated()
    
    def getActions(self):
        return self.children
    
    def getActionById(self, obj_id):
        for action in self.children:
            if action.getId() == obj_id:
                return action
        return None
    
    def loadActionsCallback(self,json):
        actionIds = [a.getId() for a in self.children]
        for action in json:
            if action['id'] not in actionIds:
                self.children.append(Action(self,action))
            else:
                self.getActionById(action['id']).update(action)
        result_action_ids = [a['id'] for a in json]
        for action in self.children:
            if action.getId() not in result_action_ids:
                self.removeChild(action)
        self.updated()
            
    
    def loadActions(self):
        self.getApplication().doRPCCall(self.getMenuItem().getMenu().getSite().getSites().getSkarphed(),
                                        self.loadActionsCallback,"getActionsOfActionList",[self.getId()])
    
    def getId(self):
        if self.data.has_key('id'):
            return self.data['id']
        else:
            return None
    
    def addActionCallback(self,json):
        self.loadActions()
    
    def addAction(self):
        self.getApplication().doRPCCall(self.getMenuItem().getMenu().getSite().getSites().getSkarphed(),
                                        self.addActionCallback,"addActionToActionList",[self.getId()])
    
    def deleteActionCallback(self,json):
        self.loadActions()
        
    
    def deleteAction(self,action):
        self.getApplication().doRPCCall(self.getMenuItem().getMenu().getSite().getSites().getSkarphed(),
                                        self.deleteActionCallback,"deleteAction",[action.getId()])
        self.children.remove(action)
        action.destroy()
    
    def getPar(self):
        return self.par
    
    def getMenuItem(self):
        return self.getPar()