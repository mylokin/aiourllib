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
    def process(cls, uri_reference):
        scheme, hier_part = cls.strip_scheme(uri_reference)
        if scheme:
            # hier_part
            fragment, hier_part = cls.strip_fragment(hier_part)
            query, hier_part = cls.strip_query(hier_part)
            if hier_part.startswith('//'):
                # authority
                authority, hier_part = cls.strip_authority(hier_part)
            elif no hier_part:
                path_empty = ''
        else:
            relative_ref = hier_part
