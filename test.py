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
import sqlite3
import base64
from testfixtures.mock import call
from testfixtures import Replacer, ShouldRaise, compare
from testfixtures.popen import MockPopen, PopenBehaviour
#------------------------------------------------------------------------------

def createBase64EncodedString(code):
    return base64.b64encode(code.encode()).decode('utf-8')
#------------------------------------------------------------------------------

class CppInsightsTestCase(unittest.TestCase):
    def mock_mkstemp(self, suffix=None, prefix=None, dir=None, text=False):
        self.fd = open('/tmp/pyt.cpp', "w+")
        return [self.fd.fileno(), '/tmp/pyt.cpp']
    #------------------------------------------------------------------------------

    @staticmethod
    def removeDbTestFile(cls):
        if os.path.exists(cls.getDbNameMock()):
            os.remove(cls.getDbNameMock())
    #------------------------------------------------------------------------------

    @staticmethod
    def getDbNameMock():
        return 'urls_test.db'
    #------------------------------------------------------------------------------

    @classmethod
    def setUpClass(cls):
        cls.removeDbTestFile(cls)
    #------------------------------------------------------------------------------

    def setUp(self):
        self.app = app.test_client()
        self.Popen = MockPopen()
        self.r = Replacer()
        self.r.replace('subprocess.Popen', self.Popen)
        self.r.replace('tempfile.mkstemp', self.mock_mkstemp)
        self.r.replace('app.getDbName', self.getDbNameMock)
        self.addCleanup(self.r.restore)
    #------------------------------------------------------------------------------

    @classmethod
    def tearDownClass(cls):
        cls.removeDbTestFile(cls)
    #------------------------------------------------------------------------------

#    def tearDown(self):
##        if None != self.fd:
#            self.fd.close()
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
                 'use-libcpp',
                ]

        regEx = re.compile(r'[value|label]="(.*?)"' )
        regExGroup = re.compile(r'label="(.*?)"' ) # optgroup label=
        options = []
        for line in data:
            line = line.strip()
            if not line.startswith('<option') and not line.startswith('<optgroup'):
                continue

            if -1 != line.find('class="fonts"'):
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
        self.Popen.set_command('sudo -u pfes docker run --net=none --rm -i insights-test --', stdout=b'o', stderr=b'', returncode=0)
        self.Popen.set_command('docker images --filter=reference=insights-test --format \'{{.ID}} {{.CreatedAt}}\'', stdout=b'o', stderr=b'', returncode=0)
        self.Popen.set_command('docker images --filter=reference=insights-test --format {{.ID}} {{.CreatedAt}}', stdout=b'o', stderr=b'', returncode=0)

        rv = self.app.get('/api/v1/version',
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)
        self.assertTrue(data['stderr'] == 'Insights exited with result code: 0')
        self.assertTrue(data['stdout'] == 'o\nDocker image "insights-test" info: o\n')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_api_v1_version_invalid(self):
        self.Popen.set_command('sudo -u pfes docker run --net=none --rm -i insights-test --', stdout=b'o', stderr=b'', returncode=1)
        self.Popen.set_command('docker images --filter=reference=insights-test --format \'{{.ID}} {{.CreatedAt}}\'', stdout=b'o', stderr=b'', returncode=0)
        self.Popen.set_command('docker images --filter=reference=insights-test --format {{.ID}} {{.CreatedAt}}', stdout=b'o', stderr=b'', returncode=0)

        rv = self.app.get('/api/v1/version',
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 1)
        self.assertTrue(data['stderr'] == 'Insights exited with result code: 1')
        assert b'Compilation failed!' in data['stdout'].encode()
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_api_v1_version_none_sudo(self):
        app.config['USE_SUDO'] = False
        self.Popen.set_command('docker run --net=none --rm -i insights-test --', stdout=b'o', stderr=b'', returncode=0)
        self.Popen.set_command('docker images --filter=reference=insights-test --format \'{{.ID}} {{.CreatedAt}}\'', stdout=b'o', stderr=b'', returncode=0)
        self.Popen.set_command('docker images --filter=reference=insights-test --format {{.ID}} {{.CreatedAt}}', stdout=b'o', stderr=b'', returncode=0)

        rv = self.app.get('/api/v1/version',
                       content_type='application/json')

        app.config['USE_SUDO'] = True

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)
        self.assertTrue(data['stderr'] == 'Insights exited with result code: 0')
        self.assertTrue(data['stdout'] == 'o\nDocker image "insights-test" info: o\n')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_request_api_v1_version_none_docker(self):
        app.config['USE_DOCKER'] = False
        self.Popen.set_command('insights /tmp/pyt.cpp --', stdout=b'o', stderr=b'', returncode=0)
        self.Popen.set_command('docker images --filter=reference=insights-test --format \'{{.ID}} {{.CreatedAt}}\'', stdout=b'o', stderr=b'', returncode=0)
        self.Popen.set_command('docker images --filter=reference=insights-test --format {{.ID}} {{.CreatedAt}}', stdout=b'o', stderr=b'', returncode=0)

        rv = self.app.get('/api/v1/version',
                       content_type='application/json')

        app.config['USE_DOCKER'] = True

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)
        self.assertTrue(data['stderr'] == 'Insights exited with result code: 0')
        self.assertTrue(data['stdout'] == 'o\nDocker image "insights-test" info: Docker not used\n')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------


    def test_request_version(self):
        self.Popen.set_command('sudo -u pfes docker run --net=none --rm -i insights-test --', stdout=b'fake version info from docker', stderr=b'', returncode=0)
        self.Popen.set_command('docker images --filter=reference=insights-test --format \'{{.ID}} {{.CreatedAt}}\'', stdout=b'o', stderr=b'', returncode=0)
        self.Popen.set_command('docker images --filter=reference=insights-test --format {{.ID}} {{.CreatedAt}}', stdout=b'o', stderr=b'', returncode=0)

        rv = self.app.get('/version')

        assert b'fake version info from docker' in rv.data
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def selectedStandard(self, cppStd, text):
        return ('<option value="%s" class="single"  selected="selected" >\n                %s</option>' %(cppStd, text)).encode()
    #------------------------------------------------------------------------------

    def test_link_rev_1_valid(self):
        rv = self.app.post('/lnk?code=I2luY2x1ZGUgPGNzdGRpbz4KdGVtcGxhdGU8dHlwZW5hbWUgVT4KY2xhc3MgWAp7CnB1YmxpYzoKICAgIFgoKSAgICAgICAgICAgPSBkZWZhdWx0OwogICAgWChjb25zdCBYJiB4KSA9IGRlZmF1bHQ7CgogICAgdGVtcGxhdGU8dHlwZW5hbWUgVD4KICAgIFgoVCYmIHgpCiAgICA6IG1Ye30KICAgIHsgfQoKcHJpdmF0ZToKICAgIFUgbVg7Cn07CgppbnQgbWFpbigpCnsKICAgIFg8aW50PiBhcnJbMl17fTsKCiAgICBmb3IoY29uc3QgWDxjb25zdCBpbnQ+JiB4IDogYXJyKSB7IH0KfQ==&std=cpp11&rev=1.0',follow_redirects=True)
        assert self.selectedStandard('cpp11', 'C++ 11') in rv.data
        assert b'<meta property="og:title" content="C++ Insights" />' in rv.data
        assert b'<meta property="og:description" content="#include &lt;cstdio&gt;\ntemplate&lt;typename U&gt;\nclass X\n{\npublic:\n    X()           = default;\n    X(const X&amp;" />' in rv.data
        assert b'<title>C++ Insights</title>' in rv.data
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

    def getShortLink(self, code, std='cpp98', rev='1.0', opts=['alt-syntax-for'], description=''):
        return self.app.post('/api/v1/getshortlink',
                       data=json.dumps(dict(options=opts, code=createBase64EncodedString(code),
                           desc=createBase64EncodedString(description), rev=rev, std=std)),
                       content_type='application/json')
    #------------------------------------------------------------------------------

    def test_create_short_link(self):
        rv = self.getShortLink('hello')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink = data['shortlink']

        assert None != shortLink
        assert shortLink.startswith('/s/')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_short_link_size(self):
        rv = self.getShortLink('slzhello')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink = data['shortlink']

        assert None != shortLink
        assert shortLink.startswith('/s/')
        shortLink = shortLink.replace('/s/', '')
        assert len(shortLink) == 8
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_create_short_link_twice(self):
        # Request a link the first time
        rv = self.getShortLink('hellosame')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink = data['shortlink']

        assert None != shortLink
        assert shortLink.startswith('/s/')
        assert 200 == rv.status_code

        # Request a link for the same parameters a second time
        rv = self.getShortLink('hellosame')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 1)

        shortLink2 = data['shortlink']

        assert None != shortLink2
        assert shortLink2.startswith('/s/')
        assert 200 == rv.status_code

        assert shortLink == shortLink2
    #------------------------------------------------------------------------------

    def test_create_short_link_none_base64(self):
        rv = self.app.post('/api/v1/getshortlink',
                       data=json.dumps(dict(options=['alt-syntax-for'], code='not-base64-encoded', desc='', rev='1.0', std='cpp98')),
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 2)

        shortLink = data['shortlink']

        assert None != shortLink
        assert 'No source' == shortLink
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_create_short_link_null(self):
        rv = self.app.post('/api/v1/getshortlink',
                       data=json.dumps(dict(options=['alt-syntax-for'], code=None, rev='1.0', desc='', std='cpp98')),
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 2)

        shortLink = data['shortlink']

        assert None != shortLink
        assert 'No source' == shortLink
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_short_link_code_differ(self):
        # Request a link the first time
        rv = self.getShortLink('hellosamed')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink = data['shortlink']

        assert None != shortLink
        assert shortLink.startswith('/s/')
        assert 200 == rv.status_code

        # Request a link for 'nearly' the same parameters
        rv = self.getShortLink('bellosamed')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink2 = data['shortlink']

        assert None != shortLink2
        assert shortLink2.startswith('/s/')
        assert 200 == rv.status_code

        assert shortLink != shortLink2
    #------------------------------------------------------------------------------

    def test_short_link_options_differ(self):
        # Request a link the first time
        rv = self.getShortLink('cellosamed')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink = data['shortlink']

        assert None != shortLink
        assert shortLink.startswith('/s/')
        assert 200 == rv.status_code

        # Request a link for 'nearly' the same parameters
        rv = self.getShortLink('cellosamed', opts=['alt-syntax-subscription'])

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink2 = data['shortlink']

        assert None != shortLink2
        assert shortLink2.startswith('/s/')
        assert 200 == rv.status_code

        assert shortLink != shortLink2
    #------------------------------------------------------------------------------

    def test_short_link_std_differ(self):
        # Request a link the first time
        rv = self.getShortLink('mellosamed', std='cpp11')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink = data['shortlink']

        assert None != shortLink
        assert shortLink.startswith('/s/')
        assert 200 == rv.status_code

        # Request a link for 'nearly' the same parameters
        rv = self.getShortLink('mellosamed', std='cpp14')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink2 = data['shortlink']

        assert None != shortLink2
        assert shortLink2.startswith('/s/')
        assert 200 == rv.status_code

        assert shortLink != shortLink2
    #------------------------------------------------------------------------------

    def test_short_link_multiple_options(self):
        rv = self.getShortLink(createBase64EncodedString('multiple options'), opts=['alt-syntax-subscription,alt-syntax-for'])

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink = data['shortlink']

        assert None != shortLink
        assert shortLink.startswith('/s/')
        assert 200 == rv.status_code

        rv2 = self.app.get(shortLink,follow_redirects=False)
        assert 200 == rv2.status_code
        # XXX not working
#        assert shortLink != shortLink2
    #------------------------------------------------------------------------------

    def test_invalid_short_link(self):
        rv = self.app.get('/s/invalid',follow_redirects=True)

        assert 404 == rv.status_code
        assert b'// There is no such link.'  in rv.data
    #------------------------------------------------------------------------------

    def test_invalid_short_link_root(self):
        rv = self.app.get('/s',follow_redirects=True)

        assert 404 == rv.status_code
        assert b'Sorry, the content your are looking for is not there.'  in rv.data
    #------------------------------------------------------------------------------

    def test_create_max_length_short_link(self):
        s = 'a' * 1000000

        rv = self.app.post('/api/v1/getshortlink',
                       data=json.dumps(dict(options=['alt-syntax-for'], code=createBase64EncodedString(s), rev='1.0', desc='', std='cpp98')),
                       content_type='application/json')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink = data['shortlink']

        assert None != shortLink
        assert shortLink.startswith('/s/')
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_create_too_long_short_link(self):
        s = 'a' * 1000001

        rv = self.getShortLink(createBase64EncodedString(s))

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 1)

        shortLink = data['shortlink']

        assert None != shortLink
        assert 'Source too long' == shortLink
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_favicon(self):
        rv = self.app.get('/favicon.ico')

        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_twitter_description_for_root(self):
        rv = self.app.get('/')

        assert b'<meta property="og:description" content="C++ Insights - See your source code with the eyes of a compiler." />' in rv.data
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_twitter_description_for_link(self):
        rv = self.app.post('/lnk?code=I2luY2x1ZGUgPGNzdGRpbz4KdGVtcGxhdGU8dHlwZW5hbWUgVT4KY2xhc3MgWAp7CnB1YmxpYzoKICAgIFgoKSAgICAgICAgICAgPSBkZWZhdWx0OwogICAgWChjb25zdCBYJiB4KSA9IGRlZmF1bHQ7CgogICAgdGVtcGxhdGU8dHlwZW5hbWUgVD4KICAgIFgoVCYmIHgpCiAgICA6IG1Ye30KICAgIHsgfQoKcHJpdmF0ZToKICAgIFUgbVg7Cn07CgppbnQgbWFpbigpCnsKICAgIFg8aW50PiBhcnJbMl17fTsKCiAgICBmb3IoY29uc3QgWDxjb25zdCBpbnQ+JiB4IDogYXJyKSB7IH0KfQ==&std=cpp11&rev=1.0',follow_redirects=True)
        assert b'<meta property="og:description" content="#include &lt;cstdio&gt;\ntemplate&lt;typename U&gt;\nclass X\n{\npublic:\n    X()           = default;\n    X(const X&amp;" />' in rv.data
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_twitter_description_for_short_link(self):
        rv = self.getShortLink('#include <cstdio> int main() { printf("hello\n"); }')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink = data['shortlink']

        assert None != shortLink
        assert 200 == rv.status_code

        rv2 = self.app.get(shortLink,follow_redirects=False)

        assert 200 == rv2.status_code
        assert b'<meta property="og:description" content="#include &lt;cstdio&gt; int main() { printf(&#34;hello\n&#34;); }" />' in rv2.data
    #------------------------------------------------------------------------------

    def test_create_short_link_with_description(self):
        rv = self.getShortLink('hello with description', description='A description')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink = data['shortlink']

        rv2 = self.app.get(shortLink,follow_redirects=False)

        assert b'<meta property="og:title" content="C++ Insights - A description" />' in rv2.data
        assert b'<meta name="description" content="C++ Insights - A description" />' in rv2.data
        assert b'<title>C++ Insights - A description</title>' in rv2.data
        assert 200 == rv2.status_code
    #------------------------------------------------------------------------------

    def test_root_description(self):
        rv = self.app.get('/',follow_redirects=False)

        assert b'<meta property="og:title" content="C++ Insights" />' in rv.data
        assert b'<meta property="og:description" content="C++ Insights - See your source code with the eyes of a compiler." />' in rv.data
        assert b'<title>C++ Insights</title>' in rv.data
        assert 200 == rv.status_code
    #------------------------------------------------------------------------------

    def test_short_link_toolid_0(self):
        rv = self.getShortLink('test for tool id')

        data = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(data['returncode'] == 0)

        shortLink = data['shortlink']

        assert None != shortLink
        assert shortLink.startswith('/s/')
        assert 200 == rv.status_code

        conn = sqlite3.connect(self.getDbNameMock())
        c = conn.cursor()
        cur = c.execute('SELECT toolid FROM shortened WHERE short = ?', (shortLink.replace('/s/', ''),))
        rv = cur.fetchone()
        conn.close()

        assert 1 == rv[0]
    #------------------------------------------------------------------------------

    def test_get_app(self):
        import app
        rv = app.getApp()

        assert None != rv
#        assert app.getDbName() == 'urls.db'
    #------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
