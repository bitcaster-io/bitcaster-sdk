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
bitcaster_sdk.set_domain("project-slug", "application-slug")
bitcaster_sdk.trigger_event("event-slug", context={})
```

### Using the `Client` directly

```python
from bitcaster_sdk.client import Client

client = Client("https://key@server/api/o/org/")
client.set_domain("project", "app")
client.trigger_event("event", context={"order_id": "456"})
```

Or set project/application at construction time:

```python
client = Client("https://key@server/api/o/org/", project="project", application="app")
client.trigger_event("event", context={"order_id": "456"})
```

### Async (non-blocking)

```python
from bitcaster_sdk.async_client import AsyncClient

client = AsyncClient("https://key@server/api/o/org/")
client.set_domain("project", "app")
client.trigger_event("event", context={"order_id": "456"})

# Do other work while the request is in-flight
print("Request queued, continuing...")

# Ensure the request completes before exiting
client.flush()
```

For the full API reference see the [Sync Client](client.md) and
[Async Client](async-client.md) pages.

### Publish to a RabbitMQ queue

Trigger events through a RabbitMQ queue consumed by the Bitcaster `AgentAMQP`
monitor instead of the HTTP API. Requires `pip install bitcaster-sdk[amqp]`:

```python
from bitcaster_sdk.rabbit_client import RabbitClient

client = RabbitClient("amqp://user:password@localhost:5672/", queue="bitcaster-events")
client.set_domain("project-slug", "application-slug")
client.trigger_event("event-slug", context={"order_id": "456"})
```

See the [RabbitMQ Client](rabbit-client.md) page for details.

### Publish via CLI to RabbitMQ

Set `BITCASTER_BAE` to an `amqp://` URL and run `trigger`:

```bash
export BITCASTER_BAE=amqp://user:password@localhost:5672/
export BITCASTER_PROJECT=my-project
export BITCASTER_APPLICATION=my-app
bitcaster trigger event-slug --context order_id 456
```

Optionally tune queue/exchange/routing_key via `BITCASTER_QUEUE`,
`BITCASTER_EXCHANGE`, `BITCASTER_ROUTING_KEY`. Only `trigger` and `ping`
work with an AMQP BAE; listing commands raise an error.

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

### Register a user to an application

Register a user as an *Application Member*. The user is created if it does
not exist, per-application custom fields are merged into the membership, and
addresses can be created and assigned to the application's preferred
channels — optionally subscribing the resulting assignments to a
distribution list:

```python
from bitcaster_sdk.client import Client

client = Client("https://key@server/api/o/org/")
resp = client.register_user(
    "my-project",
    "my-app",
    "jane.doe",
    first_name="Jane",
    last_name="Doe",
    email="jane@example.com",
    custom_fields={"badge": 42},
    addresses=[
        {"value": "jane@example.com", "assign_to_preferred_channel": True},
    ],
    distribution_list="operators",  # optional
)
print(resp["created"], resp["membership"], resp["assignments"])
```

Each entry in `addresses` accepts:

| Key | Required | Description |
|---|---|---|
| `value` | yes | The address value (e.g. an email address or phone number) |
| `name` | no | A label for the address (defaults to the address type) |
| `assign_to_preferred_channel` | no | Assign the address to the compatible preferred channels (default `false`) |

### Unregister a user from an application

Remove the user's application membership. Distribution list subscriptions
are not affected:

```python
from bitcaster_sdk.client import Client

client = Client("https://key@server/api/o/org/")
resp = client.unregister_user("my-project", "my-app", "jane.doe")
print(resp["deleted"])  # number of deleted memberships
```

Both methods are also available on the [Async Client](async-client.md)
(returning a `Future`) and as module-level functions:

```python
import bitcaster_sdk

bitcaster_sdk.init()
bitcaster_sdk.register_user("my-project", "my-app", "jane.doe", email="jane@example.com")
bitcaster_sdk.unregister_user("my-project", "my-app", "jane.doe")
```

## Context manager (async)

The `AsyncClient` supports the context manager protocol. The background worker is shut down automatically on exit:

```python
from bitcaster_sdk.async_client import AsyncClient

with AsyncClient("https://key@server/api/o/org/") as client:
    result = client.ping().result(timeout=10)
    print(result)
```

For CLI usage reference, see the [CLI Reference](cli.md).

## Django integration

### Notify Bitcaster on user creation/update via signal

Connect to Django's `post_save` signal for the `User` model to fire a Bitcaster event whenever a user is created or updated:

```python
# your_app/signals.py
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from bitcaster_sdk.async_client import AsyncClient

User = get_user_model()

client = AsyncClient("https://key@server/api/o/org/", project="my-project", application="my-app")


@receiver(post_save, sender=User)
def notify_bitcaster_on_user_save(sender, instance, created, **kwargs):
    event = "user-created" if created else "user-updated"
    client.trigger_event(
        event,
        context={
            "user_id": str(instance.id),
            "email": instance.email,
            "username": instance.username or "",
        },
    )
```

Wire the signal in your app's config:

```python
# your_app/apps.py
from django.apps import AppConfig


class YourAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "your_app"

    def ready(self):
        import your_app.signals  # noqa: F401
```

The `AsyncClient` is ideal here — the signal handler returns immediately while the HTTP request runs in a background thread, keeping your response time fast.

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
