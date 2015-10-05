import urlparse


def rest_to_dict(url):
    split = urlparse.urlparse(url).path.split('/')[1:]
    values = {}
    for i in xrange(0, len(split), 2):
        values[split[i]] = split[i + 1]
    return values
