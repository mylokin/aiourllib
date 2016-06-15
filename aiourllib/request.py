import collections

from . import rfc2369


class Request(object):
    HTTP_VERSION = 1.1

    def __init__(self, method, url):
        self.method = method
        self.url = rfc2369.URI(url)

        path = self.url.path
        if not path.endswith('/'):
            path = '{}/'.format(path)
        if self.url.query:
            path = '{}?{}'.format(path, self.url.query)
        self.path = path

        self.headers = collections.OrderedDict()

        host = self.url.hostname
        if self.url.scheme == 'https':
            host = '{}:443'.format(host)
        self.headers['Host'] = host

    @property
    def line(self):
        return '{method} {path} HTTP/{http_version}'.format(
            method=self.method.upper(),
            path=self.path,
            http_version=self.HTTP_VERSION)

    @property
    def header_fields(self):
        return '\r\n'.join('{}: {}'.format(h, v) for h, v in self.headers.items())

    def __str__(self):
        return (
            '{line}\r\n'
            '{header_fields}\r\n'
            '\r\n'.format(
                line=self.line,
                header_fields=self.header_fields))
