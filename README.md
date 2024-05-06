Bitcaster Python SDK
--------------------


How to use it:

- Setupt environemnt


    &#35; Set Bitcaster application-end-point using Bitcaster Key, get it at <bc_instance>/o/<org>/a/<app>/key/
    export BITCASTER_BAE=http://key-xxxxxxxxxxxxxx@app.bitcaster.io/api/o/<org_slug>/a/<application_id>/ 

- in your code


    import bitcaster_sdk 
    bitcaster_sdk.init()
    from bitcaster_sdk import trigger
    trigger(11)


