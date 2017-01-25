# Course Subjects API Integration Tests

This directory contains files that run integration tests against the course subjects API.
To run the tests, use Python.
These libraries are required to run the integration tests:

* [requests](http://docs.python-requests.org/en/master/)
* [urllib3](https://urllib3.readthedocs.io/en/latest/)
* [ngs-httpsclient](https://pypi.python.org/pypi/ndg-httpsclient)
* [pyasn1](https://pypi.python.org/pypi/pyasn1)

Use this command to run the tests:

	python integrationtests.py -i /path/to/configuration.json

Any unittest command line arguments can be specified at the end of the argument list.
For example, this command will run the tests in verbose mode:

	python integrationtests.py -i /path/to/configuration.json -- -v

Successfully passing all the tests with the command above would output this result:

![success_test](images/successful-test.png)

Python Version: 2.7.6

### Docker

This directory contains files that run integration tests against the Course Subjects API.

First, create a configuration.json file from configuration_example.json.

Next, use these commands to build and run the container. All you need installed is Docker.

```shell
$ docker build -t course-subjects-api-tests .
# Run the integration tests in Unix
$ docker run -v "$PWD"/configuration.json:/usr/src/app/configuration.json:ro course-subjects-api-tests
# Run the integration tests in Windows
$ docker run -v c:\path\to\configuration.json:/c:\usr\src\app\configuration.json:ro course-subjects-api-tests
```

Successfully passing all the tests with the command above would output this result:

![success_test_02](images/successful-test-02.png)
