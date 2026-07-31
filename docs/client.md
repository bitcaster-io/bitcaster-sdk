---
title: Sync Client
---

# Sync Client

The `Client` is the synchronous entry-point to the Bitcaster API. Every method
blocks on the HTTP request and returns the parsed response directly.

## Quick Start

```python
from bitcaster_sdk.client import Client

client = Client("https://key@app.bitcaster.io/api/o/ORG/")
client.set_domain("my-project", "my-app")
result = client.trigger_event("order-placed", context={"order_id": "123"})
```

## API Reference

::: bitcaster_sdk.client.Client
    options:
      show_root_heading: false
      show_source: true
      members:
        - ping
        - list_projects
        - list_applications
        - list_events
        - list_distribution_lists
        - list_members
        - list_users
        - set_domain
        - trigger_event
        - add_user
        - update_user
        - unregister_user
        - base_url
        - api_url
        - last_called_url
