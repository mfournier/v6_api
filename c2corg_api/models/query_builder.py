from c2corg_api.models import DBSession


def build_order_by(model, value, direction):
    # FIXME: the attribute is not necessarily on the model
    attr = getattr(model, value)
    return attr.asc() if direction == 'asc' else attr.desc()


def dict_to_query(dictionnary, model):
    query = DBSession.query(model)
    for key, value in dictionnary.items():
        if key == 'orderby':
            direction = dictionnary['order']
            criterion = build_order_by(model, value, direction)
            query = query.order_by(criterion)
        elif key == 'order':
            continue
        elif key == 'summits':
            ids = map(int, value.split('-'))
            query = query.filter(model.document_id.in_(ids))
        elif key == 'outings':
            continue
    return query
