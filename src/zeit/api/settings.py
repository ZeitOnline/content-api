# -*- coding: utf-8 -*-
"""
    zeit.api.settings
    ~~~~~~~~~~~~~~~~

    This module contains config classes for different build scenarios.

    Copyright: (c) 2013 by ZEIT ONLINE.
    License: BSD, see LICENSE.md for more details.
"""

class Config(object):

    ACCESS_TIMEFRAME = 86400
    ACCESS_TIERS = {'free': 10000, 'pro': 50000, 'max': 100000}

    SCHEMA = '/schemas/database.sql'
    DATABASE = '/var/lib/zon-api/data.db'
    PRODUCT_ALPHABET = ''
    SERIES_ALPHABET = ''
    KEYWORD_ALPHABET = ''
    DEPARTMENT_ALPHABET = ''
    RECAPTCHA_PRIVATE_KEY = ''
    RECAPTCHA_PUBLIC_KEY = ''

    try:
        import private
        PRODUCT_ALPHABET = private.PRODUCT_ALPHABET
        SERIES_ALPHABET = private.SERIES_ALPHABET
        KEYWORD_ALPHABET = private.KEYWORD_ALPHABET
        DEPARTMENT_ALPHABET = private.DEPARTMENT_ALPHABET
    except:
        pass


class ProductionConfig(Config):

    DOC_URL = 'http://developer.zeit.de'
    API_URL = 'http://api.zeit.de'
    SOLR_URL = 'http://127.0.0.1:8983/solr'

    try:
        import private
        RECAPTCHA_PRIVATE_KEY = private.RECAPTCHA_PRIVATE_PROD
        RECAPTCHA_PUBLIC_KEY = private.RECAPTCHA_PUBLIC_PROD
    except:
        pass


class DevelopmentConfig(Config):

    DOC_URL = 'http://dev-test.zeit.de:8080'
    API_URL = 'http://api-test.zeit.de:8080'
    SOLR_URL = 'http://127.0.0.1:8983/solr'

    import urllib
    if urllib.urlopen(SOLR_URL).getcode() == 404:
        SOLR_URL = 'http://developer.zeit.de:8983/solr'

    try:
        import private
        RECAPTCHA_PRIVATE_KEY = private.RECAPTCHA_PRIVATE_DEVEL
        RECAPTCHA_PUBLIC_KEY = private.RECAPTCHA_PUBLIC_DEVEL
    except:
        pass


class LocalConfig(DevelopmentConfig):

    API_PORT = 5000
    DOC_PORT = 5001
    SERVERNAME = '127.0.0.1'
    API_URL = 'http://%s:%d' % (SERVERNAME, API_PORT)
    DOC_URL = 'http://%s:%d' % (SERVERNAME, DOC_PORT)


class TestingConfig(LocalConfig):

    TESTING = True
