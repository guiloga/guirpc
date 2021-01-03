# guilogacore-rpc
### RPC core package to build a FaaS-like application service
____
[![Build Status](https://www.travis-ci.com/guiloga/guilogacore-rpc.svg?branch=master)](https://www.travis-ci.com/guiloga/guilogacore-rpc)

This package implements core functionality that is compliant with the standard **AMQP**.
It provides an interface with some decorators, encoders, serializers and in short all the surrounded layers for easily build,
configure and run an **RPC server** as it makes up as a **FaaS-like application**.

It also provides a command line manager to handle operations that will essentially allow to setup and run a configured RPC server/consumer that will respond on messages received trough **RabbitMQ** back to a connected client/producer.

## Built With

* [RabbitMQ](https://www.rabbitmq.com/) - The message broker layer
* [Pika](https://pika.readthedocs.io/en/stable/index.html) - RabbitMQ client library

## Prerequisites ###

* Python version [**3.8**](https://www.python.org/downloads/release/python-380/) (with [pip](https://pip.pypa.io/en/stable/))

## Documentation ###

Documentation for the package is not available yet.

## Tests
Tests are built with [pytest](https://docs.pytest.org/en/stable/) and run with docker.
In order tu run it be sure last that current stable versions of docker and docker-compose are installed.

- First, build the *foobar* consumer service and run it alongside a RabbitMQ server(optionally with the management plugin):
```
docker-compose up --build -d rabbitmq consumer
```
- Run all **unit** and **integration** tests:
```
docker-compose run test
```

Optionally, run code static analysis (with flake8):
```
docker-compose run static_analysis
```

### Build

Build the distribution:
```shell script
python -m pip install -U pep517
python -m pep517.build .
```
For development, create a link file which associates source code with your interpreter site-packages directory:
```shell script
touch setup.py
echo "import setuptools
setuptools.setup()" > setup.py
# Then do
pip install --editable .
```
Upload it yo PyPi:
**twine**

## Resources
* [RFC2045](https://tools.ietf.org/html/rfc2045.html) - (MIME) Part One: Format of Internet Message Bodies.

## Authors

* **Guillem López Garcia** - [guiloga](https://github.com/guiloga)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
