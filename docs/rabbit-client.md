---
title: RabbitMQ Client
---

# RabbitMQ Client

The `RabbitClient` publishes events to a RabbitMQ queue in a format
compatible with the Bitcaster `AgentAMQP` monitor agent. No HTTP call is
made: the event message sits in the queue until the AMQP agent picks it up
and triggers the corresponding Bitcaster event.

Requires the optional `amqp` extra:

```bash
pip install bitcaster-sdk[amqp]
```

## Message format

Each published message is a JSON object:

```json
{
  "event": "order-placed",
  "data": { "order_id": "456" }
}
```

- `event` — the event slug (configurable via the `event_field` argument).
- `data` — the event context.

The Bitcaster AMQP agent resolves the event against the application of its
monitor, so the message carries no project/application information. Bind
this client to the application that owns the events with `set_domain()`
(or pass `project`/`application` to the constructor), and configure the
agent's queue and `event_field` to match.

## Usage

```python
from bitcaster_sdk.rabbit_client import RabbitClient

client = RabbitClient(
    "amqp://user:password@localhost:5672/",
    queue="bitcaster-events",
    exchange="",          # optional
    routing_key="",       # optional
    event_field="event",  # must match the agent config
)
client.set_domain("my-project", "my-app")
client.trigger_event("order-placed", context={"order_id": "456"})
```

`ping()` verifies connectivity with the RabbitMQ server:

```python
print(client.ping())
# {'connected': True, 'host': 'localhost', 'port': 5672, 'virtual_host': '/', 'queue': 'bitcaster-events', 'exchange': ''}
```

The HTTP-only methods (`list_projects`, `list_users`, `add_user`, ...) are
not available on this client and raise `NotImplementedError`; use the
[Sync Client](client.md) for the REST API.
