from geoalchemy2 import WKBElement
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa
import re


def copy_attributes(obj_from, obj_to, attributes):
    """
    Copies the given attributes from `obj_from` to `obj_to` (shallow copy).
    """
    for attribute in attributes:
        if hasattr(obj_from, attribute):
            current_val = getattr(obj_to, attribute)
            new_val = getattr(obj_from, attribute)

            # To make the SQLAlchemy check if a document has changed work
            # properly, we only copy an attribute if the value has changed.
            # For geometries, we always copy the value.
            if isinstance(current_val, WKBElement) or \
                    isinstance(new_val, WKBElement) or \
                    current_val != new_val:
                setattr(obj_to, attribute, new_val)


class ArrayOfEnum(postgresql.ARRAY):
    """
    SQLAlchemy type for an array of enums.
    http://docs.sqlalchemy.org/en/latest/dialects/postgresql.html#postgresql-array-of-enum
    """

    def bind_expression(self, bindvalue):
        return sa.cast(bindvalue, self)

    def result_processor(self, dialect, coltype):
        super_rp = super(ArrayOfEnum, self).result_processor(
            dialect, coltype)

        def handle_raw_string(value):
            inner = re.match(r"^{(.*)}$", value).group(1)
            return inner.split(",")

        def process(value):
            if value is None:
                return None
            return super_rp(handle_raw_string(value))
        return process
