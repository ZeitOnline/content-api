# -*- coding: utf-8 -*-
"""
    zeit.api.parameters
    ~~~~~~~~~~~~~~~~~~~

    This module contains classes for various request parameters.
    They provide methods for validation and translation to Solr parameter
    namespace.

    Copyright: (c) 2013 by ZEIT ONLINE.
    License: BSD, see LICENSE.md for more details.
"""

import re

from . import exception, util


class Param(object):
    """The base class for all URL parameters."""

    key = None
    default = None
    origin = None

    def __init__(self, **kwargs):
        vkeys = list(k for k in kwargs.keys())
        vargs = dict((k, v) for k, v in kwargs.iteritems() if k in vkeys)
        self.__dict__.update(vargs)
        self._value = None

    @property
    def value(self):
        return self._value or self.default

    @value.setter
    def value(self, value):
        try:
            self.valid(value)
            self._value = value
        except AssertionError:
            raise exception.JSONBadRequest()

    def __repr__(self):
        return str(self.value)

    def valid(self, value):
        pass


class StrParam(Param):
    """The base class for string parameters."""

    default = ''

    def __init__(self, **kwargs):
        super(StrParam, self).__init__(**kwargs)

    def valid(self, value):
        super(StrParam, self).valid(value)
        assert isinstance(value, basestring)


class SqlQParam(StrParam):
    """A parameter class enforcing SQL syntax."""

    default = '%'
    key = 'q'

    def __init__(self, **kwargs):
        super(SqlQParam, self).__init__(**kwargs)

    def valid(self, value):
        super(SqlQParam, self).valid(value)
        assert len(value) < 1024

    @property
    def value(self):
        return self._value or self.default

    @value.setter
    def value(self, value):
        try:
            self.valid(value)
            self._value = value.replace('*', '%')
        except AssertionError:
            raise exception.JSONBadRequest()


class FacetFieldParam(StrParam):
    """A parameter class for field facetting."""

    default = ''
    origin = 'facet.field'
    key = 'facet_field'

    def __init__(self, **kwargs):
        super(FacetFieldParam, self).__init__(**kwargs)

    def valid(self, value):
        super(FacetFieldParam, self).valid(value)
        whitelist = [
            'department',
            'product',
            'sub_department',
            'keyword',
            'author',
            'series'
        ]
        assert value in whitelist


class FacetDateParam(StrParam):
    """A parameter class for date facetting."""

    default = ''
    origin = 'facet.date.gap'
    key = 'facet_date'

    def __init__(self, **kwargs):
        super(FacetDateParam, self).__init__(**kwargs)

    def valid(self, value):
        super(FacetDateParam, self).valid(value)
        assert(re.match(r"^[0-9]{1,3}(day|month|year)$", value))

    @property
    def value(self):
        return self._value or self.default

    @value.setter
    def value(self, value):
        try:
            self.valid(value)
            self._value = util.ensure_prefix(value, '+').upper()
        except AssertionError:
            raise exception.JSONBadRequest()


class IntParam(Param):
    """The base class for integer parameters."""

    default = '0'

    def __init__(self, **kwargs):
        super(IntParam, self).__init__(**kwargs)

    def __radd__(self, other):
        result = IntParam()
        result.value = str(int(self.value) + other)
        return result

    def valid(self, value):
        super(IntParam, self).valid(value)
        assert hasattr(value, 'isdigit') and value.isdigit()


class LimitParam(IntParam):
    """A class for limit parameters."""

    default = '10'
    origin = 'rows'
    key = 'limit'

    def __init__(self, **kwargs):
        super(LimitParam, self).__init__(**kwargs)

    def valid(self, value):
        super(LimitParam, self).valid(value)
        assert int(value) >= 0 and int(value) <= 1024


class OffsetParam(IntParam):
    """A class for offset parameters."""

    default = '0'
    origin = 'start'
    key = 'offset'

    def __init__(self, **kwargs):
        super(OffsetParam, self).__init__(**kwargs)

    def valid(self, value):
        super(OffsetParam, self).valid(value)


class CsvParam(StrParam):
    """The base class for comma seperated values."""

    def __init__(self, **kwargs):
        super(CsvParam, self).__init__(**kwargs)

    def __iter__(self):
        for item in self.value.split(','):
            if item != '' and item in self.default.split(','):
                yield item

    def valid(self, value):
        super(CsvParam, self).valid(value)
        assert all(item in self.default.split(',') for item in self)


class FieldsParam(CsvParam):
    """A class for parial selection parameters."""

    key = 'fields'
    origin = 'fl'
    enforce = ''

    def __init__(self, **kwargs):
        super(FieldsParam, self).__init__(**kwargs)

    def valid(self, value):
        super(FieldsParam, self).valid(value)

    @property
    def value(self):
        if not self._value:
            return self.default
        if self.enforce != '' and self.enforce not in self._value.split(','):
            return '%s,%s' % (self.enforce, self._value)
        else:
            return self._value

    @value.setter
    def value(self, value):
        try:
            self.valid(value)
            self._value = value if '*' not in value else self.default
        except AssertionError:
            raise exception.JSONBadRequest()
