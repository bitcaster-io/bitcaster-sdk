Bitcaster Python SDK
--------------------


How to use it:

- Setupt environemnt

    
    &#35; Set Bitcaster application-end-point using Bitcaster Key, get it at <bc_instance>/o/<org>/a/<app>/key/
    export BITCASTER_AEP=http://key-xxxxxxxxxxxxxx@app.bitcaster.io/api/o/<org_slug>/a/<application_id>/ 

    
    &#35; Set Bitcaster software-development-token using Bitcaster Token, get it at <bc_instance>/o/<org>/token/
    export BITCASTER_SDT=http://sdk-yyyyyyyyyyyyyy@app.bitcaster.io/api/o/<org_slug>

- in your code


    import bitcaster_sdk 
    bitcaster_sdk.init()

&#8203;

    from bitcaster_sdk import trigget
    trigger(11)
