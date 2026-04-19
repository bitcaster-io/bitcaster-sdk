---
title: Bitcaster SDK Documentation
---

# Welcome to the Bitcaster SDK

The **Bitcaster SDK** is the official Python client library for the [Bitcaster](https://github.com/bitcaster-io/bitcaster) notification platform.

It provides a simple, Pythonic interface to interact with the Bitcaster REST API — allowing you to trigger events, manage occurrences, and integrate Bitcaster into any Python or Django application with minimal effort.

## Features

- Simple REST client for the Bitcaster API
- Django integration helpers
- CLI interface via `bitcaster` command
- Support for Python 3.8+

## Quick Start

Install the SDK:

```bash
pip install bitcaster-sdk
```

Trigger an event:

```python
from bitcaster_sdk import BitcasterClient

client = BitcasterClient(
    server="https://your-bitcaster-server",
    token="your-api-token",
)

client.trigger("my-event", payload={"message": "Hello from the SDK!"})
```

## More Information

- [Source Code](https://github.com/bitcaster-io/bitcaster-sdk)
- [Bitcaster Platform](https://github.com/bitcaster-io/bitcaster)
