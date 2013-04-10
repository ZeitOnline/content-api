# -*- coding: utf-8 -*-
"""
    zeit.api.tests
    ~~~~~~~~~~~~~~~~

    This module contains automated testing functionalities.

    Copyright: (c) 2013 by ZEIT ONLINE.
    License: BSD, see LICENSE.md for more details.
"""
import json
import random
import unittest
import werkzeug

from . import application


class ClientTestCase(unittest.TestCase):

    def setUp(self):
        self.client = application.test_client_factory()
        data = dict(
            name = 'Any Name',
            email = 'mail@provider.tld',
            challenge = '0123456789',
            response = 'abcdefghij'
            )
        resp = self.client.post('/client', data = data)
        self.parsed = json.loads(resp.data)

    def test_signup(self):
        """Client signup successful."""
        self.assertTrue(self.parsed.has_key('api_key'))

    def test_unauthorized(self):
        """Unauthorized access blocked."""
        resp = self.client.get('/client')
        self.assertEqual(resp.status_code, 401)

    def test_api_key_parameter(self):
        """Authorization via URL parameter."""
        query_string = dict(api_key = self.parsed['api_key'])
        resp = self.client.get('/client', query_string = query_string)
        self.assertEqual(resp.status_code, 200)

    def test_x_authorization_header(self):
        """Authorization via HTTP header."""
        headers = werkzeug.datastructures.Headers()
        headers.add('X-Authorization', self.parsed['api_key'])
        resp = self.client.get('/client', headers = headers)
        self.assertEqual(resp.status_code, 200)


class QueryTestCase(unittest.TestCase):

    def setUp(self):
        self.client = application.test_client_factory()
        data = dict(name = 'Some Name', email = 'mail@provider.tld')
        resp = self.client.post('/client', data = data)
        self.headers = werkzeug.datastructures.Headers()
        self.headers.add('X-Authorization', json.loads(resp.data)['api_key'])

    def __get_json(self, url, data = {}):
        print 'Checking ' + url + ' with ' + str(data)
        resp = self.client.get(url, headers = self.headers)
        self.assertEqual(resp.status_code, 200)
        return json.loads(resp.data)

    def test_endpoint_availability(self):
        """All endpoints up and running."""
        endpoints = self.__get_json('/')
        for path in endpoints:
            if '{id}' in path:
                continue
            endpoint = self.__get_json('/' + path)
            if 'matches' in endpoint:
                for match in endpoint['matches']:
                    ids = (match[i] for i in ['id', 'uuid'] if i in match)
                    for i in list(ids):
                        self.__get_json('/' + path + '/' + i)

    def test_parameter_defaults(self):
        """Parameters accepting their default values."""
        for endpoint, definition in self.__get_json('/').items():
            if '{id}' in endpoint:
                continue
            for param, val in definition['params'].items():
                self.__get_json('/' + endpoint, {param: val})


class ParameterTestCase(unittest.TestCase):

    def setUp(self):
        self.client = application.test_client_factory()
        data = dict(name = 'Some Name', email = 'mail@provider.tld')
        resp = self.client.post('/client', data = data)
        self.headers = werkzeug.datastructures.Headers()
        self.headers.add('X-Authorization', json.loads(resp.data)['api_key'])
        resp = self.client.get('/', headers = self.headers)
        self.endpoints = json.loads(resp.data)

    def test_callback_parameter(self):
        """Callback parameter results in JSONP output."""
        for ep in self.endpoints:
            if '{id}' in ep or 'client' in ep:
                continue
            rnd = ''.join(random.choice('abcdefghij') for x in range(5))
            json_resp = self.client.get(
                '/' + ep,
                query_string = dict(limit = 1),
                headers = self.headers
            )
            jsonp_resp = self.client.get(
                '/' + ep,
                query_string = dict(callback = rnd, limit = 1),
                headers = self.headers
            )
            expected = rnd + '(' + json_resp.data + ');'
            self.assertEqual(expected, jsonp_resp.data)

    def test_limit_parameter(self):
        """Limit parameter behaves as expected."""
        for ep in self.endpoints:
            if '{id}' in ep or 'limit' not in self.endpoints[ep]['params']:
                continue
            for entry, result in [(-1, 0), (0, 0), (1, 1), (1025, 0)]:
                resp = self.client.get(
                    '/' + ep,
                    query_string = dict(limit = entry),
                    headers = self.headers
                    )
                matches = json.loads(resp.data).get('matches', [])
                self.assertEqual(len(matches), result)

    def test_offset_parameter(self):
        """Offset parameter behaves as expected."""
        for ep in self.endpoints:
            if '{id}' in ep or 'offset' not in self.endpoints[ep]['params']:
                continue
            resp = self.client.get(
                '/' + ep,
                query_string = dict(limit = 0),
                headers = self.headers
                )
            maximum = json.loads(resp.data)['found']

            for entry, code in [(-1, 400), (0, 200), (maximum, 200)]:
                resp = self.client.get(
                    '/' + ep,
                    query_string = dict(offset = entry),
                    headers = self.headers
                    )
                self.assertEqual(resp.status_code, code)

    def test_fields_parameter(self):
        """Fields parameter behaves as expected."""
        for ep in self.endpoints:
            if '{id}' in ep or 'fields' not in self.endpoints[ep]['params']:
                continue
            fields = self.endpoints[ep]['params']['fields'].split(',')

            for n in range(1, len(fields)):
                for perm_fields in [fields[:n]]:
                    query_string = dict(
                        fields = ','.join(perm_fields),
                        limit = 1
                        )
                    resp = self.client.get(
                        '/' + ep,
                        query_string = query_string,
                        headers = self.headers
                        )
                    print 'Checking /' + ep + ' with ' + str(query_string)
                    parsed_fields = json.loads(resp.data)['matches'][0].keys()
                    sd = set(perm_fields).symmetric_difference(set(parsed_fields))
                    self.assertTrue(sd.issubset(['snippet']))


if __name__ == '__main__':
    unittest.main()
