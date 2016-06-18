import unittest

from aiourllib.rfc2396 import URIFabric


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
