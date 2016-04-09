from c2corg_api.models.topo_map import MAP_TYPE
from c2corg_api.search.mapping import SearchDocument, BaseMeta


class SearchTopoMap(SearchDocument):
    class Meta(BaseMeta):
        doc_type = MAP_TYPE