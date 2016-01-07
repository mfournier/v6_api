from c2corg_api.models.route import Route, RouteLocale
from c2corg_api.models.user import User
from c2corg_api.models.waypoint import Waypoint, WaypointLocale
from c2corg_api.views import set_best_locale
from colanderalchemy.schema import SQLAlchemySchemaNode
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
    )
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import relationship, joinedload, load_only
import datetime

from c2corg_api.models import Base, schema, users_schema, DBSession
from document import Document


class Association(Base):
    """Associations between documents.
    """
    __tablename__ = 'associations'

    parent_document_id = Column(
        Integer, ForeignKey(schema + '.documents.document_id'),
        nullable=False)
    parent_document = relationship(
        Document, primaryjoin=parent_document_id == Document.document_id)

    child_document_id = Column(
        Integer, ForeignKey(schema + '.documents.document_id'),
        nullable=False)
    child_document = relationship(
        Document, primaryjoin=child_document_id == Document.document_id)

    # TODO ?
    link_type = Column(String(2))

    __table_args__ = (
        PrimaryKeyConstraint(parent_document_id, child_document_id),
        Base.__table_args__
    )


class AssociationLog(Base):
    """Model to log when an association between documents was established or
    removed.
    """
    __tablename__ = 'association_log'

    id = Column(Integer, primary_key=True)

    parent_document_id = Column(
        Integer, ForeignKey(schema + '.documents.document_id'),
        nullable=False)
    parent_document = relationship(
        Document, primaryjoin=parent_document_id == Document.document_id)

    child_document_id = Column(
        Integer, ForeignKey(schema + '.documents.document_id'),
        nullable=False)
    child_document = relationship(
        Document, primaryjoin=child_document_id == Document.document_id)

    user_id = Column(
        Integer, ForeignKey(users_schema + '.user.id'), nullable=False)
    user = relationship(
        User, primaryjoin=user_id == User.id, viewonly=True)

    is_creation = Column(Boolean, default=True, nullable=False)
    written_at = Column(
        DateTime, default=datetime.datetime.now, nullable=False)

schema_association = SQLAlchemySchemaNode(
    Association,
    # whitelisted attributes
    includes=['parent_document_id', 'child_document_id'],
    overrides={})


def get_associations(document, lang):
    """Load and return associated documents.
    """
    def limit_waypoint_fields(query):
        return query.\
            options(load_only(
                Waypoint.waypoint_type, Waypoint.document_id,
                Waypoint.elevation, Waypoint.version)). \
            options(joinedload(Waypoint.locales).load_only(
                WaypointLocale.culture, WaypointLocale.title,
                WaypointLocale.version))

    parent_waypoints = limit_waypoint_fields(
        DBSession.query(Waypoint).
        join(Association,
             Association.parent_document_id == Waypoint.document_id).
        filter(Association.child_document_id == document.document_id)). \
        all()
    child_waypoints = limit_waypoint_fields(
        DBSession.query(Waypoint).
        join(Association,
             Association.child_document_id == Waypoint.document_id).
        filter(Association.parent_document_id == document.document_id)). \
        all()

    def limit_route_fields(query):
        return query.\
            options(load_only(
                Route.document_id, Route.activities, Route.elevation_min,
                Route.elevation_max, Route.version)). \
            options(joinedload(Waypoint.locales).load_only(
                RouteLocale.culture, RouteLocale.title, RouteLocale.version))

    parent_routes = limit_route_fields(
        DBSession.query(Route).
        join(Association,
             Association.parent_document_id == Route.document_id).
        filter(Association.child_document_id == document.document_id)). \
        all()
    child_routes = limit_route_fields(
        DBSession.query(Route).
        join(Association,
             Association.child_document_id == Route.document_id).
        filter(Association.parent_document_id == document.document_id)). \
        all()

    if lang is not None:
        set_best_locale(parent_waypoints, lang)
        set_best_locale(parent_routes, lang)
        set_best_locale(child_waypoints, lang)
        set_best_locale(child_routes, lang)

    return parent_waypoints + child_waypoints, parent_routes + child_routes
