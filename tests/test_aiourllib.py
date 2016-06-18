import asyncio
import contextlib
import unittest

import aiourllib


class HttpbinTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.get_event_loop()

    @classmethod
    def tearDownClass(cls):
        cls.loop.close()

    async def read(self, request):
        with contextlib.closing(await request) as response:
            return await response.read_content()

    async def read_json(self, request):
        with contextlib.closing(await request) as response:
            return await response.read_json()

    def fetch(self, url):
        request = aiourllib.get(url)
        return self.loop.run_until_complete(
            self.read(request))

    def fetch_json(self, url, read_timeout=66):
        request = aiourllib.get(url, read_timeout=read_timeout)
        return self.loop.run_until_complete(
            self.read_json(request))

    def test_ip(self):
        self.fetch_json('https://httpbin.org/ip')

    def test_user_agent(self):
        self.fetch_json('https://httpbin.org/user-agent')

    def test_headers(self):
        self.fetch_json('https://httpbin.org/headers')

    def test_get(self):
        self.fetch_json('https://httpbin.org/get')

    def test_encoding_utf8(self):
        self.fetch('https://httpbin.org/encoding/utf8')

    def test_gzip(self):
        self.fetch_json('https://httpbin.org/gzip')

    def test_deflate(self):
        self.fetch_json('https://httpbin.org/deflate')

    def test_stream(self):
        self.fetch('https://httpbin.org/stream/20')

    def test_delay(self):
        with self.assertRaises(aiourllib.exc.ReadTimeout):
            self.fetch_json('https://httpbin.org/delay/5', 1.)

    def test_xml(self):
        self.fetch('https://httpbin.org/xml')
