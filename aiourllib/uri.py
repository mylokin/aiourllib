''' rfc 3986 implementation '''
import string

__all__ = [
    'URI',
    'URIFabric',
    'URIException',
]


class URIException(Exception):
    pass


class SchemeException(URIException):
    pass


class UserInfoException(URIException):
    pass


class PortException(URIException):
    pass


class AuthorityException(URIException):
    pass


class FragmentException(URIException):
    pass


class QueryException(URIException):
    pass


class PathSegmentException(URIException):
    pass


class RelSegmentException(URIException):
    pass


class Protocol(object):
    LOWALPHA = string.ascii_lowercase
    UPALPHA = string.ascii_uppercase
    ALPHA = LOWALPHA + UPALPHA

    DIGIT = string.digits
    ALPHANUM = ALPHA + DIGIT

    MARK = '-' '_' '.' '!' '~' '*' '\'' '(' ')'

    UNRESERVED = ALPHANUM + MARK

    HEX = string.hexdigits
    ESCAPED = '%' + HEX

    RESERVED = ';' '/' '?' ':' '@' '&' '=' '+' '$' ',' '[' ']'

    URIC = RESERVED + UNRESERVED + ESCAPED
    URIC_NO_SLASH = UNRESERVED + ESCAPED + ';' '?' ':' '@' '&' '=' '+' '$' ','

    DELIMS = '<' '>' '#' '%' '"'
    UNWISE = '{' '}' '|' '\\' '^' '`'

    PCHAR = UNRESERVED + ESCAPED + ':' '@' '&' '=' '+' '$' ','

    SCHEME = ALPHANUM + '+' '-' '.'
    USERINFO = (
        UNRESERVED +
        ESCAPED +
        ';' ':' '&' '=' '+' '$' ',')

    TOPLABEL = ALPHANUM + '-'
    SEGMENT = PCHAR + ';'
    REL_SEGMENT = (
        UNRESERVED +
        ESCAPED +
        ';' '@' '&' '=' '+' '$' ',')

    @classmethod
    def process_opaque_part(cls, scheme_specific_part):
        if any(c not in cls.URIC for c in scheme_specific_part[1:]):
            raise URIException(scheme_specific_part)
        return scheme_specific_part

    @classmethod
    def process_net_path(cls, scheme_specific_part):
        return scheme_specific_part[2:]

    @classmethod
    def process_authority(cls, scheme_specific_part):
        if '/' in scheme_specific_part:
            authority, scheme_specific_part = \
                scheme_specific_part.split('/', 1)
        else:
            authority = scheme_specific_part
            scheme_specific_part = ''
        return authority, scheme_specific_part

    @classmethod
    def process_userinfo(cls, authority):
        if '@' in authority:
            userinfo, authority = authority.split('@', 1)
            if any(c not in cls.USERINFO for c in userinfo):
                raise UserInfoException(userinfo)
            if not userinfo:
                userinfo = None
        else:
            userinfo = None
        return userinfo, authority

    @classmethod
    def process_rel_segment(cls, scheme_specific_part):
        if not scheme_specific_part:
            raise RelSegmentException(scheme_specific_part)

        if '/' in scheme_specific_part:
            rel_segment, scheme_specific_part = \
                scheme_specific_part.split('/', 1)
        else:
            rel_segment = scheme_specific_part
            scheme_specific_part = ''
            return scheme_specific_part, ''

        if not rel_segment:
            raise RelSegmentException(rel_segment)

        if any(c not in cls.REL_SEGMENT for c in rel_segment):
            raise RelSegmentException(rel_segment)

        return rel_segment, scheme_specific_part

    @classmethod
    def parse_host_port(cls, authority):
        if ':' in authority:
            host, port = authority.rsplit(':', 1)
            if port.isdigit():
                port = int(port)
            else:
                raise PortException(port)
        else:
            host = authority
            port = None
        return host, port

    @classmethod
    def parse_ipv4_address(cls, host):
        host = host.split('.')
        ipv4 = all(n and n.isdigit() and int(n) <= 255 for n in host)
        if len(host) == 4 and ipv4:
            host = '.'.join(host)
        else:
            raise AuthorityException('.'.join(host))
        return host

    @classmethod
    def parse_toplabel(cls, host):
        host = host.split('.')

        toplabel = host[-1]
        if toplabel.endswith('.'):
            toplabel = toplabel[:-1]
        if not toplabel:
            raise AuthorityException('.'.join(host))
        if not (toplabel[0] in Protocol.ALPHA):
            raise AuthorityException(toplabel)
        if not (toplabel[-1] in Protocol.ALPHANUM):
            raise AuthorityException(toplabel)
        if any(c not in cls.TOPLABEL for c in toplabel[1:-1]):
            raise AuthorityException(toplabel)

        return toplabel

    @classmethod
    def parse_domainlabels(cls, host):
        host = host.split('.')

        domainlabels = host[:-1]
        for domainlabel in domainlabels:
            if not domainlabel:
                raise AuthorityException('.'.join(host))
            if not (domainlabel[0] in Protocol.ALPHANUM):
                raise AuthorityException(domainlabel)
            if not (domainlabel[-1] in Protocol.ALPHANUM):
                raise AuthorityException(domainlabel)
            if any(c not in cls.TOPLABEL for c in domainlabel[1:-1]):
                raise AuthorityException(domainlabel)

        return domainlabels

    @classmethod
    def process_scheme(cls, uri):
        if ':' not in uri:
            return None, uri

        scheme, scheme_specific_part = uri.split(':', 1)
        if scheme[0] not in Protocol.ALPHA:
            raise SchemeException(uri)

        if any(c not in cls.SCHEME for c in scheme[1:]):
            raise SchemeException(scheme)

        return scheme.lower(), scheme_specific_part

    @classmethod
    def process_fragment(cls, scheme_specific_part):
        if '#' in scheme_specific_part:
            scheme_specific_part, fragment = \
                scheme_specific_part.rsplit('#', 1)
            if any(c not in Protocol.URIC for c in fragment):
                raise FragmentException(fragment)
        else:
            fragment = None
        return fragment, scheme_specific_part

    @classmethod
    def process_query(cls, scheme_specific_part):
        if '?' in scheme_specific_part:
            scheme_specific_part, query = scheme_specific_part.rsplit('?', 1)
            if any(c not in Protocol.URIC for c in query):
                raise QueryException(query)
        else:
            query = None
        return query, scheme_specific_part

    @classmethod
    def parse_abs_path(cls, scheme_specific_part):
        abs_path = scheme_specific_part or '/'
        if not abs_path.startswith('/'):
            abs_path = '/{}'.format(abs_path)
        return abs_path

    @classmethod
    def parse_segments(cls, abs_path):
        segments = abs_path.strip('/').split('/')
        for segment in segments:
            if not segment:
                continue
            if segment[0] not in Protocol.PCHAR:
                raise PathSegmentException(segment)
            if any(c not in cls.SEGMENT for c in segment):
                raise PathSegmentException(segment)
        return segments

    @classmethod
    def parse_authority(cls, authority):
        data = {}
        data['userinfo'], authority = cls.process_userinfo(authority)
        data['host'], data['port'] = cls.parse_host_port(authority)
        return data

    @classmethod
    def provide_rel_path(cls, scheme_specific_part):
        data = {}
        data['query'], scheme_specific_part = \
            cls.process_query(scheme_specific_part)

        data['rel_segment'], scheme_specific_part = \
            cls.process_rel_segment(scheme_specific_part)

        if scheme_specific_part:
            data['abs_path'] = cls.parse_abs_path(scheme_specific_part)
        else:
            data['abs_path'] = '/'
        return data

    @classmethod
    def provide_net_path(cls, scheme_specific_part):
        data = {}
        scheme_specific_part = \
            cls.process_net_path(scheme_specific_part)
        data['authority'], scheme_specific_part = \
            cls.process_authority(scheme_specific_part)

        data.update(cls.parse_authority(data['authority']))
        data['query'], scheme_specific_part = \
            cls.process_query(scheme_specific_part)

        if scheme_specific_part:
            data['abs_path'] = cls.parse_abs_path(scheme_specific_part)
        else:
            data['abs_path'] = '/'
        return data

    @classmethod
    def provide_abs_path(cls, scheme_specific_part):
        data = {}
        data['query'], scheme_specific_part = \
            cls.process_query(scheme_specific_part)

        if scheme_specific_part:
            data['abs_path'] = cls.parse_abs_path(scheme_specific_part)
        else:
            data['abs_path'] = '/'
        return data

    @classmethod
    def provide_opaque_part(cls, scheme_specific_part):
        data = {}
        data['opaque_part'] = cls.process_opaque_part(scheme_specific_part)
        return data


class URIFabric(object):
    PROTOCOL = Protocol

    FIELDS_NET_PATH = ('scheme', 'fragment', 'authority', 'abs_path', 'query')
    FIELDS_ABS_PATH = ('scheme', 'fragment', 'abs_path', 'query')
    FIELDS_REL_PATH = ('fragment', 'abs_path', 'rel_segment', 'query')
    FIELDS_OPAQUE_PART = ('scheme', 'fragment', 'opaque_part')

    @classmethod
    def from_string(cls, source):
        data = {}
        data['scheme'], scheme_specific_part = \
            cls.PROTOCOL.process_scheme(source)
        data['fragment'], scheme_specific_part = \
            cls.PROTOCOL.process_fragment(scheme_specific_part)

        if data['scheme']:
            if scheme_specific_part.startswith('//'):
                # hier_part(net_path)
                data.update(
                    cls.PROTOCOL.provide_net_path(scheme_specific_part))
                fields = cls.FIELDS_NET_PATH
            elif scheme_specific_part.startswith('/'):
                # hier_part(abs_path)
                data.update(
                    cls.PROTOCOL.provide_abs_path(scheme_specific_part))
                fields = cls.FIELDS_ABS_PATH
            elif scheme_specific_part[0] in Protocol.URIC_NO_SLASH:
                # opaque_part
                data.update(
                    cls.PROTOCOL.provide_opaque_part(scheme_specific_part))
                fields = cls.FIELDS_OPAQUE_PART
            else:
                raise URIException(source)
        else:
            if scheme_specific_part.startswith('//'):
                # net_path
                data.update(
                    cls.PROTOCOL.provide_net_path(scheme_specific_part))
                fields = cls.FIELDS_NET_PATH
            elif scheme_specific_part.startswith('/'):
                # abs_path
                data.update(
                    cls.PROTOCOL.provide_abs_path(scheme_specific_part))
                fields = cls.FIELDS_ABS_PATH
            else:
                # rel_path
                data.update(
                    cls.PROTOCOL.provide_rel_path(scheme_specific_part))
                fields = cls.FIELDS_REL_PATH

        return URI(**{f: data[f] for f in fields})


class URI(object):
    __slots__ = [
        'scheme',
        'authority',
        'abs_path',
        'rel_segment',
        'query',
        'fragment',
        'opaque_part',

        'host',
        'port',
        'userinfo',
        'ipv4_address',
        'ipv6_address',
        'hostport',
        'hostname',
        'toplabel',
        'domainlabels',
        'segments',
    ]
    PROTOCOL = Protocol

    def __init__(
        self,
        scheme=None,
        authority=None,
        abs_path=None,
        rel_segment=None,
        query=None,
        fragment=None,
        opaque_part=None,
    ):
        self.scheme = scheme
        self.authority = authority
        self.abs_path = abs_path
        self.rel_segment = rel_segment
        self.query = query
        self.fragment = fragment
        self.opaque_part = opaque_part

        self.host = None
        self.port = None
        self.userinfo = None

        self.ipv4_address = None
        self.ipv6_address = None

        self.hostport = None
        self.hostname = None

        self.toplabel = None
        self.domainlabels = None

        self.segments = None
        if self.abs_path:
            self.PROTOCOL.parse_segments(self.abs_path)

        if self.authority:
            data = self.PROTOCOL.parse_authority(self.authority)
            self.host = self.hostport = data['host']
            self.port = data['port']
            self.userinfo = data['userinfo']

            if self.host.startswith('[') and self.host.endswith(']'):
                # ipv6
                raise NotImplementedError(self.host)
            elif self.host.replace('.', '').isdigit():
                self.ipv4_address = \
                    self.PROTOCOL.parse_ipv4_address(self.host)
            elif self.host:
                self.hostname = self.host
                self.toplabel = self.PROTOCOL.parse_toplabel(self.hostname)
                self.domainlabels = \
                    self.PROTOCOL.parse_domainlabels(self.hostname)

            if self.port:
                self.hostport = '{}:{}'.format(self.hostport, self.port)

    def __str__(self):
        if self.scheme:
            result = '{}://'.format(self.scheme)
            if self.authority:
                result = '{}{}'.format(result, self.authority)
            result = '{}{}'.format(result, self.abs_path or self.opaque_part)
            if self.query:
                result = '{}?{}'.format(result, self.query)
            if self.fragment:
                result = '{}#{}'.format(result, self.fragment)
        else:
            result = '{}{}'.format(self.rel_segment or '', self.abs_path)
            if self.query:
                result = '{}?{}'.format(result, self.query)
            if self.fragment:
                result = '{}#{}'.format(result, self.fragment)
        return result
