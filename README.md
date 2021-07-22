# guirpc :envelope:

_A pre-release is published to PyPi, but a first proper version is still under construction_ :construction_worker:

_It is an RPC core package to build a FaaS-like application service :stuck_out_tongue_winking_eye:_
____
[![Build Status](https://www.travis-ci.com/guiloga/guirpc.svg?branch=master)](https://www.travis-ci.com/guiloga/guirpc)

Is a **Python** RPC package to build and run FaaS-like application service.
It facilitates the creation of a consumer and a producer (a Pub/Sub pattern) providing an abstraction layer
for the transmission of messages over a connected message broker server.

It includes some decorators, encoders, serializers ... and also a CLI application called **guirpc**
for easily build, configure and run an **RPC server** as it makes up as a **FaaS-like application**.

## Built With

* 🐰 [RabbitMQ](https://www.rabbitmq.com/) - The message broker layer
* [Pika](https://pika.readthedocs.io/en/stable/index.html) - RabbitMQ client library

## Prerequisites ###

* Python version [**3.6**](https://www.python.org/downloads/release/python-360/) (
  with [pip](https://pip.pypa.io/en/stable/))

## Documentation ###

Package is distributed under [PyPi](https://pypi.org/). Take a look at the
official [documentation](https://guirpc.readthedocs.io/en/latest/).

Documentation of this project is created with [Sphinx](https://www.sphinx-doc.org/en/master/index.html), to build it
run:

```shell script
pip install -r docs/requirements.txt
sphinx-build -b html docs/source/ docs/build/
```

## Development

Tests are built with [pytest](https://docs.pytest.org/en/stable/) and run with docker. In order tu run it be sure last
that current stable versions of docker and docker-compose are installed.

- First, install *requirements.txt* and development required packages:
```shell script
pip install -r requirement.txt
pip install -U pytest pytest-cov flake8 black
```

- Run a local RabbitMQ server instance for development:
```shell script
docker-compose up -d rabbitmq
```

### Run tests

#### Run tests locally
```shell script
guirpc initconsumer foobar && guirpc initproducer foobar_client
export CONSUMER_CONFIG=foobar.ini
export PRODUCER_CONFIG=foobar_client.ini
export AMQP_URI=amqp://guest:guest@localhost:5672

# Run all tests
pytest
```

#### Run tests with Docker
- Build the *foobar* consumer service and run it alongside a RabbitMQ server(optionally with the management
  plugin):

```shell script
docker-compose up --build -d rabbitmq consumer
```

- Run all **unit** and **integration** tests:

```shell script
docker-compose run test
```

Optionally, run code static analysis (with flake8):

```shell script
docker-compose run static_analysis
```

For development, create a link file which associates source code with your interpreter site-packages directory:

```shell script
touch setup.py
echo "import setuptools
setuptools.setup()" > setup.py
# Then do
pip install --editable .
```

## Resources

* [RFC2045](https://tools.ietf.org/html/rfc2045.html) - (MIME) Part One: Format of Internet Message Bodies.

## Authors

* **Guillem López Garcia** - [guiloga](https://github.com/guiloga)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
