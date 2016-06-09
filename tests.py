from . import dumps, loads, PyddingUnknownTypeError
import json
import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta


class MyTestClass:
    pass


def my_test_func():
    pass


class TestPydding:
    def assertJson(self, obj, json_obj):
        s = dumps(obj, sort_keys=True)
        assert s == json.dumps(json_obj, sort_keys=True)
        assert loads(s) == obj

    def test_none(self):
        s = dumps(None, sort_keys=True)
        assert s == json.dumps({"_type": "none"}, sort_keys=True)
        assert loads(s) is None

    def test_string(self):
        obj = 'test'
        self.assertJson(obj, {"_type": "str", "value": obj})

    def test_int(self):
        obj = 100500
        self.assertJson(obj, {"_type": "int", "value": obj})

    def test_float(self):
        obj = 3.1428
        self.assertJson(obj, {"_type": "float", "value": obj})

        obj = float(1)
        self.assertJson(obj, {"_type": "float", "value": obj})
        s = dumps(obj, sort_keys=True)
        assert isinstance(loads(s), float)

    def test_list(self):
        obj = []
        self.assertJson(obj, {"_type": "list", "value": []})

        obj = [1,2,3]
        expected = {
            "_type": "list",
            "value": [
                {"_type": "int", "value": 1},
                {"_type": "int", "value": 2},
                {"_type": "int", "value": 3},
            ]
        }
        self.assertJson(obj, expected)

    def test_set(self):
        obj = set()
        self.assertJson(obj, {"_type": "set", "value": []})

        obj = {1,2}
        expected = {
            "_type": "set",
            "value": [
                {"_type": "int", "value": 1},
                {"_type": "int", "value": 2},
            ]
        }
        self.assertJson(obj, expected)

    def test_frozenset(self):
        obj = frozenset()
        self.assertJson(obj, {"_type": "frozenset", "value": []})

        obj = frozenset([1,2])
        expected = {
            "_type": "frozenset",
            "value": [
                {"_type": "int", "value": 1},
                {"_type": "int", "value": 2}
            ]
        }
        self.assertJson(obj, expected)

    def test_tuple(self):
        obj = tuple()
        self.assertJson(obj, {"_type": "tuple", "value": obj})

        obj = ('test', 1, 1.12)
        expected = {
            "_type": "tuple",
            "value": [
                {"_type": "str", "value": "test"},
                {"_type": "int", "value": 1},
                {"_type": "float", "value": 1.12},
            ]
        }
        self.assertJson(obj, expected)

    def test_dict(self):
        obj = dict()
        self.assertJson(obj, {"_type": "dict", "value": {}})

        obj = {'one': 'test', 'two': 123}
        expected = {
            "_type": "dict",
            "value": {
                "one": {
                    "_type": "str",
                    "value": "test",
                },
                "two": {
                    "_type": "int",
                    "value": 123,
                }
            }
        }
        self.assertJson(obj, expected)

    def test_decimal(self):
        obj = Decimal('1.2342')
        self.assertJson(obj, {"_type": "decimal", "value": str(obj)})

    def test_datetime(self):
        obj = datetime.now()
        obj -= timedelta(microseconds=obj.microsecond)
        self.assertJson(obj, {"_type": "datetime", "value": obj.replace(tzinfo=timezone.utc).timestamp()})

    def test_class(self):
        obj = object()
        with pytest.raises(PyddingUnknownTypeError):
            s = dumps(obj)

    def test_custom_class(self):
        obj = MyTestClass()
        with pytest.raises(PyddingUnknownTypeError):
            s = dumps(obj)

    def test_func(self):
        obj = my_test_func
        with pytest.raises(PyddingUnknownTypeError):
            s = dumps(obj)
