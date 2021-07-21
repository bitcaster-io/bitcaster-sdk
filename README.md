Bitcaster Python SDK
--------------------


How to use it:

- Setupt environemnt

    
    # Set Bitcaster application-end-point using Bitcaster Key, get it at <bc_instance>/o/<org>/a/<app>/key/
    export BITCASTER_AEP=http://key-xxxxxxxxxxxxxx@<host>:<port>/api/o/<org_slug>/a/<application_id>/ 

    
    # Set Bitcaster software-development-token using Bitcaster Token, get it at <bc_instance>/o/<org>/token/
    export BITCASTER_SDT=http://sdk-yyyyyyyyyyyyyy@<host>:<port>/api/o/<org_slug>

- in your code


    import bitcaster_sdk
    
    bitcaster_sdk.init()
    from bitcaster_sdk import  trigger, ping
    
    trigger(
