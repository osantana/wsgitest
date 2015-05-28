#!/usr/bin/env python3
# coding: utf-8


import time
import logging
import socket
import multiprocessing

try:
    from http.client import HTTPConnection, HTTPException
except ImportError:
    # noinspection PyUnresolvedReferences
    from httplib import HTTPConnection, HTTPException

from werkzeug.serving import run_simple
from werkzeug.wrappers import Response


class CheckApplicationMiddleware(object):
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        if '__application__' in environ['PATH_INFO']:
            return Response('OK')(environ, start_response)
        return self.application(environ, start_response)


# noinspection PyMethodMayBeStatic
class WSGITestServer(multiprocessing.Process):
    def __init__(self, application, host=None, port=None, *args, **kwargs):
        super(WSGITestServer, self).__init__(*args, **kwargs)
        self.host = host or "127.0.0.1"
        self.port = port or self._get_free_port()
        self.application_url = "http://{}:{}/".format(self.host, self.port)
        self.application = CheckApplicationMiddleware(application)

    def _get_free_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))
        ip, port = s.getsockname()
        s.close()
        return port

    def run(self):
        logging.getLogger("werkzeug").setLevel(logging.CRITICAL + 10)
        run_simple(self.host, self.port, self.application)

    def _check_server(self, host, port, path_info='/', timeout=3, retries=30):
        if retries < 0:
            return 0

        time.sleep(.3)

        for i in range(retries):
            try:
                conn = HTTPConnection(host, port, timeout=timeout)
                conn.request('GET', path_info)
                res = conn.getresponse()
                return res.status
            except (socket.error, HTTPException):
                time.sleep(.3)
        return 0

    def wait(self, retries=30):
        running = self._check_server(self.host, self.port, '/__application__/', retries=retries)
        if running:
            return True

        try:
            self.terminate()
        finally:
            return False

    @classmethod
    def create(cls, application, host=None, port=None):
        server = cls(application, host, port)
        server.start()
        server.wait()
        return server
