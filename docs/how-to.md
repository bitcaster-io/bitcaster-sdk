---
title: How-to Guide
---

# How-to Guide

## Installation

```bash
pip install bitcaster-sdk
```

## Setup

Set your Bitcaster endpoint as an environment variable:

```bash
export BITCASTER_BAE=https://<API_KEY>@<SERVER>/api/o/<organization_slug>/
```

Or pass the URL directly when creating a client.

## Trigger an event

### Sync

```python
import bitcaster_sdk

bitcaster_sdk.init()
bitcaster_sdk.trigger("project-slug", "application-slug", "event-slug", context={})
```

### Using the `Client` directly

```python
from bitcaster_sdk.client import Client, init

init("https://key@server/api/o/org/")
client = Client("https://key@server/api/o/org/")

client.trigger("project", "app", "event", context={"order_id": "456"})
```

### Async (non-blocking)

```python
from bitcaster_sdk.async_client import AsyncClient

client = AsyncClient("https://key@server/api/o/org/")
client.trigger("project", "app", "event", context={"order_id": "456"})

# Do other work while the request is in-flight
print("Request queued, continuing...")

# Ensure the request completes before exiting
client.flush()
```

## Ping the server

Check connectivity:

```python
from bitcaster_sdk.client import Client

client = Client("https://key@server/api/o/org/")
print(client.ping())
```

Async version:

```python
from bitcaster_sdk.async_client import AsyncClient

client = AsyncClient("https://key@server/api/o/org/")
result = client.ping().result(timeout=10)
print(result)
```

## List resources

### Projects

```python
client = Client("https://key@server/api/o/org/")
for project in client.list_projects():
    print(project["slug"])
```

### Applications

```python
client = Client("https://key@server/api/o/org/")
for app in client.list_applications("my-project"):
    print(app["slug"])
```

### Events

```python
client = Client("https://key@server/api/o/org/")
for event in client.list_events("my-project", "my-app"):
    print(event["name"], event["active"])
```

### Users

```python
client = Client("https://key@server/api/o/org/")
for user in client.list_users():
    print(user["email"], user["is_active"])
```

### Distribution lists and members

```python
client = Client("https://key@server/api/o/org/")
for dl in client.list_distribution_lists("my-project"):
    print(dl["name"], dl["id"])
    for member in client.list_members("my-project", str(dl["id"])):
        print("  ", member["address"])
```

### Async — fire all at once

```python
from bitcaster_sdk.async_client import AsyncClient

client = AsyncClient("https://key@server/api/o/org/")
users_fut = client.list_users()
projects_fut = client.list_projects()
events_fut = client.list_events("my-project", "my-app")

users = users_fut.result(timeout=10)
projects = projects_fut.result(timeout=10)
events = events_fut.result(timeout=10)
```

## Manage users

### Add a user

```python
from bitcaster_sdk.client import Client

client = Client("https://key@server/api/o/org/")
resp = client.add_user("user@example.com", "Jane", "Doe")
print(resp)
```

### Update a user

```python
from bitcaster_sdk.client import Client

client = Client("https://key@server/api/o/org/")
resp = client.update_user("user@example.com", first_name="Jane", last_name="Smith")
print(resp)
```

## Context manager (async)

The `AsyncClient` supports the context manager protocol. The background worker is shut down automatically on exit:

```python
from bitcaster_sdk.async_client import AsyncClient

with AsyncClient("https://key@server/api/o/org/") as client:
    result = client.ping().result(timeout=10)
    print(result)
```

## CLI

The SDK ships with a `bitcaster` command for quick operations:

```bash
# Ping the server
bitcaster ping

# List all users
bitcaster users list

# Trigger an event
bitcaster trigger project-slug application-slug event-slug

# Show help
bitcaster --help
```

Set the endpoint via `--bae` or the `BITCASTER_BAE` environment variable.

## Error handling

The SDK raises typed exceptions for common failure modes:

```python
from bitcaster_sdk.exceptions import (
    AuthenticationError,   # 401
    AuthorizationError,    # 403
    ConfigurationError,    # bad setup
    EventNotFoundError,    # 404
    ValidationError,       # 400
)
```

Example:

```python
from bitcaster_sdk.client import Client
from bitcaster_sdk.exceptions import AuthenticationError

client = Client("https://bad-key@server/api/o/org/")
try:
    client.ping()
except AuthenticationError as e:
    print(f"Auth failed: {e}")
```

With the async client, errors are raised when calling `.result()`:

```python
from bitcaster_sdk.async_client import AsyncClient
from bitcaster_sdk.exceptions import AuthenticationError

client = AsyncClient("https://bad-key@server/api/o/org/")
future = client.ping()
try:
    result = future.result(timeout=10)
except AuthenticationError as e:
    print(f"Auth failed: {e}")
```