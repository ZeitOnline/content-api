# -*- coding: utf-8 -*-
"""
    zeit.api.queries
    ~~~~~~~~~~~~~~~~

    This module contains classes for the different kind of queries a client
    may submit to the API. These define allowed parameters and values, methods
    to fetch a raw result set from a Solr server and transform or enrich the
    received results.

    Copyright: (c) 2013 by ZEIT ONLINE.
    License: BSD, see LICENSE.md for more details.
"""

import json
import exceptions
import os
import time
import urllib
import urllib2
import warnings

from flask import g, current_app as current_app, request

from . import exception, parameters, util


class Query(object):
    """The base class for all API queries."""

    def __getitem__(self, key):
        if key not in self.__dict__.keys():
            raise exceptions.KeyError()
        return self.__dict__[key]

    def __init__(self, **kwargs):
        for kw in kwargs:
            if kw in self.__dict__.keys():
                getattr(self, kw).value = kwargs[kw]
            elif kw == 'callback' or kw == 'api_key':
                pass
            else:
                warnings.warn('Unsupported parameter key %s' % kw)

    def __iter__(self):
        for param in self.__dict__.values():
            if isinstance(param, parameters.Param):
                yield (param.origin or param.key, param.value)

    def __str__(self):
        return str(dict(self.__iter__()))

    def items(self):
        return list(self.__iter__())

    def params(self):
        for param in self.__dict__.values():
            if isinstance(param, parameters.Param) and param.key:
                yield (param.key, param.value)


class SearchQuery(Query):
    """The base class for all SQL-based searches."""

    _default_field = 'value'

    def __init__(self, endpoint, **kwargs):
        self.q = parameters.SqlQParam()
        self.limit = parameters.LimitParam()
        self.offset = parameters.OffsetParam()
        self._endpoint = endpoint
        super(SearchQuery, self).__init__(**kwargs)

    def _fetch_raw(self):
        sql = 'SELECT * FROM %s WHERE %s LIKE ? LIMIT ?, ?;'
        query = sql % (self._endpoint, self._default_field)
        options = (self.q.value, self.offset.value, self.limit.value)
        result = g.db.execute(query, options).fetchall()
        return result

    def _fetch_count(self):
        sql = 'SELECT COUNT(*) FROM %s WHERE %s LIKE ?;'
        query = sql % (self._endpoint, self._default_field)
        result = g.db.execute(query, (self.q.value,)).fetchone()
        return result[0]

    def _matches(self):
        for row in self._fetch_raw():
            match = dict()
            for key in self.fields:
                position = self.fields.default.split(',').index(key)
                match[key] = row[position]
            yield match

    def fetch(self):
        return dict(
            matches=list(self._matches()),
            found=self._fetch_count(),
            limit=int(self.limit.value),
            offset=int(self.offset.value)
        )


class AuthorSearchQuery(SearchQuery):
    """Search query for content authors."""

    def __init__(self, **kwargs):
        self.fields = parameters.FieldsParam(
            default='href,id,type,uri,value'
        )
        super(AuthorSearchQuery, self).__init__('author', **kwargs)


class DepartmentSearchQuery(SearchQuery):
    """Search query for newspaper departments."""

    def __init__(self, **kwargs):
        self.fields = parameters.FieldsParam(
            default='href,id,parent,uri,value'
        )
        super(DepartmentSearchQuery, self).__init__('department', **kwargs)


class KeywordSearchQuery(SearchQuery):
    """Search query for available keywords."""

    def __init__(self, **kwargs):
        self.fields = parameters.FieldsParam(
            default='href,id,lexical,score,type,uri,value'
        )
        super(KeywordSearchQuery, self).__init__('keyword', **kwargs)


class ProductSearchQuery(SearchQuery):
    """Search query for publication products."""

    def __init__(self, **kwargs):
        self.fields = parameters.FieldsParam(
            default='href,id,uri,value'
        )
        super(ProductSearchQuery, self).__init__('product', **kwargs)


class SeriesSearchQuery(SearchQuery):
    """Search query for article series."""

    def __init__(self, **kwargs):
        self.fields = parameters.FieldsParam(
            default='href,id,name,uri,value'
        )
        super(SeriesSearchQuery, self).__init__('series', **kwargs)


class ContentSearchQuery(Query):
    """Unfiltered content search query."""

    _endpoint = 'content'
    __action = 'search'

    def __init__(self, **kwargs):
        self.q = parameters.StrParam(
            key='q',
            origin='q',
            default='*:*'
        )
        self.sort = parameters.StrParam(
            key='sort',
            origin='sort',
            default='release_date desc'
        )
        self.fields = parameters.FieldsParam(
            default=('subtitle,uuid,title,href,release_date,'
                'uri,snippet,supertitle,teaser_title,teaser_text'),
            enforce='uuid'
        )
        self.facet_date = parameters.FacetDateParam()
        self.facet_field = parameters.FacetFieldParam()
        self.limit = parameters.LimitParam()
        self.offset = parameters.OffsetParam()
        super(ContentSearchQuery, self).__init__(**kwargs)
        if self.facet_field.value != '' or self.facet_date.value != '':
            self.facet = parameters.StrParam(
                key='facet',
                origin='facet',
                default='true'
            )
        if self.facet_date.value != '':
            self.facet_date_field = parameters.StrParam(
                origin='facet.date',
                default='release_date'
            )

    def _fetch_raw(self):
        query = util.url_encode(dict(self))
        url = '%s/%s/%s?%s' % (current_app.config['SOLR_URL'],
            self.__class__._endpoint, self.__action, query)
        try:
            data = urllib2.urlopen(url)
            return json.load(data)
        except urllib2.URLError:
            raise exception.service_unavailable()

    def _make_matches(self, raw):
        for match in raw['response']['docs']:
            if 'uri' in self.fields:
                match['uri'] = '%s/%s/%s' % (current_app.config['API_URL'],
                    self.__class__._endpoint, match['uuid'])
            if 'snippet' in self.fields and self.q.value != self.q.default:
                snippet = raw['highlighting'][match['uuid']]
                if len(snippet.values()) > 0:
                    match['snippet'] = snippet.values()[0][0]
            if self.fields._value:
                if 'uuid' not in self.fields._value:
                    del match['uuid']

    def fetch(self):
        raw = self._fetch_raw()
        self._make_matches(raw)
        response = dict(
            matches=raw['response']['docs'],
            found=raw['response']['numFound'],
            limit=int(self.limit.value),
            offset=int(self.offset.value)
        )
        if  hasattr(self, 'facet'):
            response['facets'] = dict()
            response['facets'].update(
                raw['facet_counts']['facet_dates'])
            response['facets'].update(
                raw['facet_counts']['facet_fields'])
        return response


class FilteredContentSearchQuery(ContentSearchQuery):
    """Pre-filtered search query."""

    _default_field = 'id'

    def __init__(self, endpoint='', filter_id='', **kwargs):

        self.fq = parameters.StrParam(
            default='%s:%s' % (endpoint, filter_id),
            origin='fq'
        )
        super(FilteredContentSearchQuery, self).__init__(**kwargs)
        self._endpoint = endpoint
        self._id = filter_id

    def fetch(self):
        if self._endpoint not in ('author', 'content', 'department', 'keyword',
                'product', 'series'):
            raise exception.endpoint_not_found()
        sql = 'SELECT * FROM %s WHERE %s LIKE :q;'
        query = sql % (self._endpoint, self._default_field)
        result = g.db.execute(query, {'q': self._id}).fetchall()
        if len(result) == 0:
            raise exception.resource_not_found()
        if self._endpoint == 'author':
            self.fq.value = self.fq.value.replace('-', '*')
        meta = dict(zip(QueryFactory(self._endpoint).fields, result[0]))
        if self._endpoint == 'department':
            if meta['parent'] != '':
                self.fq.value = 'sub_department:%s' % (self._id)
        meta.update(super(FilteredContentSearchQuery, self).fetch())
        return meta


class DisplayClientQuery(Query):
    """Display client information and API usage stats."""

    def __init__(self, **kwargs):
        super(DisplayClientQuery, self).__init__(**kwargs)

    def fetch(self):
        row = g.db.execute('SELECT * FROM client WHERE api_key=?',
                (g.api_key,)).fetchone()
        return dict(
            api_key=row[0],
            tier=row[1],
            name=row[2],
            email=row[3],
            requests=row[4],
            reset=row[5],
            quota=current_app.config['ACCESS_TIERS'][row[1]]
        )


class RegisterClientQuery(Query):
    """Register a new API client with a POST request."""

    def __init__(self, **kwargs):
        self.name = parameters.StrParam()
        self.email = parameters.StrParam()
        self.challenge = parameters.StrParam()
        self.response = parameters.StrParam()
        super(RegisterClientQuery, self).__init__(**kwargs)

    def _verify_captcha(self):
        if current_app.config['TESTING']:
            return True
        data = urllib.urlencode(
            dict(
                privatekey=current_app.config['RECAPTCHA_PRIVATE_KEY'],
                remoteip=request.remote_addr,
                challenge=self.challenge.value,
                response=self.response.value
            )
        )
        url = 'http://www.google.com/recaptcha/api/verify'
        return 'true' in urllib.urlopen(url, data).readline()

    def push(self):
        empty = self.name.value == '' or self.email.value == ''
        if empty or not self._verify_captcha():
            raise exception.bad_request()
        g.api_key = str(os.urandom(26).encode('hex'))
        tier = 'free'
        name = self.name.value
        email = self.email.value
        requests = 0
        reset = int(time.time())
        query = 'INSERT INTO client VALUES (?, ?, ?, ?, ?, ?)'
        g.db.execute(query, (g.api_key, tier, name, email, requests, reset))
        return DisplayClientQuery().fetch()


class QueryFactory(object):
    """A factory class for general endpoint queries."""

    def __init__(self, endpoint='', **kwargs):
        if endpoint == 'author':
            self.__class__ = AuthorSearchQuery
        elif endpoint == 'client':
            self.__class__ = DisplayClientQuery
        elif endpoint == 'content':
            self.__class__ = ContentSearchQuery
        elif endpoint == 'department':
            self.__class__ = DepartmentSearchQuery
        elif endpoint == 'keyword':
            self.__class__ = KeywordSearchQuery
        elif endpoint == 'product':
            self.__class__ = ProductSearchQuery
        elif endpoint == 'series':
            self.__class__ = SeriesSearchQuery
        else:
            raise exception.endpoint_not_found()
        self.__init__(**kwargs)


class ContentIdQuery(Query):
    """Display content item with the given id."""

    _endpoint = 'content'
    __action = 'id'

    def __init__(self, content_id='', **kwargs):
        self.fields = parameters.CsvParam(
            default=('categories,creators,href,keywords,relations,release_'
                'date,supertitle,teaser_text,teaser_title,title,uri,uuid'),
            key='fields'
        )
        self.fq = parameters.StrParam(
            default='uuid:%s' % content_id,
            origin='fq'
        )
        self.q = parameters.StrParam(
            origin='q',
            default='*:*'
        )
        super(ContentIdQuery, self).__init__(**kwargs)

    def _fetch_raw(self):
        query = util.url_encode(dict(self))
        url = '%s/%s/%s?%s' % (current_app.config['SOLR_URL'],
            self.__class__._endpoint, self.__action, query)
        try:
            data = urllib2.urlopen(url)
            return json.load(data)
        except urllib2.URLError:
            raise exception.service_unavailable()

    def _fetch_keywords(self, keywords):
        for keyword in keywords:
            query = 'SELECT type, value FROM keyword WHERE id = ?;'
            row = g.db.execute(query, (keyword,)).fetchone()
            if row is None:
                continue
            yield dict(
                rel=row[0],
                name=row[1],
                uri='%s/keyword/%s' % (current_app.config['API_URL'],
                    keyword)
            )

    def _fetch_relations(self, relations):
        for relation in relations:
            url = '%s/content/id?q=%s' % (current_app.config['SOLR_URL'],
                relation)
            solr_data = urllib2.urlopen(url)
            try:
                parsed = json.load(solr_data)
                title = parsed['response']['docs'][0]['title']
            except:
                continue
            yield dict(
                rel='related',
                name=title,
                uri='%s/content/%s' % (current_app.config['API_URL'],
                    relation)
            )

    def _fetch_authors(self, authors):
        for author in authors:
            yield dict(
                rel='author',
                name=author,
                uri='%s/author/%s' % (current_app.config['API_URL'],
                    author.replace(' ', '-'))
            )

    def _fetch_category(self, endpoint, cat_id, type):
        query = 'SELECT value FROM %s WHERE id = "%s";' % (endpoint, cat_id)
        row = g.db.execute(query).fetchone()
        if row:
            yield dict(
                rel=type,
                name=row[0],
                uri='%s/%s/%s' % (current_app.config['API_URL'],
                    endpoint, cat_id)
            )

    def fetch(self):
        raw = self._fetch_raw()

        if len(raw['response']['docs']) == 0:
            raise exception.resource_not_found()
        else:
            doc = raw['response']['docs'][0]

        categories = [('department', 'department'), ('product', 'product'),
            ('sub_department', 'department'), ('series', 'series')]
        whitelist = ['categories', 'creators', 'keywords', 'relations']
        blacklist = ['body']

        for key in whitelist:
            doc[key] = []

        for key in blacklist:
            if key in doc:
                del doc[key]

        if 'uri' in self.fields:
            doc['uri'] = '%s/%s/%s' % (current_app.config['API_URL'],
                self._endpoint, doc['uuid'])

        if 'keyword' in doc and 'keywords' in self.fields:
            kw = self._fetch_keywords(doc['keyword'])
            doc['keywords'].extend(kw)
            del doc['keyword']

        if 'related' in doc and 'relations' in self.fields:
            rl = self._fetch_relations(doc['related'])
            doc['relations'].extend(rl)
            del doc['related']

        if 'author' in doc and 'creators' in self.fields:
            au = self._fetch_authors(doc['author'])
            doc['creators'].extend(au)
            del doc['author']

        for category, endpoint in categories:
            if category in doc and 'categories' in self.fields:
                cat_id = doc[category]
                cat = self._fetch_category(endpoint, cat_id, category)
                doc['categories'].extend(cat)
                del doc[category]

        for key in doc.keys():
            if key not in self.fields:
                del doc[key]

        return doc


class DefinitionQuery(Query):
    """Return API meta information for all available queries."""

    def __init__(self, **kwargs):
        super(DefinitionQuery, self).__init__(**kwargs)

    def _make_def(self, endpoint, query_class):
        url = '%s/%s' % (current_app.config['API_URL'], endpoint)
        params = dict(p for p in query_class().params())
        doc = query_class().__doc__
        return endpoint, dict(url=url, params=params, doc=doc)

    def fetch(self):
        endpoints = {'author': AuthorSearchQuery,
            'author/{id}': FilteredContentSearchQuery,
            'client': DisplayClientQuery,
            'content': ContentSearchQuery,
            'content/{id}': ContentIdQuery,
            'department': DepartmentSearchQuery,
            'department/{id}': FilteredContentSearchQuery,
            'keyword': KeywordSearchQuery,
            'keyword/{id}': FilteredContentSearchQuery,
            'product': ProductSearchQuery,
            'product/{id}': FilteredContentSearchQuery,
            'series': SeriesSearchQuery,
            'series/{id}': FilteredContentSearchQuery}
        return dict(self._make_def(ep, endpoints[ep]) for ep in endpoints)
