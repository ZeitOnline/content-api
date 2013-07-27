# -*- coding: utf-8 -*-
"""
    zeit.api.exceptions
    ~~~~~~~~~~~~~~~~~~~

    This module contains custom JSON formatted HTTP exceptions. Not to be
    confused with the identically named werkzeug module 'exceptions'.
    Exceptions correspond to standard HTTP status codes.

    Copyright: (c) 2013 by ZEIT ONLINE.
    License: BSD, see LICENSE.md for more details.
"""

import json

from flask import request
from werkzeug.exceptions import HTTPException
from werkzeug.utils import escape


class JSONHTTPException(HTTPException):

    def __init__(self, *args, **kwargs):
        super(JSONHTTPException, self).__init__(*args, **kwargs)
        self.description = kwargs.get('description', self.description)
        message = '%d: %s' % (self.code, self.description)
        print >> request.environ['wsgi.errors'], message


    def get_body(self, environ):
        return json.dumps(dict(description=self.get_description(environ)))

    def get_headers(self, environ):
        return [('Content-Type', 'application/json')]


class TooManyRequests(JSONHTTPException):
    code = 429
    description = 'You have reached your request quota.'

    @property
    def name(self):
        return 'Too Many Requests'


class Unauthorized(JSONHTTPException):
    code = 401
    description = 'The provided api key seems to be invalid.'


class EndpointNotFound(JSONHTTPException):
    code = 404
    description = 'The requested endpoint is not defined.'


class ResourceNotFound(JSONHTTPException):
    code = 404
    description = 'The requested resource can not be found.'


class MethodNotAllowed(JSONHTTPException):
    code = 405

    def get_description(self, environ):
        method = escape(environ.get('REQUEST_METHOD', 'GET'))
        return 'The method %s is not allowed for the requested URL.' % method


class BadRequest(JSONHTTPException):
    code = 400
    description = 'The request cannot be fulfilled due to bad syntax.'


class InternalServerError(JSONHTTPException):
    code = 500
    description = 'Due to an internal error the request could not be fulfilled.'


class ServiceUnavailable(JSONHTTPException):
    code = 503
    description = 'The service is currently unavailable.'
