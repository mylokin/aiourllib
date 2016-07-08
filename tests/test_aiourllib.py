import asyncio
import contextlib
import unittest

import aiourllib


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)

    @classmethod
    def tearDownClass(cls):
        cls.loop.close()


class HttpbinJsonTestCase(TestCase):
    async def read(self, request):
        with contextlib.closing(await request) as response:
            return await response.read_json()

    def fetch(self, url, read_timeout=60, connection_timeout=60):
        request = aiourllib.get(
            url,
            read_timeout=read_timeout,
            connection_timeout=connection_timeout,
        )
        return self.loop.run_until_complete(self.read(request))

    def test_ip(self):
        self.fetch('https://httpbin.org/ip')

    def test_user_agent(self):
        self.fetch('https://httpbin.org/user-agent')

    def test_headers(self):
        self.fetch('https://httpbin.org/headers')

    def test_get(self):
        self.fetch('https://httpbin.org/get')

    def test_gzip(self):
        self.fetch('https://httpbin.org/gzip')

    def test_deflate(self):
        self.fetch('https://httpbin.org/deflate')

    def test_delay(self):
        with self.assertRaises(aiourllib.exc.ReadTimeout):
            self.fetch('https://httpbin.org/delay/5', 1.)


class HttpbinTestCase(TestCase):
    async def read(self, request):
        with contextlib.closing(await request) as response:
            return await response.read_content()

    def fetch(self, url):
        request = aiourllib.get(url)
        return self.loop.run_until_complete(self.read(request))

    def test_encoding_utf8(self):
        self.fetch('https://httpbin.org/encoding/utf8')

    def test_stream(self):
        self.fetch('https://httpbin.org/stream/20')

    def test_xml(self):
        self.fetch('https://httpbin.org/xml')


class HttpbinHeadTestCase(TestCase):
    async def read(self, request):
        with contextlib.closing(await request) as response:
            return response

    def head(self, uri):
        request = aiourllib.head(uri)
        return self.loop.run_until_complete(self.read(request))

    def test_ip(self):
        response = self.head('https://httpbin.org/ip')
        self.assertEqual(response.status_code, 200)


class HttpbinPostTestCase(TestCase):
    async def send(self, request):
        with contextlib.closing(await request) as response:
            await request.send()
            return await response.read_content()

    def post(self, uri, data):
        request = aiourllib.post(uri, data)
        return self.loop.run_until_complete(self.send(request))

    def test_post(self):
        self.post('https://httpbin.org/ip', 'data')
