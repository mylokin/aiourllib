import string


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
        if port.isdigit():
            port = int(port)
        else:
            raise PortException(port)
        return port, authority

    @classmethod
    def verify_ipv4_address(cls, host):
        host = host.split('.')
        ipv4 = all(n and n.isdigit() and not n.startswith('0') and
            int(n) <= 255 for n in host)
        return len(host) == 4 and ipv4:

    @classmethod
    def process(cls, uri_reference):
        scheme, hier_part = cls.strip_scheme(uri_reference)
        if scheme:
            # hier_part
            fragment, hier_part = cls.strip_fragment(hier_part)
            query, hier_part = cls.strip_query(hier_part)
            if hier_part.startswith('//'):
                # authority
                authority, hier_part = cls.strip_authority(hier_part)
                userinfo, authority = cls.strip_userinfo(authority)
                port, authority = cls.strip_port(authority)
                host = authority
                if cls.verify_ipv4_address(host):
                    ipv4_address = host
                elif all(c in cls.REG_NAME for c in host):
                    reg_name = host
                else:
                    raise AuthorityException(host)
                path_abempty = hier_part
            elif no hier_part:
                path_empty = ''
        else:
            relative_ref = hier_part
