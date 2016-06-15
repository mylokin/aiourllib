import string
import unittest


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


class URI(object):
    SCHEME = Protocol.ALPHANUM + '+' '-' '.'
    USERINFO = (
        Protocol.UNRESERVED +
        Protocol.ESCAPED +
        ';' ':' '&' '=' '+' '$' ',')

    TOPLABEL = Protocol.ALPHANUM + '-'
    SEGMENT = Protocol.PCHAR + ';'
    REL_SEGMENT = (
        Protocol.UNRESERVED +
        Protocol.ESCAPED +
        ';' '@' '&' '=' '+' '$' ',')

    def __init__(self, uri):
        self.scheme, scheme_specific_part = self.process_scheme(uri)

        self.fragment, scheme_specific_part = \
            self.process_fragment(scheme_specific_part)

        self.authority = self.hostport = self.host = None
        self.userinfo = None
        self.port = None
        self.ipv6_address = self.ipv4_address = None
        self.toplabel = self.domainlabels = self.hostname = None
        self.abs_path = self.rel_segment = self.segments = None
        self.query = None

        self.opaque_part = None
        if self.scheme:
            if scheme_specific_part.startswith('//'):
                # hier_part(net_path)
                self.handle_net_path(scheme_specific_part)
            elif scheme_specific_part.startswith('/'):
                # hier_part(abs_path)
                self.handle_abs_path(scheme_specific_part)
            elif scheme_specific_part[0] in Protocol.URIC_NO_SLASH:
                # opaque_part
                self.handle_opaque_part(scheme_specific_part)
            else:
                raise URIException(uri)
        else:
            if scheme_specific_part.startswith('//'):
                # net_path
                self.handle_net_path(scheme_specific_part)
            elif scheme_specific_part.startswith('/'):
                # abs_path
                self.handle_abs_path(scheme_specific_part)
            else:
                # rel_path
                self.handle_rel_path(scheme_specific_part)

    def handle_rel_path(self, scheme_specific_part):
        self.query, scheme_specific_part = \
            self.process_query(scheme_specific_part)

        self.rel_segment, scheme_specific_part = \
            self.process_rel_segment(scheme_specific_part)

        if scheme_specific_part:
            self.abs_path = self.parse_abs_path(scheme_specific_part)
            self.segments = self.parse_segments(self.abs_path)
        else:
            self.abs_path = '/'
            self.segments = None

    def handle_net_path(self, scheme_specific_part):
        scheme_specific_part = self.process_net_path(scheme_specific_part)
        authority, scheme_specific_part = \
            self.process_authority(scheme_specific_part)
        self.userinfo, authority = self.process_userinfo(authority)
        self.host, self.port = self.parse_host_port(authority)

        if self.host.startswith('[') and self.host.endswith(']'):
            # ipv6
            raise NotImplementedError(self.host)
        elif self.host.replace('.', '').isdigit():
            self.ipv4_address = self.parse_ipv4_address(self.host)
        elif self.host:
            self.toplabel = self.parse_toplabel(self.host)
            self.domainlabels = self.parse_domainlabels(self.host)
            self.hostname = self.host

        self.hostport = self.host

        if self.port:
            self.hostport = '{}:{}'.format(self.hostport, self.port)

        self.authority = self.hostport

        if self.userinfo:
            self.authority = '{}@{}'.format(self.userinfo, self.authority)

        self.query, scheme_specific_part = \
            self.process_query(scheme_specific_part)

        if scheme_specific_part:
            self.abs_path = self.parse_abs_path(scheme_specific_part)
            self.segments = self.parse_segments(self.abs_path)
        else:
            self.abs_path = '/'
            self.segments = None

        return scheme_specific_part

    def handle_abs_path(self, scheme_specific_part):
        self.query, scheme_specific_part = \
            self.process_query(scheme_specific_part)

        if scheme_specific_part:
            self.abs_path = self.parse_abs_path(scheme_specific_part)
            self.segments = self.parse_segments(self.abs_path)
        else:
            self.abs_path = '/'
            self.segments = None

        return scheme_specific_part

    def handle_opaque_part(self, scheme_specific_part):
        self.opaque_part, scheme_specific_part = \
            self.process_opaque_part(scheme_specific_part)
        return scheme_specific_part

    @classmethod
    def process_opaque_part(cls, scheme_specific_part):
        if any(c not in Protocol.URIC for c in scheme_specific_part[1:]):
            raise URIException(scheme_specific_part)
        return scheme_specific_part, ''

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
    def parse_rel_path(cls, scheme_specific_part):
        rel_path = scheme_specific_part
        if not rel_path:
            raise PathSegmentException(rel_path)

        if any(c not in cls.REL_SEGMENT for c in rel_path):
            raise PathSegmentException(rel_path)

        return rel_path

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


class TestURI(unittest.TestCase):
    def assertMatch(self, uri):
        self.assertEqual(str(URI(uri)), uri)

    def test_net_path(self):
        self.assertMatch('http://a/b/c/d;p?q')

    def test_ending_slash(self):
        self.assertMatch('http://a/b/c/g/')

    def test_no_ending_slash(self):
        self.assertMatch('http://a/b/c/g')

    def test_file_scheme(self):
        self.assertMatch('file:///tmp/test.py')

    def test_extended_scheme(self):
        self.assertMatch('tmp+fdf:///d/test.py?fasdfs')

    def test_no_scheme(self):
        self.assertMatch('/tmp/test.py')

    def test_authority(self):
        source = 'mongo://a:b@c:1/d/e'
        self.assertMatch(source)

    def test_authority_value(self):
        uri = URI('mongo://a:b@c:1/d/e')
        self.assertEqual(uri.authority, 'a:b@c:1')

    def test_rel_segment(self):
        self.assertMatch('a/b/c/')

    def test_rel_segment_value(self):
        self.assertEqual(URI('a/b/c/').rel_segment, 'a')

    def test_fail_only_query(self):
        with self.assertRaises(RelSegmentException):
            URI('?a')


if __name__ == '__main__':
    unittest.main()
