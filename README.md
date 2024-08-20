Bitcaster Python SDK
--------------------


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
