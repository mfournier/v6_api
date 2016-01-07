import collections
import datetime

from c2corg_api.models import DBSession
from c2corg_common.attributes import cultures_priority
from colander import null
from pyramid.httpexceptions import HTTPError, HTTPNotFound
from pyramid.view import view_config
from cornice import Errors
from cornice.util import json_error, _JSONError
from cornice.resource import view
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
import json


cors_policy = dict(
    headers=('Content-Type'),
    origins=('*')
)


@view_config(context=HTTPNotFound)
@view_config(context=HTTPError)
def http_error_handler(exc, request):
    """In case of a HTTP error, return the error details as JSON, e.g.:

        {
            "status": "error",
            "errors": [
                {
                    "location": "request",
                    "name": "Not Found",
                    "description": "document not found"
                }
            ]
        }
    """
    if isinstance(exc, _JSONError):
        # if it is an error from Cornice, just return it
        return exc

    errors = Errors(request, exc.code)
    errors.add('request', exc.title, exc.detail)

    return json_error(errors)


def json_view(**kw):
    """ A Cornice view that expects 'application/json' as content-type.
    """
    kw['content_type'] = 'application/json'
    return view(**kw)


def restricted_json_view(**kw):
    """ A Cornice view that handles restricted json resources.
    """
    if 'permission' not in kw:
        kw['permission'] = 'authenticated'
    return json_view(**kw)


def restricted_view(**kw):
    """ A Cornice view that handles restricted resources.
    """
    if 'permission' not in kw:
        kw['permission'] = 'authenticated'
    return view(**kw)


def to_json_dict(obj, schema):
    obj_dict = serialize(schema.dictify(obj))

    # manually copy `available_cultures` and `associations` (it would be
    # cleaner to add the field to the schema, but ColanderAlchemy doesn't like
    # it because it's not a real column)
    if hasattr(obj, 'available_cultures'):
        obj_dict['available_cultures'] = getattr(obj, 'available_cultures')
    if hasattr(obj, 'associations'):
        obj_dict['associations'] = getattr(obj, 'associations')

    return obj_dict


def serialize(data):
    """
    Colanders `serialize` method is not intended for JSON serialization (it
    turns everything into a string and keeps colander.null).
    https://github.com/tisdall/cornice/blob/c18b873/cornice/schemas.py
    Returns the most agnostic version of specified data.
    (remove colander notions, datetimes in ISO, ...)
    """
    if isinstance(data, basestring):
        return unicode(data)
    if isinstance(data, collections.Mapping):
        return dict(map(serialize, data.iteritems()))
    if isinstance(data, collections.Iterable):
        return type(data)(map(serialize, data))
    if isinstance(data, (datetime.date, datetime.datetime)):
        return data.isoformat()
    if isinstance(data, WKBElement):
        geometry = to_shape(data)
        return json.dumps(mapping(geometry))
    if data is null:
        return None

    return data


def to_seconds(date):
    return int((date - datetime.datetime(1970, 1, 1)).total_seconds())


def set_best_locale(documents, preferred_lang):
    """Sets the "best" locale on the given documents. The "best" locale is
    the locale in the given "preferred language" if available. Otherwise
    it is the "most relevant" translation according to `cultures_priority`.
    """
    if preferred_lang is None:
        return

    for document in documents:
        # need to detach the document from the session, so that the
        # following change to `document.locales` is not persisted
        DBSession.expunge(document)

        if document.locales:
            available_locales = {
                locale.culture: locale for locale in document.locales}
            if preferred_lang in available_locales:
                document.locales = [available_locales[preferred_lang]]
            else:
                best_locale = next(
                    (available_locales[lang] for lang in cultures_priority
                        if lang in available_locales), None)
                if best_locale:
                    document.locales = [best_locale]
