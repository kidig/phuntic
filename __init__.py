import json
import datetime
from decimal import Decimal
from pydoc import locate

LIST_TYPES = [list, set, frozenset, tuple]
FROZENDICT_ENABLED = False

try:
    from frozendict import frozendict
    LIST_TYPES += [frozendict]
    FROZENDICT_ENABLED = True
except ImportError:
    pass


class PyddingUnknownTypeError(TypeError):
    pass


class PyddingDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, o):
        print("debug:", o)
        if '_type' not in o:
            return o

        obj_type = o['_type']
        value = o.get('value', None)

        if obj_type == 'none':
            return None

        if obj_type in ('dict', 'list', 'str', 'int'):
            return value

        if obj_type in ('float', 'set', 'frozenset', 'tuple'):
            return locate(obj_type)(value)

        if obj_type == 'decimal':
            return Decimal(value)

        if obj_type == 'datetime':
            return datetime.datetime.utcfromtimestamp(value)

        if FROZENDICT_ENABLED and obj_type == 'frozendict':
            return frozendict(value)

        return o


def wrap_object(obj):
    if obj is None:
        obj = dict(_type='none')
    elif isinstance(obj, (str, int, float, bool)):
        obj = dict(_type=type(obj).__name__, value=obj)

    elif isinstance(obj, dict):
        obj = dict(_type='dict', value={k: wrap_object(v) for k, v in obj.items()})

    elif isinstance(obj, (list, set, frozenset, tuple)):
        obj = dict(_type=type(obj).__name__, value=[wrap_object(v) for v in obj])

    elif isinstance(obj, Decimal):
        obj = dict(_type='decimal', value=str(obj))

    elif isinstance(obj, datetime.datetime):
        obj = dict(_type='datetime', value=obj.replace(tzinfo=datetime.timezone.utc).timestamp())

    else:
        raise PyddingUnknownTypeError(repr(obj) + " is not pydding-like!")

    return obj


def dumps(obj, **kwargs):
    """Serialize ``obj`` to a JSON formatted ``str``"""
    return json.dumps(wrap_object(obj), **kwargs)


def loads(*args, **kwargs):
    """Deserialize ``s`` (a ``str`` instance containing a JSON document) to a Python object"""
    kwargs['cls'] = kwargs.pop('cls', PyddingDecoder)
    return json.loads(*args, **kwargs)