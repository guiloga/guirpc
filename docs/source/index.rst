=======
 guirpc
=======
| Is a **Python** RPC package to build and run FaaS-like application service.
| It facilitates the creation of an consumer or a producer, as well as an abstraction layer for the transmission
  of messages over a connected message broker server.

.. rst-class:: title-note

  updated at January 28, 2021


About RPC
=========
**RPC (Remote Procedure Call**) technically is described as a transport protocol
and stands for a common pattern of communication between applications acting as a client/server pairs.
However it is better thought as a general mechanism closely linked to distributed systems because it meets
the needs of an application that requires an exchange of request / response messages.

This pattern is implemented through a transport layer, usually referred as a **message broker server**, like `RabbitMQ`_.

.. _RabbitMQ: https://www.rabbitmq.com

Simple Request-Reply (RPC) pattern
----------------------------------
There are different patterns in the RPC mechanism but focusing on the Simple RPC, the message transaction
is performed in the following way:

A ``client/producer`` sends a request message that is routed to a long-lived server queue.
The message is consumed by the ``server/consumer`` from the request queue and then
it sends back a response through a response queue to the client.

*The client is blocked until a response is received from the server.*

|

.. image:: _static/img/diagram1.png
   :height: 141
   :width: 641
   :alt: request-reply diagram
   :align: center


About this package
==================
This package implements core functionality that is compliant with the standard **AMQP**.
It provides an interface with some decorators, encoders, serializers and in short all the surrounded layers for easily build,
configure and run an **RPC server** as it makes up as a **FaaS-like application**.

It also provides a command line manager to handle operations that will essentially allow to setup
and run a configured RPC server/consumer that will respond on messages received
trough **RabbitMQ** back to a connected client/producer.


Transport layers
----------------
.. image:: _static/img/rabbitmq.png
   :height: 94
   :width: 214
   :alt: RabbitMQ logo

.. note:: **RabbitMQ** is the unique supported message broker as transport layer in this project (for now).


**Index**: Documentation
========================

.. toctree::
   :maxdepth: 2

   quickstart


**Release:** Development history
================================

.. toctree::
   :maxdepth: 1

- **v0.2 - June 1, 2021**
   - Fixed connection_is_open decorator and added AMQP_URI variable. `b680b7e`_
   - Fixed StreamLostError on Producer creation. `498723e`_

.. _b680b7e: https://github.com/guiloga/guirpc/commit/b680b7e0247aed8ef93438b316f7cc2dc9a5e0e4
.. _498723e: https://github.com/guiloga/guirpc/commit/498723e07ba855bd21c8382c3bf2afffca7045aa

- **v0.1 - February 5, 2021**
   - Initial realease.
