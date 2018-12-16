import os

import pytest
from dotenv.environ import UndefinedValueError, env
from dotenv.helpers import Csv


def test_env_str(monkeypatch):
    monkeypatch.setitem(os.environ, 'ENV1', 'myval')
    assert env("ENV1") == "myval"
    assert env.str("ENV1") == "myval"


def test_env_bool(monkeypatch):
    monkeypatch.setitem(os.environ, 'ENV1', 'true')
    monkeypatch.setitem(os.environ, 'ENV2', 'false')
    assert env("ENV1", cast=bool) is True
    assert env.bool("ENV1") is True
    assert env("ENV2", cast=bool) is False
    assert env.bool("ENV2") is False


def test_env_empty_string_means_false(monkeypatch):
    monkeypatch.setitem(os.environ, 'ENV1', '')
    assert False is env('ENV1', cast=bool)


def test_env_default_none():
    assert None is env('UndefinedKey', default=None)


def test_env_default_value(monkeypatch):
    if 'ENV1' in os.environ:
        del os.environ['ENV1']
    assert env("ENV1", "Hello") == "Hello"
    assert env("ENV1", 1) == 1
    assert env("ENV1", 1, cast=str) == '1'


def test_env_list(monkeypatch):
    monkeypatch.setitem(os.environ, 'ENV1', '1,2,3')
    assert env("ENV1", cast=list) == ['1', '2', '3']


def test_env_csv(monkeypatch):
    monkeypatch.setitem(os.environ, 'ENV1', '1,2,3')
    assert env("ENV1", cast=Csv(cast=int)) == [1, 2, 3]
    assert env.csv("ENV1", cast=int) == [1, 2, 3]


def test_env_undefined(monkeypatch):
    if 'ENV1' in os.environ:
        del os.environ['ENV1']

    with pytest.raises(UndefinedValueError):
        env("ENV1")


def test_csv():
    csv = Csv()
    assert ['127.0.0.1', '.localhost', '.herokuapp.com'] == \
        csv('127.0.0.1, .localhost, .herokuapp.com')

    csv = Csv(int)
    assert [1, 2, 3, 4, 5] == csv('1,2,3,4,5')

    csv = Csv(post_process=tuple)
    assert ('HTTP_X_FORWARDED_PROTO', 'https') == \
        csv('HTTP_X_FORWARDED_PROTO, https')

    csv = Csv(cast=lambda s: s.upper(), delimiter='\t', strip=' %*')
    assert ['VIRTUAL_ENV', 'IMPORTANT STUFF', 'TRAILING SPACES'] == \
        csv('%virtual_env%\t *important stuff*\t   trailing spaces   ')


def test_csv_quoted_parse():
    csv = Csv()

    assert ['foo', 'bar, baz', 'qux'] == csv(""" foo ,'bar, baz', 'qux'""")

    assert ['foo', 'bar, baz', 'qux'] == csv(''' foo ,"bar, baz", "qux"''')

    assert ['foo', "'bar, baz'", "'qux"] == csv(''' foo ,"'bar, baz'", "'qux"''')

    assert ['foo', '"bar, baz"', '"qux'] == csv(""" foo ,'"bar, baz"', '"qux'""")
