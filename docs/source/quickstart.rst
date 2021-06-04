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


| Note that this is not forced to be in that structure, the server.py module can be renamed or moved into another location.
| The *root* field in the .ini configuration file is the one that points to the consumer server module.


Init a producer
===============
| In order to setup the initialization of a **producer** ``client stub`` that will call the consumer methods
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

| Note that this is not forced to be in that structure, the client.py can be renamed or moved into another location.
| The *root* field in the .ini configuration file is the one that points to the producer client module.


Make an RPC request
===================
| Before moving to make a first RPC request we need to setup some requirements, let's dive in.

Message Broker
--------------
| To put everything to work first of all we are going to run a local RabbitMQ server using docker:

::

    docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:management-alpine

| The *management* tag of the `RabbitMQ Docker Image`_ ships with the `management plugin`_ exposing it
  in its default port 15672 which is very useful as it serves as a control plane of the server.

.. _RabbitMQ Docker Image: https://hub.docker.com/_/rabbitmq/

.. _management plugin: https://www.rabbitmq.com/management.html

Preliminary notes
-----------------
| Take a look at both .ini configuration files. The [server.connection] section set the connection parameters
  to the RabbitMQ server. In our base example we are going to connect it to the local RabbitMQ server,
  we have not modified or added any extra settings so the default connection URI is: **guest:guest@localhost:5672**.

.. note:: Alternatively to avoid declaring the connection parameters in the configuration file,
          the connection uri can be globally set by the **AMQP_URI** environment variable.
          (i.e AMQP_URI="amqp/guest:guest@localhost:5672/%2F")

Configure and Run the **Server Consumer**
-----------------------------------------
| Ensure that the environment variable **CONSUMER_CONFIG** is set and
  points to the path of he *foobar.ini* file.

| Export it directly in the current bash or within the ~/.bashrc file:

::

    echo "export CONSUMER_CONFIG=<path-to-foobar.ini>" >> ~/.bashrc

| Run a worker instance of the consumer with the established configuration:

::

    guirpc runconsumer

Configure the **Client Stub**
-----------------------------
| Ensure that the environment variable **PRODUCER_CONFIG** is set and
  points to the path of the *foobar_client.ini* file.

| Export it directly in the current bash or within the ~/.bashrc file:

::

    echo "export PRODUCER_CONFIG=<path-to-foobar_client.ini>" >> ~/.bashrc


.. note:: The **guirpc.amqp.utils.ClientConnector** class accepts an argument that is the name of
          the environment variable that points the the .ini configuration file.
          The default variable name is **PRODUCER_CONFIG**.

Let's put it all together
-------------------------
| Now to we are going to consume our service. To illustrate it, the following code is a python script in which we import
 the client stub module making calls to our producer functions which ones passes requests to the *foobar_sum* and
 *foobar_count* ``registered FaaS`` in our consumer.

.. code-block:: python

    #!/usr/bin/env python

    from foobar_client import client


    def make_request1():
        sum_body = {'foo': 5, 'bar': 12}
        print(f"RPC Request to 'foobar_sum'")
        print(f"\tbody: {sum_body}")
        x_resp = client.foobar_sum(sum_body)
        if x_resp.is_error:
            print(f"\tResponse error: {x_resp.error_message}")

        print(f"\tResponse success: {x_resp.object}")
        res = x_resp.object['result']
        assert res == 17


    def make_request2():
        sentence = 'foobar!'*5 # 10 foo bar counts
        print(f"RPC Request to 'foobar_count'")
        print(f"\tbody: {sentence}")
        x_resp = client.foobar_count(sentence)
        if x_resp.is_error:
            print(f"\tResponse error: {x_resp.error_message}")

        print(f"\tResponse success: {x_resp.object}")
        res = int(x_resp.object)
        assert res == 10


    def main():
        make_request1()
        make_request2()


    if __name__ == '__main__':
        main()


.. note:: Look at the consumer log stream to see how the messages are received;
          making an acknowledgement when it is received immediately by the consumer and
          then passing trough the registered function (consuming it) and sending a reply to the client.