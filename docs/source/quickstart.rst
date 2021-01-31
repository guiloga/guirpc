===========
 Quickstart
===========

The following sections are outlined to illustrate the installation of the package and the initial creation process of a consumer
and a producer until a first RPC request is made.

To illustrate it we are going to work with a base example creating a consumer named **foobar**
and a producer named **foobar_client**.


Installation
============

Package is distributed under PyPi, so it can be easily installed with pip:

::

  pip install -U guirpc

To install it directly from source:

::

  git clone https://github.com/guiloga/guirpc

  touch setup.py
  echo "import setuptools \
    setuptools.setup()" > setup.py

  python3 setup.py install


Manager
-------
A command-line **manager** application called **guirpc** is provided with the installation of the package.
It has commands that will handle the initialization of pre-created fixtures as starting templates
which will allow to simplify a initial setup of a consumer or a producer.

To check the installation and to take a look at the the list of possible commands:
::

  guirpc --help


Init a consumer
===============
In order to setup the initialization of a **consumer** ``server application`` run the following command:

.. note:: We will call it ``foobar`` consumer in our base example.


::

  guirpc initconsumer foobar

This will generate an .ini configuration file associated with the consumer and a package structure like that one:

::

  foobar
      ├── __init__.py
      ├── server.py
  foobar.ini

Note that this is not forced to be in that structure, the server.py module can be renamed or moved into another location.
The *root* field in the .ini configuration file is the one that points to the consumer server module.


Init a producer
===============
In order to setup the initialization of a **producer** ``client stub`` that will call the consumer methods
that we have created in the previous step run the following command:

.. note:: We will call it ``foobar_client`` producer in our base example.

::

  guirpc initproducer foobar_client

This will generate an .ini configuration file associated with the producer and package structure like that one:

::

  foobar_client
      ├── __init__.py
      ├── client.py
  foobar_client.ini

Note that this is not forced to be in that structure, the client.py can be renamed or moved into another location.
The *root* field in the .ini configuration file is the one that points to the producer client module.


Publish one
===========

