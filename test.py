#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# C++ Insights Web, copyright (c) by Andreas Fertig
# Distributed under an MIT license. See /LICENSE

import os
from app import app
import unittest
import tempfile
import json
from testfixtures.mock import call
from testfixtures import Replacer, ShouldRaise, compare
from testfixtures.popen import MockPopen, PopenBehaviour
#------------------------------------------------------------------------------

class CppInsightsTestCase(unittest.TestCase):
    def mock_mkstemp(self, suffix=None, prefix=None, dir=None, text=False):
        self.fd = open('/tmp/pyt.cpp', "w+")
        return [self.fd.fileno(), '/tmp/pyt.cpp']
    #------------------------------------------------------------------------------

    def setUp(self):
        self.app = app.test_client()
        self.Popen = MockPopen()
        self.r = Replacer()
        self.r.replace('subprocess.Popen', self.Popen)
        self.r.replace('tempfile.mkstemp', self.mock_mkstemp)
        self.addCleanup(self.r.restore)
    #------------------------------------------------------------------------------


#    def tearDown(self):
    #------------------------------------------------------------------------------

    def test_access_root(self):
        rv = self.app.get('/')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_invalid_site(self):
        rv = self.app.get('/aa')
        assert b'Page Not Found' in rv.data
    #------------------------------------------------------------------------------

    def test_invalid_site_with_post(self):
        rv = self.app.post('/test_function',
                       data=json.dumps(dict(foo='bar')),
                       content_type='application/json')

        assert 405 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_api_v1_tranform_valid(self):
        self.Popen.set_command('sudo -u pfes docker run --net=none -v /tmp/pyt.cpp:/home/insights/insights.cpp --rm -i insights-test -std=c++98', stdout=b'o', stderr=b'', returncode=0)

        rv = self.app.post('/api/v1/transform',
                       data=json.dumps(dict(cppStd='cpp98', code='hello')),
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)
        self.assertTrue(data['stderr'] == 'Insights exited with result code: 0')
        self.assertTrue(data['stdout'] == 'o')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_api_v1_tranform_valid_with_result_1(self):
        self.Popen.set_command('sudo -u pfes docker run --net=none -v /tmp/pyt.cpp:/home/insights/insights.cpp --rm -i insights-test -std=c++98', stdout=b'o', stderr=b'', returncode=1)

        rv = self.app.post('/api/v1/transform',
                       data=json.dumps(dict(cppStd='cpp98', code='hello')),
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 1)
        self.assertTrue(data['stderr'] == 'Insights exited with result code: 1')
        self.assertTrue(data['stdout'] == 'Compilation failed!')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_api_v1_tranform_valid_with_warnings(self):
        self.Popen.set_command('sudo -u pfes docker run --net=none -v /tmp/pyt.cpp:/home/insights/insights.cpp --rm -i insights-test -std=c++98', stdout=b'o', stderr=b'Warning: unused var', returncode=0)

        rv = self.app.post('/api/v1/transform',
                       data=json.dumps(dict(cppStd='cpp98', code='hello')),
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)
        self.assertTrue(data['stderr'] == 'Warning: unused var')
        self.assertTrue(data['stdout'] == 'o')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_api_v1_tranform_invalid_std(self):
        self.Popen.set_command('sudo -u pfes docker run --net=none -v /tmp/pyt.cpp:/home/insights/insights.cpp --rm -i insights-test -std=c++17', stdout=b'o', stderr=b'',returncode=0)

        rv = self.app.post('/api/v1/transform',
                       data=json.dumps(dict(cppStd='cpp12', code='hello')),
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)
        self.assertTrue(data['stderr'] == 'Insights exited with result code: 0')
        self.assertTrue(data['stdout'] == 'o')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_link_rev_1_valid(self):
        rv = self.app.post('/lnk?code=I2luY2x1ZGUgPGNzdGRpbz4KdGVtcGxhdGU8dHlwZW5hbWUgVT4KY2xhc3MgWAp7CnB1YmxpYzoKICAgIFgoKSAgICAgICAgICAgPSBkZWZhdWx0OwogICAgWChjb25zdCBYJiB4KSA9IGRlZmF1bHQ7CgogICAgdGVtcGxhdGU8dHlwZW5hbWUgVD4KICAgIFgoVCYmIHgpCiAgICA6IG1Ye30KICAgIHsgfQoKcHJpdmF0ZToKICAgIFUgbVg7Cn07CgppbnQgbWFpbigpCnsKICAgIFg8aW50PiBhcnJbMl17fTsKCiAgICBmb3IoY29uc3QgWDxjb25zdCBpbnQ+JiB4IDogYXJyKSB7IH0KfQ==&std=cpp11&rev=1.0',follow_redirects=True)
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_link_rev_1_missing_std(self):
        rv = self.app.post('/lnk?code=I2luY2x1ZGUgPGNzdGRpbz4KdGVtcGxhdGU8dHlwZW5hbWUgVT4KY2xhc3MgWAp7CnB1YmxpYzoKICAgIFgoKSAgICAgICAgICAgPSBkZWZhdWx0OwogICAgWChjb25zdCBYJiB4KSA9IGRlZmF1bHQ7CgogICAgdGVtcGxhdGU8dHlwZW5hbWUgVD4KICAgIFgoVCYmIHgpCiAgICA6IG1Ye30KICAgIHsgfQoKcHJpdmF0ZToKICAgIFUgbVg7Cn07CgppbnQgbWFpbigpCnsKICAgIFg8aW50PiBhcnJbMl17fTsKCiAgICBmb3IoY29uc3QgWDxjb25zdCBpbnQ+JiB4IDogYXJyKSB7IH0KfQ==&std=cpp12&rev=1.0',follow_redirects=True)
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_link_rev_1_invalid_std(self):
        rv = self.app.post('/lnk?code=I2luY2x1ZGUgPGNzdGRpbz4KdGVtcGxhdGU8dHlwZW5hbWUgVT4KY2xhc3MgWAp7CnB1YmxpYzoKICAgIFgoKSAgICAgICAgICAgPSBkZWZhdWx0OwogICAgWChjb25zdCBYJiB4KSA9IGRlZmF1bHQ7CgogICAgdGVtcGxhdGU8dHlwZW5hbWUgVD4KICAgIFgoVCYmIHgpCiAgICA6IG1Ye30KICAgIHsgfQoKcHJpdmF0ZToKICAgIFUgbVg7Cn07CgppbnQgbWFpbigpCnsKICAgIFg8aW50PiBhcnJbMl17fTsKCiAgICBmb3IoY29uc3QgWDxjb25zdCBpbnQ+JiB4IDogYXJyKSB7IH0KfQ==&rev=1.0',follow_redirects=True)
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_link_rev_1_missing_rev(self):
        rv = self.app.post('/lnk?code=I2luY2x1ZGUgPGNzdGRpbz4KdGVtcGxhdGU8dHlwZW5hbWUgVT4KY2xhc3MgWAp7CnB1YmxpYzoKICAgIFgoKSAgICAgICAgICAgPSBkZWZhdWx0OwogICAgWChjb25zdCBYJiB4KSA9IGRlZmF1bHQ7CgogICAgdGVtcGxhdGU8dHlwZW5hbWUgVD4KICAgIFgoVCYmIHgpCiAgICA6IG1Ye30KICAgIHsgfQoKcHJpdmF0ZToKICAgIFUgbVg7Cn07CgppbnQgbWFpbigpCnsKICAgIFg8aW50PiBhcnJbMl17fTsKCiAgICBmb3IoY29uc3QgWDxjb25zdCBpbnQ+JiB4IDogYXJyKSB7IH0KfQ==&std=cpp11',follow_redirects=True)
        assert 404 == rv.status_code
    #------------------------------------------------------------------------------

    def test_link_rev_1_invalid_base64(self):
        rv = self.app.post('/lnk?code=I2luY2x1ZGUgPGNzdGRpbz4KdGVtcGxhdGU8dHlwZW5hbWUgVT4KY2xhc3MgWAp7CnB1YmxpYzoKICAgIFgoKSAgICAgICAgICAgPSBkZWZhdWx0OwogICAgWChjb25zdCBYJiB4KSA9IGRlZmF1bHQ7CgogICAgdGVtcGxhdGU8dHlwZW5hbWUgVD4KICAgIFgoVCYmIHgpCiAgICA6IG1Ye30KICAgIHsgfQoKcHJpdmF0ZToKICAgIFUgbVg7Cn07CgppbnQgbWFpbigpCnsKICAgIFg8aW50PiBhcnJbMl17fTsKCiAgICBmb3IoY29uc3QgWDxjb25zdCBpbnQAAAAAAAAAAJiB4IDogYXJyKSB7IH0KfQ==&std=cpp11&rev=1.0',follow_redirects=True)
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
