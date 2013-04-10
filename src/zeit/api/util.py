# -*- coding: utf-8 -*-
"""
    zeit.api.util
    ~~~~~~~~~~~~~

    This module provides helper functions used throughout the application.

    Copyright: (c) 2013 by ZEIT ONLINE.
    License: BSD, see LICENSE.md for more details.
"""

import re
import urllib
import urlparse


def append_to_csv(csv, new):
    """Add a new value to a string formatted, comma separted value list."""

    if csv == '':
        return new
    arr = csv.split(',')
    arr.append(new)
    return ','.join(arr)


def csv_to_list(csv):
    """Convert a csv string to an array, while ommitting empty entries."""

    for val in csv.split(','):
        if val != '':
            yield val


def dict_by_list(dic, arr):
    """Filter a dictionary by a list of valid keys."""

    for key in dic:
        if key in arr:
            yield key, dic[key]


def ensure_prefix(string, prefix):
    """Ensure, that a string is prefixed by another string."""

    if string[:len(prefix)] == prefix:
        return string
    return prefix + string


def iri_to_uri(iri):
    """Convert an Internationalized Resource Identifier to a URI."""

    parts = urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti == 1 else
            url_encode_non_ascii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )


def save_xpath(element, xpath, fallback=''):
    """Safely return the first result of an xpath expression."""

    try:
        return element.xpath(xpath)[0]
    except IndexError:
        return fallback


def url_encode(data):
    """Safely encode a dictionary to a URL compatible string."""

    param = dict()
    for key, val in data.iteritems():
        if key == 'facet.field':
            param[key] = list(csv_to_list(val))
        elif isinstance(val, int):
            param[key] = '%d' % val
        else:
            param[key] = val
    return urllib.urlencode(param, True)


def url_encode_non_ascii(href):
    """URL-encode non ascii characters."""

    function = lambda c: '%%%02x' % ord(c.group(0))
    return re.sub('[\x80-\xFF]', function, href)
