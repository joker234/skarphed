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

from cgi import FieldStorage
from urlparse import parse_qs
from traceback import print_exc
from StringIO import StringIO
import json

import logging
import os
import sys

sys.path.append(os.path.dirname(__file__))

from database import *
from logger import logger
from protocolhandler import ProtocolHandler
from repository import *
from session import SessionMiddleware
from shareddatamiddleware import SharedDataMiddleware


def default_template(environ, response_headers):
    """
    Loads the default repositories template and returns it.
    """
    try:
        f = open('/usr/share/skdrepo/template.html')
        template = f.read()
        f.close()
        repository = Repository()
        template = template.replace('{{publickey}}', repository.get_public_key(environ))
        response_body = [template]
        response_headers.append(('Content-Type', 'text/html'))
        response_headers.append(('Content-Length', str(len(template))))
        status = '200 OK'
    except IOError, ie:
        response_body = ['404 Not Found'] # TODO: improve error message
        response_headers.append(('Content-Type', 'text/plain'))
        status = '404 Not Found'
    except RepositoryException, e:
        # TODO what to return if there is no public key
        response_body = ['404 Not Found'] # TODO: improve error message
        response_headers.append(('Content-Type', 'text/plain'))
        status = '404 Not Found'
    except DatabaseException, e:
        # TODO what to return if there is no public key
        response_body = ['404 Not Found'] # TODO: improve error message
        response_headers.append(('Content-Type', 'text/plain'))
        status = '404 Not Found'
    return (status, response_body)


def repo_application(environ, start_response):
    """
    The repositories WSGI application. If the incoming request's type is POST then it
    will be delegated to a protocol handler, otherwise the default template will be returned.
    """
    response_body = []
    response_headers = []

    status = '200 OK'
    if environ['REQUEST_METHOD'] == 'POST':
        try:
            size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError, e:
            size = 0
        args = FieldStorage(fp=environ['wsgi.input'], environ=environ)
        jsonstr = args.getvalue('j')
        logger.info('POST from %s: %s' % (environ['REMOTE_ADDR'], jsonstr))

        try:
            repository = Repository()
            handler = ProtocolHandler(repository, jsonstr)
            response_body = [handler.execute(environ)]
        except DatabaseException, e:
            logger.warning('database exception: %s' % str(e))
            response_body = ['{"error":{"c":%d,"args":["errorstr":"%s"]}}' %
                    (RepositoryErrorCode.DATABASE_ERROR, str(e))]
        except RepositoryException, e:
            logger.warning('repository exception: %s' % json.dumps(e.get_error_json()))
            response_body = ['{"error":%s}' % json.dumps(e.get_error_json())] 
        except Exception, e:
            logger.warning('unknown exception: %s' % str(e))
            response_body = ['{"error":%s}' % str(e)]

        response_headers.append(('Content-Type', 'application/json'))

        logger.debug('response to %s: %s, %s, %s' % (environ['REMOTE_ADDR'], status, str(response_headers), str(response_body)))
    else:
        logger.info('GET from %s: %s' % (environ.get('REMOTE_ADDR', 'unknown'), environ['PATH_INFO']))
        if environ['PATH_INFO'] == '/':
            (status, response_body) = default_template(environ, response_headers) 
        else:
            (status, response_body) = ('404 Not Found', '404 Not Found')
        logger.debug('response to %s: %s, %s' % (environ['REMOTE_ADDR'], status, str(response_headers)))
    
    start_response(status, response_headers)
    return response_body


"""
Wraps the repository application in a
0) SharedDataMiddleware, to provide some static content
1) DatabaseMiddleware, to provide a database connection via environ['db']
2) SessionMiddleware, to provide session handling
"""
application = SharedDataMiddleware(
        DatabaseMiddleware(SessionMiddleware(repo_application)),
        'static')
