# -*- coding: utf-8 -*-
"""
    zeit.api.blueprints
    ~~~~~~~~~~~~~~~~~~~

    This module configures two blueprint instances, one for the api server and
    one for the developer portal and documentation.

    Copyright: (c) 2013 by ZEIT ONLINE.
    License: BSD, see LICENSE.md for more details.
"""

import contextlib
import sqlite3

import flask
from flask import g, jsonify, current_app as current_app
from werkzeug.datastructures import ImmutableDict

from zeit.api import access, metadata, queries
from zeit.api.exceptions import BadRequest, ResourceNotFound, \
    MethodNotAllowed, InternalServerError


api_server = flask.Blueprint('api_server', __name__)
developer_portal = flask.Blueprint('developer_portal', __name__)
developer_portal.jinja_options = ImmutableDict(
    {'extensions': ['jinja2.ext.loopcontrols']})


@api_server.app_errorhandler(400)
def handle_bad_request(error):
    return BadRequest(error)


@api_server.app_errorhandler(404)
def handle_resource_not_found(error):
    return ResourceNotFound(error)


@api_server.app_errorhandler(405)
def handle_method_not_allowed(error):
    return MethodNotAllowed(error)


@api_server.app_errorhandler(500)
def handle_internal_server_error(error):
    return InternalServerError(error)


@api_server.before_app_first_request
def initialize_database():
    """On first startup, make sure the database is initialized."""
    g.db = sqlite3.connect(current_app.config['DATABASE'],
        isolation_level=None)
    schema = (current_app.root_path + current_app.config['SCHEMA'])
    with contextlib.closing(g.db) as db:
        with api_server.open_resource(schema) as f:
            db.cursor().executescript(f.read())
            db.commit()


@api_server.before_app_request
def before_request():
    """Intercept preflight requests, connect db and extract API key."""
    if flask.request.method == 'OPTIONS':
        return flask.Response(status=204)
    g.db = sqlite3.connect(current_app.config['DATABASE'],
        isolation_level=None)
    g.api_key = flask.request.headers.get('X-Authorization',
        flask.request.args.get('api_key', None))


@api_server.after_app_request
def after_request(response):
    """Optionally convert to JSONP, set response headers and close db."""
    callback = flask.request.args.get('callback', False)
    if callback:
        response.data = str(callback) + '(' + response.data + ');'
        response.mimetype = 'application/javascript'
    response.mimetype += ';charset=UTF-8'
    response.headers['Server'] = 'Zeit Api'
    response.headers['Cache-Control'] = 'max-age=1'
    if hasattr(g, 'db'):
        g.db.close()
    return response


@api_server.route('/')
def show_definition():
    query = queries.DefinitionQuery()
    return jsonify(query.fetch())


@api_server.route('/trigger')
def trigger_update():
    metadata.update()
    return flask.Response(status=204)


@api_server.route('/client',  methods=['POST'])
def register_client():
    form = flask.request.form.copy().to_dict()
    query = queries.RegisterClientQuery(**form)
    return jsonify(query.push())


@api_server.route('/<string:endpoint>')
def search(endpoint):
    with access.Verifictaion():
        param = flask.request.args.copy().to_dict()
        query = queries.QueryFactory(endpoint, **param)
        return jsonify(query.fetch())


@api_server.route('/<string:endpoint>/<string:res>')
def filtered_search(endpoint, res):
    with access.Verifictaion():
        param = flask.request.args.copy().to_dict()
        query = queries.FilteredContentSearchQuery(endpoint, res, **param)
        return jsonify(query.fetch())


@api_server.route('/content/<string:uuid>')
def content_by_id(uuid):
    with access.Verifictaion():
        param = flask.request.args.copy().to_dict()
        query = queries.ContentIdQuery(uuid, **param)
        return jsonify(query.fetch())


@developer_portal.route('/')
def redirect_index():
    return flask.redirect('/index/')


@developer_portal.route('/style.css')
def style_sheet():
    response = flask.make_response(flask.render_template('style.css'))
    response.headers['Content-Type'] = 'text/css'
    return response


@developer_portal.route('/<path:path>/')
def documentation(path):
    if 'documentation' in path:
        return flask.redirect(path.replace('documentation', 'docs'))

    context = dict(
        trunk=path if '/' not in path else path.split('/')[0],
        file=path if '/' not in path else path.split('/')[-1],
        recaptcha=current_app.config['RECAPTCHA_PUBLIC_KEY'],
        api_url=current_app.config['API_URL'],
        doc_url=current_app.config['DOC_URL']
    )
    try:
        return flask.render_template(path + '.html', **context)
    except Exception, e:
        current_app.logger.error('%r: %s' % (e, e.message))
        rendered = flask.render_template('error.html', **context)
        return flask.make_response(rendered, 404)


@developer_portal.after_app_request
def caching(response):
    response.headers['Cache-Control'] = 'max-age=7200, public'
    response.headers['Server'] = 'Zeit Developer'
    return response
