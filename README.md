Bitcaster Python SDK
--------------------

[![Pypi](https://badge.fury.io/py/bitcaster-sdk.svg)](https://badge.fury.io/py/bitcaster-sdk)
[![coverage](https://codecov.io/github/bitcaster-io/bitcaster-sdk/coverage.svg?branch=develop)](https://codecov.io/github/saxix/django-strategy-field?branch=develop)
[![Test](https://github.com/bitcaster-io/bitcaster-sdk/actions/workflows/test.yml/badge.svg)](https://github.com/bitcaster-io/bitcaster-sdk/actions/workflows/test.yml)
[![Django](https://img.shields.io/pypi/frameworkversions/bitcaster-io/bitcaster-sdk)](https://pypi.org/project/bitcaster-sdk/)


How to use it:

Setupt environemnt

- Set Bitcaster application-end-point using Bitcaster Key, get it at <bc_instance>/o/<org>/a/<app>/key/

    ```
    export BITCASTER_BAE=http://<KEY>@<SERVER>/api/o/<organization_slug>/p/<project_slug>/a/<application_slug>/

    ```

- in your code

    ```
    import bitcaster_sdk
        bitcaster_sdk.init()
        from bitcaster_sdk import trigger
        trigger(11)

    ```



- from command line

    ```
    $ bitcaster
    Usage: bitcaster [OPTIONS] COMMAND [ARGS]...

    Options:
      --bae BAE  Bitcaster BAE. Not needed if $BITCASTER_BAE is set
      --debug
      --help     Show this message and exit.

    Commands:
      events   lists Application's Events
      lists    lists Project's DistributionList
      members  lists DistributionList Members
      ping     ping Bitcaster server
      trigger  trigger Application's Event
      users    displays Organization's Users

    ```
