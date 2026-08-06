---
title: CLI Reference
---

# CLI Reference

The SDK ships with a `bitcaster` command for quick operations from the terminal.

## Setup

Authentication uses a **BAE** (Bitcaster API Endpoint) — a URL that embeds the API key and organization:

```
https://<API_KEY>@<SERVER>/api/o/<organization_slug>/
```

You can also embed a default project and application via query parameters:

```
https://<API_KEY>@<SERVER>/api/o/<organization_slug>/?project=my-project&application=my-app
```

Provide it via the `BITCASTER_BAE` environment variable or the `--bae` flag:

```bash
export BITCASTER_BAE=https://key@server/api/o/org/
bitcaster ping
```

```bash
bitcaster --bae https://key@server/api/o/org/ ping
```

When the BAE includes `?project=...&application=...`, the `--project` / `-p` and `--application` / `-a` flags become optional on `events` and `trigger` commands.

## Global options

| Option | Env var | Description |
|---|---|---|
| `--bae BAE` | `BITCASTER_BAE` | Bitcaster API endpoint |
| `--debug` | `BITCASTER_DEBUG` | Enable debug logging |
| `--json` | — | Output raw JSON instead of formatted tables |

## Commands

### `bitcaster ping`

Check connectivity to the Bitcaster server:

```bash
bitcaster ping
```

### `bitcaster projects`

List all projects in the organization:

```bash
bitcaster projects
```

### `bitcaster applications`

List all applications for a project:

```bash
bitcaster applications --project my-project
```

Short form: `bitcaster applications -p my-project`

### `bitcaster events`

List all events for an application:

```bash
bitcaster events --project my-project --application my-app
```

Short form: `bitcaster events -p my-project -a my-app`

Shows event name, slug, active/locked status, and description.

### `bitcaster lists`

List all distribution lists for a project:

```bash
bitcaster lists --project my-project
```

### `bitcaster members`

List members of a distribution list:

```bash
bitcaster members --project my-project --distribution <list-id>
```

Short form: `bitcaster members -p my-project -d <list-id>`

### `bitcaster trigger`

Trigger an event with optional context and options:

```bash
bitcaster trigger --project my-project --application my-app event-slug
```

Pass context key-value pairs:

```bash
bitcaster trigger -p my-project -a my-app event-slug \
  --context order_id abc-123 \
  --context amount 42.50
```

Pass options (additional payload):

```bash
bitcaster trigger -p my-project -a my-app event-slug \
  --options priority high
```

Use `-vv` for verbose output that shows the context and options being sent.

Project and application can also be set via environment variables so they don't need to be repeated:

```bash
export BITCASTER_PROJECT=my-project
export BITCASTER_APPLICATION=my-app
bitcaster trigger event-slug
```

### `bitcaster users`

Manage organization users.

#### `bitcaster users list`

List all users:

```bash
bitcaster users list
```

#### `bitcaster users add`

Add a new user:

```bash
bitcaster users add user@example.com
```

With optional fields:

```bash
bitcaster users add user@example.com --first-name Jane --last-name Doe
```

#### `bitcaster users update`

Update an existing user:

```bash
bitcaster users update user@example.com --first-name Jane --last-name Smith
```

Custom fields can be updated as a JSON string. The `--mode` flag controls how custom fields are merged:

```bash
bitcaster users update user@example.com --custom '{"role": "admin"}' --mode merge
```

Available modes: `ignore` (default), `merge`, `override`, `remove`.

### `bitcaster serve`

Start a fake Bitcaster server for development. Dumps all incoming requests to stdout:

```bash
bitcaster serve --port 9000
```

Customise the response:

```bash
bitcaster serve --port 9000 --response-code 201 --response-body '{"id": "abc"}'
```

## Environment variable reference

| Variable | Used by |
|---|---|
| `BITCASTER_BAE` | `--bae` |
| `BITCASTER_PROJECT` | `--project` / `-p` on `events`, `trigger`, `lists`, `members` |
| `BITCASTER_APPLICATION` | `--application` / `-a` on `events`, `trigger` |
| `BITCASTER_DEBUG` | `--debug` |

### RabbitMQ (AMQP) BAE

When `BITCASTER_BAE` starts with `amqp://` the CLI uses a RabbitMQ
client instead of the HTTP API. Only the `trigger` and `ping` commands
are available; listing commands raise an error.

Additional environment variables for the AMQP transport:

| Variable | Default | Used by |
|---|---|---|
| `BITCASTER_QUEUE` | `bitcaster` | Queue name to publish to |
| `BITCASTER_EXCHANGE` | `""` | Exchange name (optional) |
| `BITCASTER_ROUTING_KEY` | `""` | Routing key when binding the queue |
| `BITCASTER_EVENT_FIELD` | `event` | JSON field that holds the event slug |

Example:

```bash
export BITCASTER_BAE=amqp://user:password@localhost:5672/
export BITCASTER_PROJECT=my-project
export BITCASTER_APPLICATION=my-app
export BITCASTER_QUEUE=my-events
bitcaster trigger order-placed --context order_id 456
```
