import re
import string
import ipaddress

from . import utils


class RequestProtocol(object):
    METHOD_GET = 'GET'
    METHOD_OPTIONS = 'OPTIONS'
    METHOD_HEAD = 'HEAD'
    METHOD_POST = 'POST'
    METHOD_PUT = 'PUT'
    METHOD_DELETE = 'DELETE'
    METHOD_TRACE = 'TRACE'
    METHOD_CONNECT = 'CONNECT'

    HTTP_VERSION = '1.1'

    CRLF = '\r\n'
    SP = ' '

    REQUEST_LINE = '{method}{sp}{request_uri}{sp}HTTP/{http_version}{crlf}'

    @classmethod
    def path(cls, uri):
        path = uri.path
        if uri.query:
            path = '{}?{}'.format(path, uri.query)
        return path

    @classmethod
    def header_fields(cls, headers):
        return '\r\n'.join(
            '{}: {}'.format(h, v) for h, v in headers.items())

    @classmethod
    def request_line(cls, method, request_uri):
        return cls.REQUEST_LINE.format(
            method=method,
            sp=cls.SP,
            request_uri=request_uri,
            http_version=cls.HTTP_VERSION,
            crlf=cls.CRLF)


class ResponseProtocol(object):
    COLON = ':'
    HTTP = 'HTTP/'

    REGEX_CHARSET = re.compile(r';\s*charset=([^;]*)', re.I)
    REGEX_TOKEN = re.compile(
        r'([a-zA-Z][a-zA-Z_-]*)\s*(?:=(?:"([^"]*)"|'
        r'([^ \t",;]*)))?')

    @classmethod
    def parse_status(cls, status):
        if status.startswith(cls.HTTP):
            http_version, status_code, status_text = status.split(None, 2)
            status = '{} {}'.format(
                utils.smart_text(status_code),
                utils.smart_text(status_text))
        return status

    @classmethod
    def parse_status_code(cls, status):
        return int(status.split()[0])

    @classmethod
    def parse_charset(cls, header, charset):
        match = cls.REGEX_CHARSET.search(utils.smart_text(header))
        if match:
            charset = match.group(1)
        return charset

    @classmethod
    def parse_cache_control(cls, header):
        header = utils.smart_text(header)
        cache = {}
        for match in cls.REGEX_TOKEN.finditer(header):
            name = match.group(1)
            value = match.group(2) or match.group(3) or None
            if value and value.isdigit():
                value = int(value)
            cache[name] = value

        cache_control = {}
        for n in [
            'public',
            'no-store',
            'no-transform',
            'must-revalidate',
            'proxy-revalidate',
        ]:
            if n not in cache:
                continue
            cache_control[n] = None

        for n, v in cache.items():
            if n not in [
                'private',
                'no-cache',
                'max-age',
                's-maxage',
                'stale-while-revalidate',
                'stale-if-error',
            ]:
                continue
            cache_control[n] = v
        return cache_control


class URIProtocol(object):
    ALPHA = string.ascii_letters
    DIGIT = string.digits
    UNRESERVED = ALPHA + DIGIT + '-' '.' '_' '~'

    GEN_DELIMS = ':' '/' '?' '#' '[' ']' '@'
    SUB_DELIMS = '!' '$' '&' '\'' '(' ')' '*' '+' ',' ';' '='
    RESERVED = GEN_DELIMS + SUB_DELIMS

    PCT_ENCODED = '%' + string.hexdigits
    PCHAR = UNRESERVED + PCT_ENCODED + SUB_DELIMS + ':' + '@'

    # Parts
    SCHEME = ALPHA + DIGIT + '+' + '-' + '.'
    QUERY = PCHAR + '/' '?'
    FRAGMENT = PCHAR + '/' '?'

    # Authority
    USERINFO = UNRESERVED + PCT_ENCODED + SUB_DELIMS + ':'
    PORT = DIGIT

    # Host
    REG_NAME = UNRESERVED + PCT_ENCODED + SUB_DELIMS

    # Path
    SEGMENT = PCHAR
    SEGMENT_NZ_NC = UNRESERVED + PCT_ENCODED + SUB_DELIMS + '@'

    @classmethod
    def strip_scheme(cls, uri):
        if ':' not in uri:
            return None, uri

        scheme, hier_part = uri.split(':', 1)
        if scheme[0] not in cls.ALPHA:
            raise exc.SchemeException(uri)

        if any(c not in cls.SCHEME for c in scheme[1:]):
            raise exc.SchemeException(scheme)

        return scheme.lower(), hier_part

    @classmethod
    def strip_fragment(cls, hier_part):
        if '#' in hier_part:
            hier_part, fragment = \
                hier_part.rsplit('#', 1)
            if any(c not in cls.FRAGMENT for c in fragment):
                raise exc.FragmentException(fragment)
        else:
            fragment = None
        return fragment, hier_part

    @classmethod
    def strip_query(cls, hier_part):
        if '?' in hier_part:
            hier_part, query = hier_part.rsplit('?', 1)
            if any(c not in cls.QUERY for c in query):
                raise exc.QueryException(query)
        else:
            query = None
        return query, hier_part

    @classmethod
    def strip_authority(cls, hier_part):
        if hier_part.startswith('//'):
            hier_part = hier_part[2:]
        if '/' in hier_part:
            authority, hier_part = hier_part.split('/', 1)
            hier_part = '/{}'.format(hier_part)
        else:
            authority = hier_part
            hier_part = ''
        return authority, hier_part

    @classmethod
    def strip_userinfo(cls, authority):
        if '@' in authority:
            userinfo, authority = authority.split('@', 1)
            if any(c not in cls.USERINFO for c in userinfo):
                raise exc.UserInfoException(userinfo)
            if not userinfo:
                userinfo = None
        else:
            userinfo = None
        return userinfo, authority

    @classmethod
    def strip_port(cls, authority):
        if ':' in authority:
            authority, port = authority.rsplit(':', 1)
        else:
            return None, authority
        if port.isdigit():
            port = int(port)
        else:
            raise exc.PortException(port)
        return port, authority

    @classmethod
    def verify_reg_name(cls, host):
        return all(c in cls.REG_NAME for c in host)

    @classmethod
    def verify_ipv4_address(cls, host):
        if '.' not in host:
            return False

        try:
            ipaddress.IPv4Address(host)
        except ipaddress.AddressValueError:
            return False
        else:
            return True

    @classmethod
    def verify_ipv6_address(cls, host):
        if ':' not in host:
            return False

        try:
            ipaddress.IPv6Address(host)
        except ipaddress.AddressValueError:
            return False
        else:
            return True

    @classmethod
    def verify_path_abempty(cls, path):
        if not path:
            return True

        if not path.startswith('/'):
            return False

        segments = path.split('/')
        for segment in segments:
            if any(c not in cls.SEGMENT for c in segment):
                return False
        else:
            return True

    @classmethod
    def verify_path_absolute(cls, path):
        if not path.startswith('/'):
            return False

        segments = path.split('/')[1:]
        segment = segments[0]
        if not segment or any(c not in cls.SEGMENT for c in segment):
            return False

        for segment in segments[1:]:
            if any(c not in cls.SEGMENT for c in segment):
                return False
        else:
            return True

    @classmethod
    def verify_path_noscheme(cls, path):
        if path.startswith('/'):
            return False

        segments = path.split('/')
        segment = segments[0]
        if not segment or any(c not in cls.SEGMENT_NZ_NC for c in segment):
            return False

        for segment in segments[1:]:
            if any(c not in cls.SEGMENT for c in segment):
                return False
        else:
            return True

    @classmethod
    def verify_path_rootless(cls, path):
        if path.startswith('/'):
            return False

        segments = path.split('/')
        segment = segments[0]
        if not segment or any(c not in cls.SEGMENT for c in segment):
            return False

        for segment in segments[1:]:
            if any(c not in cls.SEGMENT for c in segment):
                return False
        else:
            return True

    @classmethod
    def verify_path_empty(cls, path):
        return bool(path)
