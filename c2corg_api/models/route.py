from c2corg_api.models.schema_utils import restrict_schema
from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    SmallInteger,
    String,
    ForeignKey
    )

from colanderalchemy import SQLAlchemySchemaNode
import colander

from c2corg_api.models import schema
from c2corg_api.models.utils import ArrayOfEnum
from utils import copy_attributes
from document import (
    ArchiveDocument, Document, DocumentLocale, ArchiveDocumentLocale,
    get_update_schema, geometry_schema_overrides, schema_locale_attributes,
    schema_attributes)
from c2corg_api.models import enums

ROUTE_TYPE = 'r'


class _RouteMixin(object):

    __mapper_args__ = {
        'polymorphic_identity': ROUTE_TYPE
    }

    # activite
    activities = Column(ArrayOfEnum(enums.activity_type), nullable=False)

    # altitude min.
    elevation_min = Column(SmallInteger)

    # altitude max.
    elevation_max = Column(SmallInteger)

    # denivele positif du troncon dans le sens aller
    height_diff_up = Column(SmallInteger)

    # denivele negatif du troncon dans le sens aller
    height_diff_down = Column(SmallInteger)

    # longueur du troncon
    route_length = Column(Integer)

    # altitude du debut des difficultes
    difficulties_height = Column(SmallInteger)

    # denivele de l'approche
    height_diff_access = Column(SmallInteger)

    # Denivele des difficultes
    height_diff_difficulties = Column(SmallInteger)

    # type d'itineraire (aller-retour, boucle, ...)
    route_types = Column(ArrayOfEnum(enums.route_type))

    # orientations
    orientations = Column(ArrayOfEnum(enums.orientation_type))

    # temps de parcours total
    durations = Column(ArrayOfEnum(enums.route_duration_type))

    # crampons et materiel de securite sur glacier
    glacier_gear = Column(enums.glacier_gear_type)

    # configuration
    configuration = Column(ArrayOfEnum(enums.route_configuration_type))

    # approche par remontee mecanique possible
    lift_access = Column(Boolean)

    # cotation technique ski
    ski_rating = Column(enums.ski_rating)

    # exposition ski
    ski_exposition = Column(enums.exposition_rating)

    # cotation ponctuelle ski
    labande_ski_rating = Column(enums.labande_ski_rating)

    # cotation globale ski
    labande_global_rating = Column(enums.global_rating)

    # cotation globale
    global_rating = Column(enums.global_rating)

    # engagement
    engagement_rating = Column(enums.engagement_rating)

    # risques objectifs
    risk_rating = Column(enums.risk_rating)

    # qualite de l'equipement en place
    equipment_rating = Column(enums.equipment_rating)

    # cotation glace
    ice_rating = Column(enums.ice_rating)

    # cotation mixte
    mixed_rating = Column(enums.mixed_rating)

    # exposition rocher
    exposition_rock_rating = Column(enums.exposition_rock_rating)

    # cotation libre FR
    rock_free_rating = Column(enums.climbing_rating)

    # cotation obligatoire FR
    rock_required_rating = Column(enums.climbing_rating)

    # cotation escalade artificielle obligatoire
    aid_rating = Column(enums.aid_rating)

    # cotation via ferrata
    via_ferrata_rating = Column(enums.via_ferrata_rating)

    # cotation randonee
    hiking_rating = Column(enums.hiking_rating)

    # Exposition randonnee et VTT
    hiking_mtb_exposition = Column(enums.exposition_rating)

    # cotation raquette
    snowshoe_rating = Column(enums.snowshoe_rating)

    # cotation VTT (montee)
    mtb_up_rating = Column(enums.mtb_up_rating)

    # cotation VTT (descente)
    mtb_down_rating = Column(enums.mtb_down_rating)

    # longueur de bitume
    mtb_length_asphalt = Column(Integer)

    # longueur de piste
    mtb_length_trail = Column(Integer)

    # denivele de portage ou poussage
    mtb_height_diff_portages = Column(Integer)

    # type de rocher
    rock_types = Column(ArrayOfEnum(enums.rock_type))

    # type de voie
    climbing_outdoor_types = Column(enums.climbing_outdoor_type)


attributes = [
    'activities', 'elevation_min', 'elevation_max',
    'height_diff_up', 'height_diff_down', 'route_length',
    'difficulties_height', 'height_diff_access', 'height_diff_difficulties',
    'route_types', 'orientation', 'duration', 'glacier_gear', 'configuration',
    'lift_access', 'ski_rating', 'ski_exposition', 'labande_ski_rating',
    'labande_global_rating', 'global_rating', 'engagement_rating',
    'risk_rating', 'equipment_rating', 'ice_rating', 'mixed_rating',
    'exposition_rock_rating', 'rock_free_rating', 'rock_required_rating',
    'aid_rating', 'via_ferrata_rating', 'hiking_rating',
    'hiking_mtb_exposition', 'snowshoe_rating', 'mtb_up_rating',
    'mtb_down_rating', 'mtb_length_asphalt', 'mtb_length_trail',
    'mtb_height_diff_portages', 'rock_types', 'climbing_outdoor_types']


class Route(_RouteMixin, Document):
    """
    """
    __tablename__ = 'routes'

    document_id = Column(
        Integer,
        ForeignKey(schema + '.documents.document_id'), primary_key=True)

    def to_archive(self):
        route = ArchiveRoute()
        super(Route, self)._to_archive(route)
        copy_attributes(self, route, attributes)

        return route

    def update(self, other):
        super(Route, self).update(other)
        copy_attributes(other, self, attributes)


class ArchiveRoute(_RouteMixin, ArchiveDocument):
    """
    """
    __tablename__ = 'routes_archives'

    id = Column(
        Integer,
        ForeignKey(schema + '.documents_archives.id'), primary_key=True)


class _RouteLocaleMixin(object):

    __mapper_args__ = {
        'polymorphic_identity': ROUTE_TYPE
    }

    # pente
    slope = Column(String)

    # remarques
    remarks = Column(String)

    # materiel specifique
    gear = Column(String)

    # bibliographie et webographie
    external_resources = Column(String)

    # historique de l'itineraire
    route_history = Column(String)


attributes_locales = [
    'slope', 'remarks', 'gear', 'external_resources', 'route_history'
]


class RouteLocale(_RouteLocaleMixin, DocumentLocale):
    """
    """
    __tablename__ = 'routes_locales'

    id = Column(
                Integer,
                ForeignKey(schema + '.documents_locales.id'), primary_key=True)

    def to_archive(self):
        locale = ArchiveRouteLocale()
        super(RouteLocale, self).to_archive(locale)
        copy_attributes(self, locale, attributes_locales)

        return locale

    def update(self, other):
        super(RouteLocale, self).update(other)
        copy_attributes(other, self, attributes_locales)


class ArchiveRouteLocale(_RouteLocaleMixin, ArchiveDocumentLocale):
    """
    """
    __tablename__ = 'routes_locales_archives'

    id = Column(
        Integer,
        ForeignKey(schema + '.documents_locales_archives.id'),
        primary_key=True)


schema_route_locale = SQLAlchemySchemaNode(
    RouteLocale,
    # whitelisted attributes
    includes=schema_locale_attributes + attributes_locales,
    overrides={
        'version': {
            'missing': None
        }
    })

schema_route = SQLAlchemySchemaNode(
    Route,
    # whitelisted attributes
    includes=schema_attributes + attributes,
    overrides={
        'document_id': {
            'missing': None
        },
        'version': {
            'missing': None
        },
        'locales': {
            'children': [schema_route_locale]
        },
        'activities': {
            'validator': colander.Length(min=1)
        },
        'geometry': geometry_schema_overrides
    })

schema_update_route = get_update_schema(schema_route)
schema_association_route = restrict_schema(schema_route, [
    'locales.title', 'elevation_min', 'elevation_max', 'activities'
])
