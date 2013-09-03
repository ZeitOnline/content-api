# -*- coding: utf-8 -*-
"""
    zeit.api.application
    ~~~~~~~~~~~~~~~~~~~~

    This module contains factory methods, that return WSGI compatible app
    instances configured for deployment or testing, and a local run method,
    that does not require a full WSGI server.

    Copyright: (c) 2013 by ZEIT ONLINE.
    License: BSD, see LICENSE.md for more details.
"""

import flask

from zeit.api import settings, blueprints


def make_app(blueprint, config):
    """Configure a flask instance with a given blueprint and configuration."""
    app = flask.Flask(import_name=__name__)
    app.register_blueprint(blueprint)
    app.url_map.strict_slashes = False
    app.config.from_object(config)
    return app


def run_local_api():
    """Run an api server instance on a local development server."""
    cfg = settings.LocalConfig()
    app = make_app(blueprints.api_server, cfg)
    app.run(host=cfg.SERVERNAME, port=cfg.API_PORT, debug=True)


def run_local_doc():
    """Runs a developer portal instance on a local development server."""
    cfg = settings.LocalConfig()
    app = make_app(blueprints.developer_portal, cfg)
    app.run(host=cfg.SERVERNAME, port=cfg.DOC_PORT, debug=True)


def test_client_factory():
    """Return a client instance for automated testing."""
    app = make_app(blueprints.api_server, settings.TestingConfig())
    return app.test_client()


def api_factory(global_config, **local_conf):
    """Return an api server instance configured for production."""
    return make_app(blueprints.api_server, settings.ProductionConfig())


def doc_factory(global_config, **local_conf):
    """Return a developer portal instance configured for production."""
    return make_app(blueprints.developer_portal, settings.ProductionConfig())


def api_dev_factory(global_config, **local_conf):
    """Return an api server instance configured for development."""
    return make_app(blueprints.api_server, settings.DevelopmentConfig())


def doc_dev_factory(global_config, **local_conf):
    """Return a developer portal instance configured for development."""
    return make_app(blueprints.developer_portal, settings.DevelopmentConfig())
