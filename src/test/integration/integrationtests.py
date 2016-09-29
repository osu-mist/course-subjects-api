import argparse
import json
import ssl
import unittest
import warnings

import requests
import urllib3

try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass

def read_config(config_path):
    with open(config_path) as f:
        return json.load(f)

class CourseSubjectTests(unittest.TestCase):
    config = None
    _access_token = None

    @property
    def url(self):
        return self.config['hostname'] + self.config['version'] + self.config['api']

    def access_token(self):
        if self._access_token is None:
            url = self.config['hostname'] + self.config['version'] + self.config["token_endpoint"]
            post_data = {
                'client_id': self.config["client_id"],
                'client_secret': self.config["client_secret"],
                'grant_type': 'client_credentials',
            }
            response = requests.post(url, data=post_data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['content-type'], 'application/json')
            body = response.json()
            self.assertEqual(body['token_type'], 'BearerToken') # XXX should be Bearer
            self._access_token = body["access_token"]
        return self._access_token

    def authorization(self):
        return 'Bearer ' + self.access_token()

    def query(self):
        headers = {'Authorization': self.authorization()}
        return requests.get(self.url, headers=headers)

    def check_ssl(self, protocol, url):
        manager = urllib3.poolmanager.PoolManager(
            ssl_version=protocol)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', urllib3.exceptions.InsecureRequestWarning)
            try:
                manager.request('GET', url)
            except urllib3.exceptions.SSLError:
                return False
            else:
                return True

    def test_success(self):
        """a request return 200 Success and a json object"""
        response = self.query()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/json')

        with open('golden.json') as f:
            golden = json.load(f)

        body = response.json()
        self.assertEqual(body, golden)

    def test_unauth(self):
        """an unauthenticated request returns a 401"""
        response = requests.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_response_time(self):
        """the API responds within five seconds"""
        response = self.query()
        self.assertLess(response.elapsed.total_seconds(), 5)

    def test_tls_v1(self):
        """a call using TLSv1 is successful"""
        self.assertTrue(self.check_ssl(ssl.PROTOCOL_TLSv1, self.url))

    def test_ssl_v2(self):
        """a call using SSLv2 fails"""
        try:
            # if openssl is compiled without ssl support,
            # the PROTOCOL_SSLv2 constant is not available
            ssl.PROTOCOL_SSLv2
        except AttributeError:
            self.skipTest('SSLv2 support not available')
        self.assertFalse(self.check_ssl(ssl.PROTOCOL_SSLv2, self.url))

    def test_ssl_v3(self):
        """a call using SSLv3 fails"""
        self.assertFalse(self.check_ssl(ssl.PROTOCOL_SSLv3, self.url))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--config-path', default='')
    parser.add_argument('unittest_args', nargs='*')
    return parser.parse_args()

if __name__ == '__main__':
    import sys
    _args = parse_args()
    _config = read_config(_args.config_path)

    # unittest isn't terribly well suited to this type of testing
    # because there's no supported way to pass configuration or
    # other parameters into the test cases
    # nevertheless, we use it because it produces nice
    # output messages
    CourseSubjectTests.config = _config # ugh

    unittest.main(argv=[sys.argv[0]] + _args.unittest_args)
