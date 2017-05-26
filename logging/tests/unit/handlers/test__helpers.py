# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest


class TestFlaskTrace(unittest.TestCase):

    def create_app(self):
        import flask

        app = flask.Flask(__name__)

        @app.route('/')
        def index():
            return 'test flask trace'

        return app

    def setUp(self):
        self.app = self.create_app()

    def test_trace_id_no_context_header(self):
        from google.cloud.logging.handlers._helpers import get_trace_id_from_flask
        from google.cloud.logging.handlers._helpers import get_trace_id

        with self.app.test_request_context(
                path='/',
                headers={}):
            trace_id = get_trace_id_from_flask()
            trace_id_returned = get_trace_id()

        self.assertEqual(trace_id, None)
        self.assertEqual(trace_id_returned, None)

    def test_trace_id_valid_context_header(self):
        from google.cloud.logging.handlers._helpers import get_trace_id_from_flask
        from google.cloud.logging.handlers._helpers import get_trace_id

        flask_trace_header = 'X_CLOUD_TRACE_CONTEXT'
        flask_trace_id = 'testtraceidflask/testspanid'

        with self.app.test_request_context(
                path='/',
                headers={flask_trace_header:flask_trace_id}):
            trace_id = get_trace_id_from_flask()
            trace_id_returned = get_trace_id()

        expected_trace_id = 'testtraceidflask'
        self.assertEqual(trace_id, expected_trace_id)
        self.assertEqual(trace_id, trace_id_returned)


class TestDjangoTrace(unittest.TestCase):

    def setUp(self):
        from django.conf import settings
        from django.test.utils import setup_test_environment

        if not settings.configured:
            settings.configure()
        setup_test_environment()

    def tearDown(self):
        from django.test.utils import teardown_test_environment

        teardown_test_environment()

    def test_trace_id_no_context_header(self):
        from django.test import RequestFactory
        from google.cloud.logging.handlers._helpers import get_trace_id_from_django
        from google.cloud.logging.handlers._helpers import get_trace_id
        from google.cloud.logging.handlers.middleware.request import RequestMiddleware
        from google.cloud.logging.handlers.middleware.request import _thread_locals

        request = RequestFactory().get('/')

        middleware = RequestMiddleware()
        middleware.process_request(request)
        trace_id = get_trace_id_from_django()
        trace_id_returned = get_trace_id()

        self.assertEqual(trace_id, None)
        self.assertEqual(trace_id_returned, None)

        _thread_locals.__dict__.clear()

    def test_trace_id_valid_context_header(self):
        from django.test import RequestFactory
        from google.cloud.logging.handlers._helpers import get_trace_id_from_django
        from google.cloud.logging.handlers._helpers import get_trace_id
        from google.cloud.logging.handlers.middleware.request import RequestMiddleware
        from google.cloud.logging.handlers.middleware.request import _thread_locals

        django_trace_header = 'HTTP_X_CLOUD_TRACE_CONTEXT'
        django_trace_id = 'testtraceiddjango/testspanid'

        request = RequestFactory().get(
            '/',
            **{django_trace_header:django_trace_id})

        middleware = RequestMiddleware()
        middleware.process_request(request)
        trace_id = get_trace_id_from_django()
        trace_id_returned = get_trace_id()

        expected_trace_id = 'testtraceiddjango'
        self.assertEqual(trace_id, expected_trace_id)
        self.assertEqual(trace_id, trace_id_returned)

        _thread_locals.__dict__.clear()
