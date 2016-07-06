import collections
import string
import ipaddress

URI = collections.namedtuple('URI', [
    'scheme',
    'authority',
    'path',
    'query',
    'fragment',
    'components',
])

URIComponents = collections.namedtuple('URIComponents', [
    'userinfo',
    'port',
    'host',
    'ipv6_address',
    'ipv4_address',
    'reg_name',
    'path_abempty',
    'path_absolute',
    'path_rootless',
    'path_empty',
    'relative_ref',
])


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


class PathException(URIException):
    pass


class Protocol(object):
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
            raise SchemeException(uri)

        if any(c not in cls.SCHEME for c in scheme[1:]):
            raise SchemeException(scheme)

        return scheme.lower(), hier_part

    @classmethod
    def strip_fragment(cls, hier_part):
        if '#' in hier_part:
            hier_part, fragment = \
                hier_part.rsplit('#', 1)
            if any(c not in Protocol.FRAGMENT for c in fragment):
                raise FragmentException(fragment)
        else:
            fragment = None
        return fragment, hier_part

    @classmethod
    def strip_query(cls, hier_part):
        if '?' in hier_part:
            hier_part, query = hier_part.rsplit('?', 1)
            if any(c not in Protocol.QUERY for c in query):
                raise QueryException(query)
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
                raise UserInfoException(userinfo)
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
            raise PortException(port)
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


def from_string(uri_reference):
    uri = {
        'scheme': None,
        'authority': None,
        'path': None,
        'query': None,
        'fragment': None,
        'components': None,
    }
    components = {
        'userinfo': None,
        'port': None,
        'host': None,
        'ipv6_address': None,
        'ipv4_address': None,
        'reg_name': None,
        'path_abempty': None,
        'path_absolute': None,
        'path_rootless': None,
        'path_empty': None,
        'relative_ref': None,
    }

    uri['scheme'], hier_part = Protocol.strip_scheme(uri_reference)
    uri['fragment'], hier_part = Protocol.strip_fragment(hier_part)
    uri['query'], hier_part = Protocol.strip_query(hier_part)
    if uri['scheme']:
        # hier_part
        if hier_part.startswith('//'):
            # authority
            authority, hier_part = Protocol.strip_authority(hier_part)
            uri['authority'] = authority
            components['userinfo'], authority = \
                Protocol.strip_userinfo(authority)
            components['port'], authority = \
                Protocol.strip_port(authority)
            host = components['host'] = authority
            if Protocol.verify_ipv6_address(host):
                components['ipv6_address'] = host
            elif Protocol.verify_ipv4_address(host):
                components['ipv4_address'] = host
            elif Protocol.verify_reg_name(host):
                components['reg_name'] = host
            else:
                raise AuthorityException(host)

            if Protocol.verify_path_abempty(hier_part):
                uri['path'] = components['path_abempty'] = hier_part
            else:
                raise PathException(hier_part)

        elif Protocol.verify_path_absolute(hier_part):
            uri['path'] = components['path_absolute'] = hier_part
        elif Protocol.verify_path_rootless(hier_part):
            uri['path'] = components['path_rootless'] = hier_part
        elif Protocol.verify_path_empty(hier_part):
            uri['path'] = components['path_empty'] = hier_part
        else:
            raise PathException(hier_part)

    else:
        # relative_ref
        relative_ref = components['relative_ref'] = hier_part
        if relative_ref.startswith('//'):
            # authority
            authority, relative_ref = Protocol.strip_authority(relative_ref)
            uri['authority'] = authority
            components['userinfo'], authority = \
                Protocol.strip_userinfo(authority)
            components['port'], authority = \
                Protocol.strip_port(authority)
            host = components['host'] = authority
            if Protocol.verify_ipv6_address(host):
                components['ipv6_address'] = host
            elif Protocol.verify_ipv4_address(host):
                components['ipv4_address'] = host
            elif Protocol.verify_reg_name(host):
                components['reg_name'] = host
            else:
                raise AuthorityException(host)

            if Protocol.verify_path_abempty(relative_ref):
                uri['path'] = components['path_abempty'] = relative_ref
            else:
                raise PathException(relative_ref)

        elif Protocol.verify_path_absolute(relative_ref):
            uri['path'] = components['path_absolute'] = relative_ref
        elif Protocol.verify_path_noscheme(relative_ref):
            uri['path'] = components['path_noscheme'] = relative_ref
        elif Protocol.verify_path_empty(relative_ref):
            uri['path'] = components['path_empty'] = relative_ref
        else:
            raise PathException(relative_ref)
    components = URIComponents(**components)
    uri['components'] = components
    return URI(**uri)


def to_string(uri):
    # scheme authority path query fragment
    uri_reference = ''
    if uri.scheme:
        uri_reference = '{}:'.format(uri.scheme)
    if uri.authority:
        uri_reference = '{}//{}'.format(uri_reference, uri.authority)
    uri_reference = '{}{}'.format(uri_reference, uri.path or '')
    if uri.query:
        uri_reference = '{}?{}'.format(uri_reference, uri.query)
    if uri.fragment:
        uri_reference = '{}#{}'.format(uri_reference, uri.fragment)
    return uri_reference
