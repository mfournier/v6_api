import os
import sys
from elasticsearch_dsl import Index

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from c2corg_api.search.mapping import SearchDocument, analysis_settings
from c2corg_api.search import configure_es_from_config, elasticsearch_config


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    configure_es_from_config(settings)
    setup_es()


def setup_es():
    """Create the ElasticSearch index and configure the mapping.
    """
    client = elasticsearch_config['client']
    index_name = elasticsearch_config['index']

    info = client.info()
    print('ElasticSearch version: {0}'.format(info['version']['number']))

    if client.indices.exists(index_name):
        print('Index "{0}" already exists. To re-create the index, manually '
              'delete the index and run this script again.'.format(index_name))
        print ('To delete the index run:')
        print('curl -XDELETE \'http://{0}:{1}/{2}/\''.format(
            elasticsearch_config['host'], elasticsearch_config['port'],
            index_name))
        sys.exit(0)

    index = Index(index_name)
    index.settings(analysis=analysis_settings)
    index.doc_type(SearchDocument)
    index.create()

    print('Index "{0}" created'.format(index_name))


def drop_index(silent=True):
    """Remove the ElasticSearch index.
    """
    index = Index(elasticsearch_config['index'])
    try:
        index.delete()
    except Exception as exc:
        if not silent:
            raise exc
