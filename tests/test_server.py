# coding: utf-8


from unittest import TestCase

try:
    from urllib.parse import urljoin
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin


import requests
from requests import ConnectionError

from werkzeug.wrappers import Request, Response

from wsgitest.server import WSGITestServer


@Request.application
def application(request):
    return Response('Hello World!')


class ServerTestCase(TestCase):
    def test_start(self):
        server = WSGITestServer.create(application)

        response = requests.get(urljoin(server.application_url, "/"))
        self.assertEqual(response.status_code, 200)

        server.terminate()
        with self.assertRaises(ConnectionError):
            requests.get(urljoin(server.application_url, "/"))

    def test_application_reference(self):
        server = WSGITestServer.create("tests.test_server.application")
        try:
            response = requests.get(urljoin(server.application_url, "/"))
            self.assertEqual(response.status_code, 200)
        finally:
            server.terminate()


class AppServerTestCase(TestCase):
    def setUp(self):
        self.server = WSGITestServer.create(application)
        self.app_url = self.server.application_url

    def tearDown(self):
        self.server.terminate()

    def _url(self, url):
        return urljoin(self.app_url, url)

    def test_hello(self):
        response = requests.get(self._url("/"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Hello World!")

    def test_wrapper(self):
        response = requests.get(self._url("/__application__/"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
