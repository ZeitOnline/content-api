# -*- coding: utf-8 -*-
"""
    zeit.api.metadata
    ~~~~~~~~~~~~~~~~~

    This module contains methods that maintain metadata entities by parsing XML
    files and updating the API's SQLite database.

    Copyright: (c) 2013 by ZEIT ONLINE.
    License: BSD, see LICENSE.md for more details.
"""

import urllib

from flask import g, current_app
from lxml import etree

from .util import iri_to_uri, save_xpath


def __update_product(product):
    """Update the given product entity."""
    product_id = save_xpath(product, './@id').lower()
    uri = '%s/product/%s' % (current_app.config['API_URL'], product_id)
    value = save_xpath(product, 'text()')
    href = save_xpath(product, './@href')
    query = 'REPLACE INTO product VALUES (?, ?, ?, ?);'
    g.db.execute(query, (href, product_id, uri, value))


def __update_series(series):
    """Update the given series entity."""
    series_id = save_xpath(series, './@url')
    uri = '%s/series/%s' % (current_app.config['API_URL'], series_id)
    value = save_xpath(series, './@title')
    name = save_xpath(series, './@serienname')
    query = 'REPLACE INTO series VALUES (?, ?, ?, ?, ?);'
    href = 'http://www.zeit.de/serie/%s' % series_id
    g.db.execute(query, (href, series_id, name, uri, value))


def __update_keyword(keyword, ranks, types):
    """Update the given keyword entity."""
    kw_id = save_xpath(keyword, './@url_value')
    uri = '%s/keyword/%s' % (current_app.config['API_URL'], kw_id)
    value = save_xpath(keyword, 'text()')
    lexical = save_xpath(keyword, './@lexical_value')
    kw_type = save_xpath(keyword, './@type')
    kw_type = 'subject' if kw_type in ['free', 'topic'] else kw_type.lower()
    score = (ranks.index(int(save_xpath(keyword, './@freq'))) + 1)
    score = int(100.0 / len(ranks) * score)
    href = 'http://www.zeit.de/schlagworte/%s/%s/index' % (types[kw_type], kw_id)
    query = 'REPLACE INTO keyword VALUES (?, ?, ?, ?, ?, ?, ?);'
    g.db.execute(query, (href, kw_id, lexical, score, kw_type, uri, value))


def __update_department(department):
    """Update the given department entity."""
    dept_id = save_xpath(department, './@label')
    if dept_id in ['startseite']:
        return
    uri = '%s/department/%s' % (current_app.config['API_URL'], dept_id)
    value = save_xpath(department, 'text()')
    href = save_xpath(department, './@href')[19:].split('/', 1)[0]
    parent = href if href != dept_id else ''
    path = parent + '/' + dept_id if parent else dept_id
    href = 'http://www.zeit.de/%s/index' % path
    query = 'REPLACE INTO department VALUES (?, ?, ?, ?, ?);'
    g.db.execute(query, (href, dept_id, parent, uri, value))


def __update_author(author):
    """Update the given author entity."""
    value = save_xpath(author, './@name')
    author_id = value.replace(' ', '-')
    uri = '%s/author/%s' % (current_app.config['API_URL'], author_id)
    initial = value.split(' ')[-1] or 'A'
    href_raw = 'http://www.zeit.de/autoren/%s/%s/index.xml'
    href = href_raw % (initial[0], value.replace(' ', '_'))
    href = href if urllib.urlopen(iri_to_uri(href)).getcode() == 200 else ''
    query = 'REPLACE INTO author VALUES (?, ?, ?, ?, ?);'
    g.db.execute(query, (href, author_id, 'author', uri, value))


def update():
    """Update metadata of all categories and write changes to database."""
    products = current_app.config['PRODUCT_ALPHABET']
    for p in etree.parse(products).xpath('//product'):
        __update_product(p)

    series = current_app.config['SERIES_ALPHABET']
    for s in etree.parse(series).xpath('//series'):
        print s
        __update_series(s)

    keywords = current_app.config['KEYWORD_ALPHABET']
    parsed_keywords = etree.parse(keywords).xpath('//tag')
    ranks = sorted(set(int(save_xpath(k, './@freq')) for k in parsed_keywords))
    types = {'location': 'orte', 'person': 'personen', 'subject': 'themen',
        'organization': 'organisationen'}
    for k in parsed_keywords:
        print k
        __update_keyword(k, ranks, types)

    depts = current_app.config['DEPARTMENT_ALPHABET']
    for d in etree.parse(depts).xpath('/lists/list[@id="sitemap"]//link'):
        print d
        __update_department(d)

    url = '/select?q=*:*&facet=true&facet.field=author'
    url += '&facet.limit=1000000&rows=0&facet.mincount=1'
    authors = current_app.config['SOLR_URL'] + url
    for a in etree.parse(authors).xpath('//lst[@name="author"]/int'):
        print a
        __update_author(a)
