---
title: Async Client
---

# Async Client

The `AsyncClient` provides a non-blocking interface to the Bitcaster API. Every API method returns a [`concurrent.futures.Future`][], allowing your application to continue executing while the request is processed in a background thread.

For shared constructor arguments, properties, and inherited methods see the
[Sync Client](client.md) reference.

## Quick Start

```python
from bitcaster_sdk.async_client import AsyncClient

client = AsyncClient("https://key@app.bitcaster.io/api/o/ORG/")
future = client.ping()
result = future.result(timeout=10)
```

## Motivation

The sync [`Client`][bitcaster_sdk.client.Client] blocks the calling thread on every HTTP request. `AsyncClient` delegates requests to a daemon-thread [`BackgroundWorker`][bitcaster_sdk.async_worker.BackgroundWorker], freeing the caller to do other work while the HTTP round-trip completes.

This is especially useful in:

- **Web applications** (e.g. Django views) where you want to return a response without waiting for the Bitcaster API
- **Event-driven systems** where you fire notifications and move on
- **High-throughput pipelines** that send many independent requests concurrently

## Architecture

```
┌──────────────┐     submit()     ┌──────────────────┐
│ AsyncClient  │ ───────────────► │ AsyncTransport   │
│              │                  │                  │
│  ping()      │   Future[Resp]   │  BackgroundWorker │
│  trigger()   │ ◄─────────────── │  (daemon thread)  │
│  list_*()    │                  │  ┌────────────┐   │
│  add_user()  │                  │  │  Queue     │   │
│  update_user()│                  │  │  (RLock)   │   │
└──────────────┘                  │  └────────────┘   │
                                  └──────────────────┘
                                          │
                                          ▼
                                  ┌──────────────────┐
                                  │  HTTP Session    │
                                  │  (requests)      │
                                  └──────────────────┘
```

## Usage

### Initialisation

```python
client = AsyncClient("https://key@app.bitcaster.io/api/o/ORG/")
```

The `base_url` format is identical to [`Client`][bitcaster_sdk.client.Client]:

```
https://<API_KEY>@<SERVER>/api/o/<organization_slug>/
```

### Non-blocking calls

Every method returns a `Future`. Call `.result(timeout)` to get the actual response:

```python
# Fire and collect later
ping_future = client.ping()
events_future = client.list_events("my-project", "my-app")

# Block only when you need the result
print(ping_future.result(timeout=10))
print(events_future.result(timeout=10))
```

### Context manager

```python
with AsyncClient("https://key@app.bitcaster.io/api/o/ORG/") as client:
    result = client.ping().result(timeout=10)
```

The context manager calls [`close()`](#bitcaster_sdk.async_client.AsyncClient.close) on exit, which flushes pending work and shuts down the background thread.

### Flushing and shutdown

```python
# Wait for all queued requests to complete (default 10s)
client.flush()

# Shut down the background thread
client.close()
```

## API Reference

::: bitcaster_sdk.async_client.AsyncClient
    options:
      show_root_heading: false
      show_source: true
      members:
        - ping
        - list_events
        - list_users
        - list_projects
        - list_applications
        - list_distribution_lists
        - list_members
        - set_domain
        - trigger_event
        - add_user
        - update_user
        - unregister_user
        - flush
        - close

## Examples

### Trigger an event asynchronously

```python
client = AsyncClient("https://key@app.bitcaster.io/api/o/ORG/")
client.set_domain("my-project", "my-app")
future = client.trigger_event("order-placed", context={"order_id": "123"})

# Do other work while the request is in-flight
process_local_task()

# Get the result (blocks if not yet available)
response = future.result(timeout=10)
```

### Concurrent list operations

```python
client = AsyncClient("https://key@app.bitcaster.io/api/o/ORG/")

# Fire all three requests concurrently
users_fut = client.list_users()
projects_fut = client.list_projects()
events_fut = client.list_events("my-project", "my-app")

# Collect results
users = users_fut.result(timeout=10)
projects = projects_fut.result(timeout=10)
events = events_fut.result(timeout=10)
```

## Thread safety

`AsyncClient` is built on a vendored [`Queue`][bitcaster_sdk.async_queue.Queue] with [`RLock`][] and is safe to use from multiple threads. The background worker is fork-safe — if the process forks, a new worker thread is started automatically.
