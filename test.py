#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# C++ Insights Web, copyright (c) by Andreas Fertig
# Distributed under an MIT license. See /LICENSE

import os
from app import app
import unittest
import tempfile
import re
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
#        if hasattr(self, 'fd'):
#            self.fd.close()
    #------------------------------------------------------------------------------

    def test_access_root(self):
        rv = self.app.get('/')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_cpp_options_order_root(self):
        rv = self.app.get('/')
        data = rv.data.decode("utf-8").splitlines()
        opts = [ 'C++ Standard',
                 'cpp98',
                 'cpp11',
                 'cpp14',
                 'cpp17',
                 'cpp2a',
                 'Alternative Styles',
                 'alt-syntax-for',
                 'alt-syntax-subscription',
                 'More Transformations',
#                 'stdinitlist',
                 'all-implicit-casts',
                ]

        regEx = re.compile(r'[value|label]="(.*?)"' )
        regExGroup = re.compile(r'label="(.*?)"' ) # optgroup label=
        options = []
        for line in data:
            line = line.strip()
            if not line.startswith('<option') and not line.startswith('<optgroup'):
                continue

            m = regEx.search(line)
            if None != m:
                options.append(m.group(1))


        assert opts == options
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
        self.Popen.set_command('sudo -u pfes docker run --net=none -v /tmp/pyt.cpp:/home/insights/insights.cpp --rm -i insights-test -- -std=c++98', stdout=b'o', stderr=b'', returncode=0)

        rv = self.app.post('/api/v1/transform',
                       data=json.dumps(dict(insightsOptions=['cpp98'], code='hello')),
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)
        self.assertTrue(data['stderr'] == 'Insights exited with result code: 0')
        self.assertTrue(data['stdout'] == 'o')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_api_v1_tranform_valid_with_result_1(self):
        self.Popen.set_command('sudo -u pfes docker run --net=none -v /tmp/pyt.cpp:/home/insights/insights.cpp --rm -i insights-test -- -std=c++98', stdout=b'o', stderr=b'', returncode=1)

        rv = self.app.post('/api/v1/transform',
                       data=json.dumps(dict(insightsOptions=['cpp98'], code='hello')),
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 1)
        self.assertTrue(data['stderr'] == 'Insights exited with result code: 1')
        self.assertTrue(data['stdout'] == 'Compilation failed!')
        assert b'Compilation failed!' in data['stdout'].encode()
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_api_v1_tranform_valid_with_result_and_insights_args_1(self):
        self.Popen.set_command('sudo -u pfes docker run --net=none -v /tmp/pyt.cpp:/home/insights/insights.cpp --rm -i insights-test -alt-syntax-for -- -std=c++98', stdout=b'o', stderr=b'', returncode=0)

        rv = self.app.post('/api/v1/transform',
                       data=json.dumps(dict(insightsOptions=['alt-syntax-for','cpp98'], code='hello')),
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)
        self.assertTrue(data['stderr'] == 'Insights exited with result code: 0')
        self.assertTrue(data['stdout'] == 'o')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_api_v1_tranform_valid_with_warnings(self):
        self.Popen.set_command('sudo -u pfes docker run --net=none -v /tmp/pyt.cpp:/home/insights/insights.cpp --rm -i insights-test -- -std=c++98', stdout=b'o', stderr=b'Warning: unused var', returncode=0)

        rv = self.app.post('/api/v1/transform',
                       data=json.dumps(dict(insightsOptions=['cpp98'], code='hello')),
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)
        self.assertTrue(data['stderr'] == 'Warning: unused var')
        self.assertTrue(data['stdout'] == 'o')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_api_v1_tranform_invalid_std(self):
        self.Popen.set_command('sudo -u pfes docker run --net=none -v /tmp/pyt.cpp:/home/insights/insights.cpp --rm -i insights-test -- -std=c++17', stdout=b'o', stderr=b'',returncode=0)

        rv = self.app.post('/api/v1/transform',
                       data=json.dumps(dict(insightsOptions=['cpp12'], code='hello')),
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)
        self.assertTrue(data['stderr'] == 'Insights exited with result code: 0')
        self.assertTrue(data['stdout'] == 'o')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_api_v1_version(self):
        self.Popen.set_command('sudo -u pfes docker run --net=none --rm -i insights-test', stdout=b'o', stderr=b'', returncode=0)

        rv = self.app.get('/api/v1/version',
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)
        self.assertTrue(data['stderr'] == 'Insights exited with result code: 0')
        self.assertTrue(data['stdout'] == 'o')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_api_v1_version_invalid(self):
        self.Popen.set_command('sudo -u pfes docker run --net=none --rm -i insights-test', stdout=b'o', stderr=b'', returncode=1)

        rv = self.app.get('/api/v1/version',
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 1)
        self.assertTrue(data['stderr'] == 'Insights exited with result code: 1')
        assert b'Compilation failed!' in data['stdout'].encode()
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_version(self):
        self.Popen.set_command('sudo -u pfes docker run --net=none --rm -i insights-test', stdout=b'fake version info from docker', stderr=b'', returncode=0)

        rv = self.app.get('/version')

        assert b'fake version info from docker' in rv.data
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def selectedStandard(self, cppStd, text):
        return ('<option value="%s" class="single"  selected="selected" >%s</option>' %(cppStd, text)).encode()
    #------------------------------------------------------------------------------

    def test_link_rev_1_valid(self):
        rv = self.app.post('/lnk?code=I2luY2x1ZGUgPGNzdGRpbz4KdGVtcGxhdGU8dHlwZW5hbWUgVT4KY2xhc3MgWAp7CnB1YmxpYzoKICAgIFgoKSAgICAgICAgICAgPSBkZWZhdWx0OwogICAgWChjb25zdCBYJiB4KSA9IGRlZmF1bHQ7CgogICAgdGVtcGxhdGU8dHlwZW5hbWUgVD4KICAgIFgoVCYmIHgpCiAgICA6IG1Ye30KICAgIHsgfQoKcHJpdmF0ZToKICAgIFUgbVg7Cn07CgppbnQgbWFpbigpCnsKICAgIFg8aW50PiBhcnJbMl17fTsKCiAgICBmb3IoY29uc3QgWDxjb25zdCBpbnQ+JiB4IDogYXJyKSB7IH0KfQ==&std=cpp11&rev=1.0',follow_redirects=True)
        assert self.selectedStandard('cpp11', 'C++ 11') in rv.data
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_link_rev_1_invalid_std(self):
        rv = self.app.post('/lnk?code=I2luY2x1ZGUgPGNzdGRpbz4KdGVtcGxhdGU8dHlwZW5hbWUgVT4KY2xhc3MgWAp7CnB1YmxpYzoKICAgIFgoKSAgICAgICAgICAgPSBkZWZhdWx0OwogICAgWChjb25zdCBYJiB4KSA9IGRlZmF1bHQ7CgogICAgdGVtcGxhdGU8dHlwZW5hbWUgVD4KICAgIFgoVCYmIHgpCiAgICA6IG1Ye30KICAgIHsgfQoKcHJpdmF0ZToKICAgIFUgbVg7Cn07CgppbnQgbWFpbigpCnsKICAgIFg8aW50PiBhcnJbMl17fTsKCiAgICBmb3IoY29uc3QgWDxjb25zdCBpbnQ+JiB4IDogYXJyKSB7IH0KfQ==&std=cpp12&rev=1.0',follow_redirects=True)
        assert self.selectedStandard('cpp17', 'C++ 17') in rv.data
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_link_rev_1_missing_std(self):
        rv = self.app.post('/lnk?code=I2luY2x1ZGUgPGNzdGRpbz4KdGVtcGxhdGU8dHlwZW5hbWUgVT4KY2xhc3MgWAp7CnB1YmxpYzoKICAgIFgoKSAgICAgICAgICAgPSBkZWZhdWx0OwogICAgWChjb25zdCBYJiB4KSA9IGRlZmF1bHQ7CgogICAgdGVtcGxhdGU8dHlwZW5hbWUgVD4KICAgIFgoVCYmIHgpCiAgICA6IG1Ye30KICAgIHsgfQoKcHJpdmF0ZToKICAgIFUgbVg7Cn07CgppbnQgbWFpbigpCnsKICAgIFg8aW50PiBhcnJbMl17fTsKCiAgICBmb3IoY29uc3QgWDxjb25zdCBpbnQ+JiB4IDogYXJyKSB7IH0KfQ==&rev=1.0',follow_redirects=True)
        assert self.selectedStandard('cpp17', 'C++ 17') in rv.data
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_link_rev_1_missing_rev(self):
        rv = self.app.post('/lnk?code=I2luY2x1ZGUgPGNzdGRpbz4KdGVtcGxhdGU8dHlwZW5hbWUgVT4KY2xhc3MgWAp7CnB1YmxpYzoKICAgIFgoKSAgICAgICAgICAgPSBkZWZhdWx0OwogICAgWChjb25zdCBYJiB4KSA9IGRlZmF1bHQ7CgogICAgdGVtcGxhdGU8dHlwZW5hbWUgVD4KICAgIFgoVCYmIHgpCiAgICA6IG1Ye30KICAgIHsgfQoKcHJpdmF0ZToKICAgIFUgbVg7Cn07CgppbnQgbWFpbigpCnsKICAgIFg8aW50PiBhcnJbMl17fTsKCiAgICBmb3IoY29uc3QgWDxjb25zdCBpbnQ+JiB4IDogYXJyKSB7IH0KfQ==&std=cpp11',follow_redirects=True)
        assert self.selectedStandard('cpp17', 'C++ 17') in rv.data
        assert b'The revision of the link is invalid.' in rv.data
        assert 404 == rv.status_code
    #------------------------------------------------------------------------------

    def test_link_rev_1_invalid_rev(self):
        rv = self.app.post('/lnk?code=I2luY2x1ZGUgPGNzdGRpbz4KdGVtcGxhdGU8dHlwZW5hbWUgVT4KY2xhc3MgWAp7CnB1YmxpYzoKICAgIFgoKSAgICAgICAgICAgPSBkZWZhdWx0OwogICAgWChjb25zdCBYJiB4KSA9IGRlZmF1bHQ7CgogICAgdGVtcGxhdGU8dHlwZW5hbWUgVD4KICAgIFgoVCYmIHgpCiAgICA6IG1Ye30KICAgIHsgfQoKcHJpdmF0ZToKICAgIFUgbVg7Cn07CgppbnQgbWFpbigpCnsKICAgIFg8aW50PiBhcnJbMl17fTsKCiAgICBmb3IoY29uc3QgWDxjb25zdCBpbnQ+JiB4IDogYXJyKSB7IH0KfQ==&std=cpp11&rev=22',follow_redirects=True)
        assert self.selectedStandard('cpp17', 'C++ 17') in rv.data
        assert b'The revision of the link is invalid.' in rv.data
        assert 404 == rv.status_code
    #------------------------------------------------------------------------------

    def test_link_rev_1_invalid_base64(self):
        rv = self.app.post('/lnk?code=I2luY2x1ZGUgPGNzdGRpbz4KdGVtcGxhdGU8dHlwZW5hbWUgVT4KY2xhc3MgWAp7CnB1YmxpYzoKICAgIFgoKSAgICAgICAgICAgPSBkZWZhdWx0OwogICAgWChjb25zdCBYJiB4KSA9IGRlZmF1bHQ7CgogICAgdGVtcGxhdGU8dHlwZW5hbWUgVD4KICAgIFgoVCYmIHgpCiAgICA6IG1Ye30KICAgIHsgfQoKcHJpdmF0ZToKICAgIFUgbVg7Cn07CgppbnQgbWFpbigpCnsKICAgIFg8aW50PiBhcnJbMl17fTsKCiAgICBmb3IoY29uc3QgWDxjb25zdCBpbnQAAAAAAAAAAJiB4IDogYXJyKSB7IH0KfQ==&std=cpp11&rev=1.0',follow_redirects=True)
        assert self.selectedStandard('cpp11', 'C++ 11') in rv.data
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
