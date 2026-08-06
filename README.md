# Bitcaster Python SDK

[![Test](https://github.com/bitcaster-io/bitcaster-sdk/actions/workflows/test.yml/badge.svg)](https://github.com/bitcaster-io/bitcaster-sdk/actions/workflows/test.yml)
[![codecov](https://codecov.io/github/bitcaster-io/bitcaster-sdk/graph/badge.svg?token=gZTNDaXB57)](https://codecov.io/github/bitcaster-io/bitcaster-sdk)
[![Pypi](https://badge.fury.io/py/bitcaster-sdk.svg)](https://badge.fury.io/py/bitcaster-sdk)

Python client for the [Bitcaster](https://bitcaster.io) event notification platform.

## Quick start

Set your Bitcaster API endpoint:

```
export BITCASTER_BAE=https://<API_KEY>@<SERVER>/api/o/<organization_slug>/
```

You can embed a default project and application in the BAE via query parameters:

```
export BITCASTER_BAE=https://<API_KEY>@<SERVER>/api/o/<organization_slug>/?project=my-project&application=my-app
```

### Sync client

```python
from bitcaster_sdk import Client

client = Client("https://<API_KEY>@<SERVER>/api/o/<organization_slug>/")
# Or with defaults baked in:
client = Client("https://<API_KEY>@<SERVER>/api/o/<organization_slug>/?project=my-project&application=my-app")
client.set_domain("my-project", "my-app")

result = client.trigger_event("order.created", context={"id": "abc-123"})
print(result)

users = client.list_users()
events = client.list_events("my-project", "my-app")
projects = client.list_projects()
```

### Async client (non-blocking)

```python
from bitcaster_sdk import AsyncClient

with AsyncClient("https://<API_KEY>@<SERVER>/api/o/<organization_slug>/") as client:
    client.set_domain("my-project", "my-app")
    future = client.trigger_event("order.created", context={"id": "abc-123"})
    result = future.result(timeout=10)
    print(result)
```

The async client runs HTTP requests on a background thread. The context manager ensures clean shutdown.

### Module-level API (quick scripts)

```python
import bitcaster_sdk

bitcaster_sdk.init()  # reads BITCASTER_BAE env var
bitcaster_sdk.set_domain("my-project", "my-app")

result = bitcaster_sdk.trigger_event("order.created")
users = bitcaster_sdk.list_users()
```

## CLI

```bash
# Check connectivity
bitcaster ping

# Trigger an event
bitcaster trigger --project my-project --application my-app event-slug \
  --context order_id abc-123

# List resources
bitcaster projects
bitcaster applications --project my-project
bitcaster events --project my-project --application my-app
bitcaster users list

# Start a fake dev server
bitcaster serve --port 9000
```

See the [CLI reference](docs/cli.md) for full documentation.
