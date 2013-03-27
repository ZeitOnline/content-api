# -*- coding: utf-8 -*-
"""
    zeit.api.exception
    ~~~~~~~~~~~~~~~~~~

    This module contains custom JSON exceptions. Not to be confused with the
    similarly named flask module 'exceptions'. Exceptions correspond to
    standard HTTP status codes.

    Copyright: (c) 2013 by ZEIT ONLINE.
    License: BSD, see LICENSE.md for more details.
"""

from flask.exceptions import JSONHTTPException
from werkzeug.exceptions import (escape, NotFound, MethodNotAllowed,
	Unauthorized, BadRequest, InternalServerError, ServiceUnavailable)
from flask import request


class JSONTooManyRequests(JSONHTTPException):
	code = 429
	description = 'You have reached your request quota.'
	@property
	def name(self):
		return 'Too Many Requests'


class JSONUnauthorized(JSONHTTPException, Unauthorized):
	description = 'The provided api key seems to be invalid.'


class JSONEndpointNotFound(JSONHTTPException, NotFound):
	description = 'The requested endpoint is not defined.'


class JSONResourceNotFound(JSONHTTPException, NotFound):
	description = 'The requested resource can not be found.'


class JSONMethodNotAllowed(JSONHTTPException, MethodNotAllowed):
	def get_description(self, environ):
		m = escape(environ.get('REQUEST_METHOD', 'GET'))
		return 'The method %s is not allowed for the requested URL.' % m


class JSONBadRequest(JSONHTTPException, BadRequest):
	description = 'The request cannot be fulfilled due to bad syntax.'


class JSONInternalServerError(JSONHTTPException, InternalServerError):
	description = 'Due to an internal error the request could not be fulfilled.'


class JSONServiceUnavailable(JSONHTTPException, ServiceUnavailable):
	description = 'The service is currently unavailable.'

def too_many_requests(error = None):
	excp = JSONTooManyRequests()
	message = '%d: %s' % (excp.code, error or excp.description)
	print >> request.environ['wsgi.errors'], message
	return excp

def unauthorized(error = None):
	excp = JSONUnauthorized()
	message = '%d: %s' % (excp.code, error or excp.description)
	print >> request.environ['wsgi.errors'], message
	return excp

def endpoint_not_found(error = None):
	excp = JSONEndpointNotFound()
	message = '%d: %s' % (excp.code, error or excp.description)
	print >> request.environ['wsgi.errors'], message
	return excp

def resource_not_found(error = None):
	excp = JSONResourceNotFound()
	message = '%d: %s' % (excp.code, error or excp.description)
	print >> request.environ['wsgi.errors'], message
	return excp

def method_not_allowed(error = None):
	excp = JSONMethodNotAllowed()
	message = '%d: %s' % (excp.code, error or excp.description)
	print >> request.environ['wsgi.errors'], message
	return excp

def bad_request(error = None):
	excp = JSONBadRequest()
	message = '%d: %s' % (excp.code, error or excp.description)
	print >> request.environ['wsgi.errors'], message
	return excp

def internal_server_error(error = None):
	excp = JSONInternalServerError()
	message = '%d: %s' % (excp.code, error or excp.description)
	print >> request.environ['wsgi.errors'], message
	return excp

def service_unavailable(error = None):
	excp = JSONServiceUnavailable()
	message = '%d: %s' % (excp.code, error or excp.description)
	print >> request.environ['wsgi.errors'], message
	return excp
