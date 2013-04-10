# -*- coding: utf-8 -*-
"""
    zeit.api.access
    ~~~~~~~~~~~~~~~

    This module provides functionalities for regulating API access.

    Copyright: (c) 2013 by ZEIT ONLINE.
    License: BSD, see LICENSE.md for more details.
"""
import time

from flask import g, current_app as current_app

from . import exception


class Verifictaion(object):
    """Context manager class for API key validation and usage tracking."""

    def __enter__(self):
        """Verify key and quota. Raise exception if either fails."""
        if not hasattr(g, 'api_key'):
            raise exception.unauthorized()

        query = 'SELECT requests,reset,tier FROM client WHERE api_key=?;'
        client = g.db.execute(query, (g.api_key,)).fetchone()

        if not client:
            raise exception.unauthorized()

        requests = client[0]
        reset = client[1]
        quota = current_app.config['ACCESS_TIERS'][client[2]]
        timeframe = current_app.config['ACCESS_TIMEFRAME']

        if (int(time.time()) - reset) / timeframe > 0:
            reset += ((int(time.time()) - reset) / timeframe) * timeframe
            requests = 0
            query = ('UPDATE OR IGNORE client SET reset=?, requests=? '
                'WHERE api_key=?;')
            g.db.execute(query, (reset, requests, g.api_key))

        if quota <= requests:
            raise exception.too_many_requests()

    def __exit__(self, type, value, traceback):
        """Increase request counter before closing context."""
        query = ('UPDATE OR IGNORE client SET requests=requests + 1 '
            'WHERE api_key=?;')
        g.db.execute(query, (g.api_key,))
