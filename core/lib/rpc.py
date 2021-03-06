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

from json import JSONDecoder, JSONEncoder
from traceback import print_exc
from StringIO import StringIO
from operation import OperationDaemon
import base64
import os
import subprocess

class Rpc(object):
    def __init__(self, core):
        self._core = core

    def __call__(self, instructions):
        jd = JSONDecoder()
        je = JSONEncoder()
        answer = {}
        try:
            instructions = jd.decode(instructions)
        except ValueError, e:
            answer['error'] = "could not decode instructions"
            self._core.response_body.append(je.encode(answer))
            return

        method = instructions['method']
        params = instructions['params']

        if not hasattr(self,method):
            answer['error'] = "The Rpc-backed does not support this method %s"%method
            self._core.response_body.append(je.encode(answer))
            return
        try:
            exec "res = self.%s(params)"%method
        except Exception, e:
            error = StringIO()
            print_exc(None,error)
            answer['error'] = {}
            answer['error']['traceback'] = error.getvalue()
            answer['error']['class'] = e.__class__.__name__
            answer['error']['message'] = str(e)
            self._core.response_body.append(je.encode(answer))
            return
        else:
            answer['result'] = res
            self._core.response_body.append(je.encode(answer))
    
    # RPC - Method-Implementations____________________________

    def executeModuleMethod(self, params):
        module_id = params[0]
        method_name = params[1]
        parameter = params[2]

        module_manager = self._core.get_module_manager()
        module = module_manager.get_module(module_id)
        exec "res = module.%s(*parameter)"%method_name
        return res

    def getServerInfo(self,params):
        return self._core.get_configuration().get_entry("core.name")

    def getInstanceId(self, params):
        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()

        if session_user.check_permission('skarphed.manageserverdata'):
            config = self._core.get_configuration()
            return config.get_entry('core.instance_id')
        else:
            return None

    def authenticateUser(self,params):
        username = params[0]
        password = params[1]
        
        session_manager = self._core.get_session_manager()

        try:
            user_manager = self._core.get_user_manager()
        except UserException , e:
            session = session_manager.get_current_session()
            if session is not None:
                session.delete()
            return False

        user = user_manager.get_user_by_name(username)

        if user.authenticate(password):
            session = session_manager.create_session(user)
            return user.get_permissions()
        else:
            session = session_manager.get_current_session()
            if session is not None:
                session.delete()
            return False

    def alterPassword(self, params):
        user_id = params[0]
        new_password = params[1]
        old_password = params[2]

        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()

        if user_id == session_user.get_id():
            session_user.alter_password(new_password,old_password)
        else:
            if session_user.check_permission("skarphed.users.alter_password"):
                user_manager = self._core.get_user_manager()
                user = user_manager.get_user_by_id(user_id)
                user.alter_password(new_password,"",True)
        return True

    def getPublicKey(self, params):
        pki_manager = self._core.get_pki_manager()
        return pki_manager.get_public_key(as_string=True)


    def getUsers(self,params):
        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if session_user.check_permission('skarphed.users.view'):
            user_manager = self._core.get_user_manager()
            users = user_manager.get_users_for_admin_interface()
            return users
        return False

    def getRoles(self,params):
        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if session_user.check_permission('skarphed.roles.view'):
            ret = []
            permission_manager = self._core.get_permission_manager()
            for role in permission_manager.get_roles():
                ret.append({"id":role.get_id(), "name": role.get_name()})
            return ret
        return False

    def createUser(self,params):
        username = str(params[0])
        password = str(params[1])

        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if session_user.check_permission('skarphed.users.create'):
            user_manager = self._core.get_user_manager()
            user_manager.create_user(username,password)
        return True

    def grantRightToUser(self,params):
        user_id = int(params[0])
        permission_name  = str(params[1])

        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if session_user.check_permission('skarphed.users.grant_revoke'):
            user_manager = self._core.get_user_manager()
            user = user_manager.get_user_by_id(user_id)
            user.grant_permission(permission_name)
            return True

    def revokeRightFromUser(self,params):
        user_id = int(params[0])
        permission_name = str(params[1])

        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if session_user.check_permission('skarphed.users.grant_revoke'):
            user_manager = self._core.get_user_manager()
            user = user_manager.get_user_by_id(user_id)
            user.revoke_permission(permission_name)
            return True

    def getRightsForUserPage(self,params):
        user_id = int(params[0])
        user_manager = self._core.get_user_manager()
        user = user_manager.get_user_by_id(user_id)
        return user.get_grantable_permissions()

    def grantRightToRole(self,params):
        role_id = int(params[0])
        permission_name = str(params[1])

        permission_manager = self._core.get_permission_manager()
        role = permission_manager.get_role(role_id)
        role.add_permission(permission_name)
        role.store()

    def revokeRightFromRole(self,params):
        role_id = int(params[0])
        permission_name = str(params[1])

        permission_manager = self._core.get_permission_manager()
        role = permission_manager.get_role(role_id)
        role.remove_permission(permission_name)
        role.store()

    def getRightsForRolePage(self,params):
        role_id = int(params[0])

        role = self._core.get_permission_manager().get_role(role_id)
        return role.get_grantable_permissions()

    def createRole(self,params):
        data = params[0]

        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if session_user.check_permission('skarphed.roles.create'):
            permission_manager = self._core.get_permission_manager()
            role = permission_manager.create_role(data)
        return role.get_id()

    def deleteRole(self, params):
        role_id = int(params[0])

        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if session_user.check_permission('skarphed.roles.delete'):
            permission_manager = self._core.get_permission_manager()
            role = permission_manager.get_role(role_id)
            role.delete()

    def getRolesForUserPage(self, params):
        user_name = params[0] # TODO get user by id instead of name
        user_manager = self._core.get_user_manager()
        user = user_manager.get_user_by_name(user_name)
        return user.get_grantable_roles()

    def assignRoleToUser(self, params):
        user_name = params[0] # TODO get user by id instead of name
        role_id = params[1]

        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if session_user.check_permission('skarphed.users.grant_revoke'):
            permission_manager = self._core.get_permission_manager()
            user_manager = self._core.get_user_manager()
            role = permission_manager.get_role(role_id)
            user_manager.get_user_by_name(user_name).assign_role(role)

    def revokeRoleFromUser(self, params):
        user_name = params[0] # TODO get user by id instead of name
        role_id = params[1]

        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if session_user.check_permission('skarphed.users.grant_revoke'):
            permission_manager = self._core.get_permission_manager()
            user_manager = self._core.get_user_manager()
            role = permission_manager.get_role(role_id)
            user_manager.get_user_by_name(user_name).revoke_role(role)

    def getCssPropertySet(self,params):
        try:
            module_id = int(params[0])
        except TypeError:
            module_id = None

        try:
            widget_id = int(params[1])
        except TypeError:
            widget_id = None

        if params[2] is not None:
            session = str(params[2])
        else:
            session = None

        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if session_user.check_permission('skarphed.css.edit'):
            css_manager = self._core.get_css_manager()
            if module_id == None and widget_id == None and session == None:
                css_propertyset = css_manager.get_csspropertyset()
            else:
                css_propertyset = css_manager.get_csspropertyset(module_id,widget_id,session)
            data = css_propertyset.serialize_set()
            return data

    def setCssPropertySet(self, params):
        data = params[0]

        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if session_user.check_permission('skarphed.css.edit'):
            css_manager = self._core.get_css_manager()
            css_propertyset = css_manager.create_csspropertyset_from_serial(data)
            css_propertyset.store()

    def getModules(self,params):
        get_installed_only = bool(params[0])

        module_manager = self._core.get_module_manager()
        repo_state = True
        repo_state = module_manager.get_repository().ping()
        
        modules = module_manager.get_module_info(get_installed_only or not repo_state)
        return {'modules':modules,'repostate':repo_state}

    def getGuiForModule(self, params):
        module_id = int(params[0])

        module_manager = self._core.get_module_manager()
        module = module_manager.get_module(module_id)
        moduleguidata = base64.b64encode(module.get_guidata())
        pki_manager = self._core.get_pki_manager()
        signature = pki_manager.sign(moduleguidata)
        configuration = self._core.get_configuration()

        return {'data':moduleguidata,
                'signature':base64.b64encode(signature),
                'libstring':configuration.get_entry('global.libpath')}

    def setRepository(self, params):
        ip = str(params[0])
        port = int(params[1])

        module_manager = self._core.get_module_manager()
        module_manager.set_repository(ip, port, '(default)')

    def getRepository(self, params):
        module_manager = self._core.get_module_manager()
        repo = module_manager.get_repository()
        return {"id":repo.get_id(), "ip":repo.get_ip(), 
                "port":repo.get_port(), "name": repo.get_name()}

    def updateModule(self, params):
        nr = str(params[0])

        module_manager = self._core.get_module_manager()
        module = module_manager.get_module(nr)
        module_meta = module_manager.get_meta_from_module(module)
        module_manager.invoke_update(module_meta)
        return True

    def updateModules(self, params):
        module_manager = self._core.get_module_manager()
        module_manager.updateModules()
        return 0

    def uninstallModule(self, params):
        module_meta = params[0]

        module_manager = self._core.get_module_manager()
        module_manager.invoke_uninstall(module_meta)
        return 0

    def installModule(self, params):
        module_meta = params[0]

        module_manager = self._core.get_module_manager()
        module_manager.invoke_install(module_meta)
        return 0        

    def dropOperation(self, params):
        operation_id = int(params[0])

        operation_manager = self._core.get_operation_manager()
        operation_manager.drop_operation(operation_id)

    def retryOperation(self, params):
        operation_id = int(params[0])

        operation_manager = self._core.get_operation_manager()
        operation_manager.retry_operation(operation_id)

    def cancelOperation(self, params):
        operation_id = int(params[0])

        operation_manager = self._core.get_operation_manager()
        operation_manager.cancel_operation(operation_id)

    def deleteUser(self, params):
        user_id = int(params[0])

        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if session_user.check_permission('skarphed.users.delete'):
            user_manager = self._core.get_user_manager()
            user = user_manager.get_user_by_id(user_id)
            user.delete()

    def getOperations(self, params):
        operationtypes = None
        if len(params) == 1:
            operationtypes = params[0]

        operation_manager = self._core.get_operation_manager()
        operations = operation_manager.get_current_operations_for_gui(operationtypes)

        return operations

    def getSites(self, params):
        page_manager = self._core.get_page_manager()

        pages = page_manager.get_pages()
        ret = []
        for page in pages:
            spaces = page.get_space_names()
            boxes = page.get_box_info()
            ret.append({
                    'id':page.get_id(),
                    'name':page.get_name(),
                    'description':page.get_description(),
                    'spaces':spaces,
                    'boxes':boxes
                })
        return ret

    def getSite(self, params):
        page_id = int(params[0])
        
        page_manager = self._core.get_page_manager()
        page = page_manager.get_page(page_id)
        spaces = page.get_space_names()
        boxes = page.get_box_info()
        ret = {
            'id':page.get_id(),
            'name':page.get_name(),
            'description':page.get_description(),
            'spaces':spaces,
            'boxes':boxes
        }
        return ret

    def assignWidgetToSpace(self,params):
        view_id = int(params[0])
        space_id = int(params[1])
        widget_id = int(params[2])

        view_manager = self._core.get_view_manager()
        view = view_manager.get_from_id(view_id)
        view.place_widget_in_space(space_id, widget_id)
        view.store()

    def removeWidgetFromSpace(self, params):
        view_id = int(params[0])
        space_id = int(params[1])

        view_manager = self._core.get_view_manager()
        view = view_manager.get_from_id(view_id)
        view.remove_widget_from_space(space_id)
        view.store()

    def getCurrentTemplate(self, params):
        template_manager = self._core.get_template_manager()

        if template_manager.is_template_installed():
            current_template = template_manager.get_current_template()
            return {'name': current_template.get_name(),
                    'description': current_template.get_description(),
                    'author': current_template.get_author()}
        else:
            return {'name': '(No Template)',
                    'description': '(Currently no Template Installed)',
                    'author': '(No Author)',}

    def installTemplate(self, params):
        templatedata = base64.b64decode(params[0])

        #TODO check for permission

        template_manager = self._core.get_template_manager()
        errorlog = template_manager.install_from_data(templatedata)
        return errorlog

    def installTemplateFromRepo(self, params):
        repo_template_id = int(params[0])
        template_manager = self._core.get_template_manager()
        errorlog = template_manager.install_from_repo(repo_template_id)
        return errorlog

    def refreshAvailableTemplates(self, params):
        template_manager = self._core.get_template_manager()
        templates = template_manager.fetch_templates_for_gui()
        ret = [{
                'id':t['id'],
                'name':t['name'],
                'description':t['description'],
                'author':t['author']
              } for t in templates]
        return ret

    def createWidget(self,params):
        module_id = int(params[0])
        new_widget_name = str(params[1])

        module_manager = self._core.get_module_manager()
        module = module_manager.get_module(module_id)
        module.create_widget(new_widget_name)
        return

    def deleteWidget(self, params):
        widget_id = int(params[0])

        module_manager = self._core.get_module_manager()
        widget = module_manager.get_widget(widget_id)
        widget.delete()
        return

    def getWidgetsOfModule(self, params):
        module_id = int(params[0])

        module_manager = self._core.get_module_manager()
        module = module_manager.get_module(module_id)
        widgets = module.get_widgets()

        return [{'id':widget.get_id(), 'name':widget.get_name(), 'gviews':widget.is_generating_views(), 'baseview':widget.get_baseview_id(), 'basespace':widget.get_baseview_space_id()} for widget in widgets]

    def getMenusOfSite(self,params):
        page_id = int(params[0])

        page_manager = self._core.get_page_manager()
        page = page_manager.get_page(page_id)
        menus = page.get_menus()
        ret = []
        for menu in menus:
            ret.append({
                    'id':menu.get_id(),
                    'name':menu.get_name()
                })
        return ret

    def getMenuItemsOfMenu(self, params):
        menu_id = int(params[0])

        action_manager = self._core.get_action_manager()
        menu_items = action_manager.get_menu_by_id(menu_id).get_menu_items()

        ret = []
        for menu_item in menu_items:
            ret.append({"name":  menu_item.get_name(),
                        "id":    menu_item.get_id(),
                        "order": menu_item.get_order()})
        return ret

    def getMenuItemsOfMenuItem(self, params):
        menu_item_id = int(params[0])

        action_manager = self._core.get_action_manager()
        menu_items = action_manager.get_menu_item_by_id(menu_item_id).get_menu_items()

        ret = []
        for menu_item in menu_items:
            ret.append({"name":  menu_item.get_name(),
                        "id":    menu_item.get_id(),
                        "order": menu_item.get_order()})
        return ret

    def increaseMenuItemOrder(self, params):
        menu_item_id = int(params[0])

        action_manager = self._core.get_action_manager()
        menu_item = action_manager.get_menu_item_by_id(menu_item_id)
        menu_item.increase_order()
        return 0

    def decreaseMenuItemOrder(self, params):
        menu_item_id = int(params[0])

        action_manager = self._core.get_action_manager()
        menu_item = action_manager.get_menu_item_by_id(menu_item_id)
        menu_item.decrease_order()
        return 0

    def moveToBottomMenuItemOrder(self, params):
        menu_item_id = int(params[0])

        action_manager = self._core.get_action_manager()
        menu_item = action_manager.get_menu_item_by_id(menu_item_id)
        menu_item.move_to_bottom_order()
        return 0

    def moveToTopMenuItemOrder(self, params):
        menu_item_id = int(params[0])

        action_manager = self._core.get_action_manager()
        menu_item = action_manager.get_menu_item_by_id(menu_item_id)
        menu_item.move_to_top_order()
        return 0

    def createMenuForSite(self, params):
        page_id = int(params[0])

        page_manager = self._core.get_page_manager()
        page = page_manager.get_page(page_id)

        action_manager = self._core.get_action_manager()
        action_manager.create_menu(page)

    def deleteMenu(self, params):
        menu_id = int(params[0])

        action_manager = self._core.get_action_manager()
        menu = action_manager.get_menu_by_id(menu_id)
        menu.delete()

    def createMenuItem(self, params):
        parent_id = int(params[0])
        parent_type = str(params[1])

        if parent_type == "menu":
            action_manager = self._core.get_action_manager()
            menu = action_manager.get_menu_by_id(parent_id)
            action_manager.create_menu_item(menu)
            return 0
        elif parent_type == "menuItem":
            action_manager = self._core.get_action_manager()
            menu_item = action_manager.get_menu_item_by_id(parent_id)
            action_manager.create_menu_item(None,menu_item)
            return 0
        else:
            return 1

    def deleteMenuItem(self, params):
        menu_item_id = int(params[0])

        action_manager = self._core.get_action_manager()
        menu_item = action_manager.get_menu_item_by_id(menu_item_id)
        menu_item.delete()
        return 0

    def renameMenuItem(self, params):
        menu_item_id = int(params[0])
        new_name = str(params[1])

        action_manager = self._core.get_action_manager()
        menu_item = action_manager.get_menu_item_by_id(menu_item_id)
        menu_item.set_name(new_name)
        return 0

    def getActionsOfActionList(self, params):
        action_list_id = int(params[0])

        action_manager = self._core.get_action_manager()
        action_list = action_manager.get_action_list_by_id(action_list_id)
        actions = action_list.get_actions()

        ret = []
        for action in actions:
            ret.append({"id":action.get_id(),
                        "name":action.get_name(),
                        "url":action.get_url(),
                        "widgetId":action.get_widget_id(),
                        "space":action.get_space(),
                        "viewId":action.get_view_id(),
                        "order":action.get_order(),
                        "type":action.get_type()})
        return ret

    def addActionToActionList(self, params):
        action_list_id = int(params[0])

        action_manager = self._core.get_action_manager()
        action_list = action_manager.get_action_list_by_id(action_list_id)
        action_manager.create_action(action_list, None, "")
        return 0

    def deleteAction(self, params):
        action_id = int(params[0])

        action_manager = self._core.get_action_manager()
        action = action_manager.get_action_by_id(action_id)
        action.delete()
        return 0

    def increaseActionOrder(self, params):
        action_id = int(params[0])

        action_manager = self._core.get_action_manager()
        action = action_manager.get_action_by_id(action_id)
        action.increase_order()
        return 0

    def decreaseActionOrder(self, params):
        action_id = int(params[0])

        action_manager = self._core.get_action_manager()
        action = action_manager.get_action_by_id(action_id)
        action.decrease_order()
        return 0

    def moveToTopActionOrder(self, params):
        action_id = int(params[0])

        action_manager = self._core.get_action_manager()
        action = action_manager.get_action_by_id(action_id)
        action.move_to_top_order()
        return 0

    def moveToBottomActionOrder(self, params):
        action_id = int(params[0])

        action_manager = self._core.get_action_manager()
        action = action_manager.get_action_by_id(action_id)
        action.move_to_bottom_order()
        return 0

    def getActionListForMenuItem(self, params):
        menu_item_id = int(params[0])

        action_manager = self._core.get_action_manager()
        menu_item = action_manager.get_menu_item_by_id(menu_item_id)
        action_list = menu_item.get_action_list()
        return {"id":action_list.get_id()}

    def setActionUrl(self, params):
        action_id = int(params[0])
        url = str(params[1])

        action_manager = self._core.get_action_manager()
        action = action_manager.get_action_by_id(action_id)
        action.set_url(url)
        return 0

    def setActionWidgetSpaceConstellation(self, params):
        action_id = int(params[0])
        widget_id = int(params[1])
        space = int(params[2])

        action_manager = self._core.get_action_manager()
        action = action_manager.get_action_by_id(action_id)
        action.set_widget_space_constellation(widget_id, space)
        return 0

    def setActionView(self, params):
        action_id = int(params[0])
        view_id = int(params[1])

        action_manager = self._core.get_action_manager()
        action = action_manager.get_action_by_id(action_id)
        action.set_view_id(view_id)
        return 0

    def renameMenu(self, params):
        menu_id = int(params[0])
        new_name = str(params[1])

        action_manager = self._core.get_action_manager()
        menu = action_manager.get_menu_by_id(menu_id)
        menu.set_name(new_name)
        return 0

    def startOperationDaemon(self,params):
        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if not session_user.check_permission("skarphed.manageserverdata"):
            return False

        configuration = self._core.get_configuration()
        os.system("python "+configuration.get_entry("core.webpath")+\
                  "/operation_daemon.py start "+ configuration.get_entry("core.instance_id"))

    def stopOperationDaemon(self,params):
        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if not session_user.check_permission("skarphed.manageserverdata"):
            return False

        configuration = self._core.get_configuration()
        os.system("python "+configuration.get_entry("core.webpath")+\
                  "/operation_daemon.py stop "+ configuration.get_entry("core.instance_id"))

    def restartOperationDaemon(self,params):
        session_manager = self._core.get_session_manager()
        session_user = session_manager.get_current_session_user()
        if not session_user.check_permission("skarphed.manageserverdata"):
            return False

        configuration = self._core.get_configuration()
        os.system("python "+configuration.get_entry("core.webpath")+\
                  "/operation_daemon.py restart "+ configuration.get_entry("core.instance_id"))

    def getOperationDaemonStatus(self,params):
        configuration = self._core.get_configuration()
        res = os.system("python "+configuration.get_entry("core.webpath")+\
                  "/operation_daemon.py status "+ configuration.get_entry("core.instance_id"))

        if res == 0:
            running = True
        else:
            running = False
        return running

    def getViews(self, params):
        view_manager = self._core.get_view_manager()
        viewlist = view_manager.get_viewlist()
        return viewlist
    
    def getView(self, params):
        view_id = int(params[0])

        view_manager = self._core.get_view_manager()
        view = view_manager.get_from_id(view_id)
        ret = {
            'id' : view.get_id(),
            'name' : view.get_name(),
            'site' : view.get_page(),
            'default' : view.get_default(),
            'space_widget_mapping' : view.get_space_widget_mapping(),
            'box_mapping': view.get_box_mapping(),
            'widget_param_mapping' : view.get_widget_param_mapping()
        }
        return ret

    def setSpaceWidgetMapping(self, params):
        view_id = int(params[0])
        mapping = dict(params[1])

        view_manager = self._core.get_view_manager()
        view = view_manager.get_from_id(view_id)
        view.set_space_widget_mapping(mapping)
        view.store()
        return True

    def setBoxMapping(self, params):
        view_id = int(params[0])
        mapping = dict(params[1])

        view_manager = self._core.get_view_manager()
        view = view_manager.get_from_id(view_id)
        view.set_box_mapping(mapping)
        view.store()
        return True

    def setWidgetParamMapping(self, params):
        view_id = int(params[0])
        widget_id = int(params[1])
        mapping = int(params[2])

        view_manager = self._core.get_view_manager()
        view = view_manager.get_from_id(view_id)
        view.set_params_for_widget(widget_id, mapping)
        view.store()

    def uploadBinary(self, params):
        data = base64.b64decode(params[0])
        filename = str(params[1])

        binary_manager = self._core.get_binary_manager()
        #TODO: Care about mimetype recognition
        binary = binary_manager.create(data, "benis/unknown", filename)
        binary.store()
        return binary.get_id()

    def setMaintenanceMode(self, params):
        state = bool(params[0])

        session_user = self._core.get_session_manager().get_current_session_user()
        if not session_user.check_permission('skarphed.manageserverdata'):
            return False

        if state:
            self._core.activate_maintenance_mode()
        else:
            self._core.deactivate_maintenance_mode()

        return True

    def getMaintenanceMode(self, params):
        return self._core.is_maintenance_mode()

    def setRendermode(self,params):
        mode = str(params[0])

        session_user = self._core.get_session_manager().get_current_session_user()
        if not session_user.check_permission('skarphed.manageserverdata'):
            return False

        return self._core.set_rendermode(mode)

    def getRendermode(self,params):
        return self._core.get_rendermode()

    def widgetActivateViewGeneration(self, params):
        widget_id = int(params[0])
        view_id = int(params[1])
        space_id = int(params[2])

        module_manager = self._core.get_module_manager()
        view_manager = self._core.get_view_manager()
        view = view_manager.get_from_id(view_id)
        widget = module_manager.get_widget(widget_id)
        widget.activate_viewgeneration(view, space_id)
        return

    def widgetDeactivateViewGeneration(self, params):
        widget_id = int(params[0])

        module_manager = self._core.get_module_manager()
        widget = module_manager.get_widget(widget_id)
        widget.deactivate_viewgeneration()
        return

    def poke(self, params):
        return self._core.get_poke_manager().poke()