wsgitest
========

|Build Status| |Coverage Status|


You can use `wsgitest` to start a HTTP server for a WSGI application and
control the process:

.. code-block:: python

    @Request.application
    def application(request):
        return Response('Hello World!')

    class AppServerTestCase(TestCase):
        def test_hello_app(self):
            server = WSGITestServer.create(application)
            try:
                response = requests.get(server.application_url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, b"Hello World!")
            finally:
                server.terminate()

        def test_hello_app_reference(self):
            server = WSGITestServer.create("tests.test_server.application")
            try:
                response = requests.get(server.application_url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, b"Hello World!")
            finally:
                server.terminate()

The method `WSGITestServer.create()` initialize a `multiprocessing.Process`_
and wait for the server startup.

You can use server as a context manager to avoid that tests get stucked when
you forget to "terminate" server:

.. code-block:: python

    @Request.application
    def application(request):
        return Response('Hello World!')

    class AppServerTestCase(TestCase):
        def test_hello_app(self):
            with WSGITestServer(application) as server:
                response = requests.get(server.application_url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, b"Hello World!")

You can also start server with an specific host/ip or TCP port:

.. code-block:: python

    @Request.application
    def application(request):
        return Response('Hello World!')

    class AppServerTestCase(TestCase):
        def test_hello_app(self):
            with WSGITestServer(application, "0.0.0.0", 5000) as server:
                response = requests.get(server.application_url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, b"Hello World!")


.. _multiprocessing.Process: https://docs.python.org/3/library/multiprocessing.html#the-process-class


.. |Build Status| image:: https://travis-ci.org/osantana/wsgitest.png?branch=master
   :target: https://travis-ci.org/osantana/wsgitest
.. |Coverage Status| image:: https://coveralls.io/repos/osantana/wsgitest/badge.svg?branch=master
   :target: https://coveralls.io/r/osantana/wsgitest?branch=master
