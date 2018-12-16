# -*- coding: utf-8 -*-
import os
import json
import string

from .helpers import Csv
from .compat import text_type


class UndefinedValueError(Exception):
    pass


class Undefined(object):
    """Class to represent undefined type. """
    pass


def _cast_boolean(value):
    """
    Helper to convert config values to boolean as ConfigParser do.
    """
    _BOOLEANS = {'1': True, 'yes': True, 'true': True, 'on': True,
                 '0': False, 'no': False, 'false': False, 'off': False, '': False}
    value = str(value)
    if value.lower() not in _BOOLEANS:
        raise ValueError('Not a boolean: %s' % value)

    return _BOOLEANS[value.lower()]


class Env():
    ENVIRON = os.environ
    NOTSET = Undefined()

    def __call__(self, var, default=NOTSET, cast=NOTSET):
        return self.get_value(var, default=default, cast=cast)

    def __contains__(self, var):
        return var in self.ENVIRON

    def get_value(self, var, default=NOTSET, cast=NOTSET):
        """
        Return the value for option or default if defined.
        """

        # We can't avoid __contains__ because value may be empty.
        try:
            value = self.ENVIRON[var]
        except KeyError:
            if isinstance(default, Undefined):
                error_msg = '{} not found. Declare it as envvar or define a default value.'.format(var)
                raise UndefinedValueError(error_msg)

            value = default

        if cast is self.NOTSET:
            return value

        if cast is bool:
            value = _cast_boolean(value)
        elif cast is list:
            value = [x for x in value.split(',') if x]
        else:
            value = cast(value)

        return value

    # shortcuts
    def int(self, var, default=NOTSET):
        return self.get_value(var, default, cast=int)

    def str(self, var, default=NOTSET):
        return self.get_value(var, default)

    def bool(self, var, default=NOTSET):
        return self.get_value(var, default, cast=bool)

    def float(self, var, default=NOTSET):
        return self.get_value(var, default, cast=float)

    def json(self, var, default=NOTSET):
        return self.get_value(var, default, cast=json.loads)

    def csv(self, var, default=NOTSET, cast=text_type, delimiter=',', strip=string.whitespace, post_process=list):
        return self.get_value(var, default, cast=Csv(cast, delimiter, strip, post_process))


env = Env()
