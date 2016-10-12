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
    maxDiff = None

    KNOWN_SUBJECTS = [
        "ART", # Art
        "BI", # Biology
        "CH", # Chemistry
        "CE", # Civil ENgineering
        "COMM", # Communication
        "CS", # Computer Science
        "ECE", # Electrical & Computer Engineer
        "ENGR", # Engineering
        "FOR", # Forestry
        "GEO", # Geosciences
        "LA", # Liberal Arts
        "LS", # Liberal Studies
        "MTH", # Mathematics
        "ME", # Mechanical Engineering
        "MUS", # Music
        "OC", # Oceanography
        "PHL", # Philosophy
        "PH", # Physics
        "PSY", # Psychology
        "H" # Public Health
        "ST", # Statistics
        "WR", # Written English
    ]

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

    @staticmethod
    def check_subject(subject):
        """checks if a subject is valid. returns an error string or None"""
        if type(subject) is not dict:
            return 'expected an object'

        if not {'id', 'type', 'attributes'}.issubset(subject.keys()):
            return 'missing id, type, or attributes'

        if type(subject['attributes']) is not dict:
            return 'expected attributes to be an object'

        if not {'abbreviation', 'title'}.issubset(subject['attributes'].keys()):
            return 'missing abbreviation or title'


        if subject['type'] != 'subjects':
            return 'type != "subject"'

        if subject['id'] != subject['attributes']['abbreviation']:
            return 'expected id and abbreviation to be the same'

        if not subject['attributes']['title']:
            return 'empty title'

        return None

    def test_success(self):
        """a request return 200 Success and a json object"""
        response = self.query()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/json')

        body = response.json()

        self.assertEqual(set(body.keys()), {'data', 'links'})

        # Check that all the returned subjects are valid
        invalid_subjects = []
        for subject in body['data']:
            try:
                error = self.check_subject(subject)
            except Exception as e:
                error = '%s: %s' % (type(e).__name__, e)

            if error is not None:
                invalid_subjects.append((subject, error))

        self.assertEqual([], invalid_subjects)

        # Check that a smattering of standard subjects are present
        subject_codes = {subject['id'] for subject in body['data']}
        missing_subjects = [code for code in self.KNOWN_SUBJECTS if code not in subject_codes]

        self.assertEqual([], missing_subjects)

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
            # openssl can be compiled without SSLv2 support, in which case
            # the PROTOCOL_SSLv2 constant is not available
            ssl.PROTOCOL_SSLv2
        except AttributeError:
            self.skipTest('SSLv2 support not available')
        self.assertFalse(self.check_ssl(ssl.PROTOCOL_SSLv2, self.url))

    def test_ssl_v3(self):
        """a call using SSLv3 fails"""
        try:
            # openssl can be compiled without SSLv3 support, in which case
            # the PROTOCOL_SSLv3 constant is not available
            ssl.PROTOCOL_SSLv3
        except AttributeError:
            self.skipTest('SSLv3 support not available')
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
