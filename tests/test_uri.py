import unittest

from aiourllib.uri import (
    URIFabric,
    SchemeException,
    RelSegmentException,
)


class TestURI(unittest.TestCase):
    def assertMatch(self, source):
        self.assertEqual(str(URIFabric.from_string(source)), source)

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

    def test_broken_scheme(self):
        with self.assertRaises(SchemeException):
            self.assertMatch('1a:///d/test.py?fasdfs')

    def test_no_scheme(self):
        self.assertMatch('/tmp/test.py')

    def test_authority(self):
        self.assertMatch('mongo://a:b@c:1/d/e')

    def test_ipv4_address(self):
        self.assertMatch('http://10.10.10.10/')

    def test_authority_value(self):
        uri = URIFabric.from_string('mongo://a:b@c:1/d/e')
        self.assertEqual(uri.authority, 'a:b@c:1')

    def test_rel_segment(self):
        self.assertMatch('a/b/c/')

    def test_rel_segment_value(self):
        self.assertEqual(URIFabric.from_string('a/b/c/').rel_segment, 'a')

    def test_fail_only_query(self):
        with self.assertRaises(RelSegmentException):
            URIFabric.from_string('?a')

    def test_rfc_example_1(self):
        uri = URIFabric.from_string('ftp://ftp.is.co.za/rfc/rfc1808.txt')

        self.assertEqual(uri.scheme, 'ftp')
        self.assertEqual(uri.authority, 'ftp.is.co.za')
        self.assertEqual(uri.abs_path, '/rfc/rfc1808.txt')
        self.assertEqual(uri.rel_segment, None)
        self.assertEqual(uri.query, None)
        self.assertEqual(uri.fragment, None)
        self.assertEqual(uri.opaque_part, None)
        self.assertEqual(uri.host, 'ftp.is.co.za')
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.userinfo, None)
        self.assertEqual(uri.ipv4_address, None)
        self.assertEqual(uri.ipv6_address, None)
        self.assertEqual(uri.hostport, 'ftp.is.co.za')
        self.assertEqual(uri.hostname, 'ftp.is.co.za')
        self.assertEqual(uri.toplabel, 'za')
        self.assertEqual(uri.domainlabels, ['ftp', 'is', 'co'])
        self.assertEqual(uri.segments, None)

    def test_rfc_example_2(self):
        uri = URIFabric.from_string('http://www.ietf.org/rfc/rfc2396.txt')

        self.assertEqual(uri.scheme, 'http')
        self.assertEqual(uri.authority, 'www.ietf.org')
        self.assertEqual(uri.abs_path, '/rfc/rfc2396.txt')
        self.assertEqual(uri.rel_segment, None)
        self.assertEqual(uri.query, None)
        self.assertEqual(uri.fragment, None)
        self.assertEqual(uri.opaque_part, None)
        self.assertEqual(uri.host, 'www.ietf.org')
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.userinfo, None)
        self.assertEqual(uri.ipv4_address, None)
        self.assertEqual(uri.ipv6_address, None)
        self.assertEqual(uri.hostport, 'www.ietf.org')
        self.assertEqual(uri.hostname, 'www.ietf.org')
        self.assertEqual(uri.toplabel, 'org')
        self.assertEqual(uri.domainlabels, ['www', 'ietf'])
        self.assertEqual(uri.segments, None)

    def test_rfc_example_3(self):
        uri = \
            URIFabric.from_string('ldap://[2001:db8::7]/c=GB?objectClass?one')

        self.assertEqual(uri.scheme, 'ldap')
        self.assertEqual(uri.authority, '2001:db8::7')
        self.assertEqual(uri.abs_path, '/')
        self.assertEqual(uri.rel_segment, None)
        self.assertEqual(uri.query, 'c=GB?objectClass?one')
        self.assertEqual(uri.fragment, None)
        self.assertEqual(uri.opaque_part, None)
        self.assertEqual(uri.host, None)
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.userinfo, None)
        self.assertEqual(uri.ipv4_address, None)
        self.assertEqual(uri.ipv6_address, '2001:db8::7')
        self.assertEqual(uri.hostport, None)
        self.assertEqual(uri.hostname, None)
        self.assertEqual(uri.toplabel, None)
        self.assertEqual(uri.domainlabels, None)
        self.assertEqual(uri.segments, None)
