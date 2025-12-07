Bitcaster Python SDK
--------------------

[![Test](https://github.com/bitcaster-io/bitcaster-sdk/actions/workflows/test.yml/badge.svg)](https://github.com/bitcaster-io/bitcaster-sdk/actions/workflows/test.yml)
[![codecov](https://codecov.io/github/bitcaster-io/bitcaster-sdk/graph/badge.svg?token=gZTNDaXB57)](https://codecov.io/github/bitcaster-io/bitcaster-sdk)
[![Pypi](https://badge.fury.io/py/bitcaster-sdk.svg)](https://badge.fury.io/py/bitcaster-sdk)


How to use it:

Setupt environemnt

- Set Bitcaster application-end-point using Bitcaster Key, get it at <bc_instance>/o/<org>/a/<app>/key/

    ```
    export BITCASTER_BAE=http://<KEY>@<SERVER>/api/o/<organization_slug>/

    ```

- in your code

    ```
    import bitcaster_sdk
        bitcaster_sdk.init()
        from bitcaster_sdk import trigger
        trigger(
            "project-slug", "application-slug", "event-slug",
            context={}
        )

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
