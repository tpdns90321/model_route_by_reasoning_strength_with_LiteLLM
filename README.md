# model-route-by-reasoning-effort

A Python callback for the LiteLLM proxy that routes requests to different model variants based on reasoning strength (`none`, `low`, `medium`, `high`).

## Installation

```bash
uv sync
```

## Usage

Configure your LiteLLM proxy to load this callback:

```yaml
# proxy_config.yaml
callbacks:
  - callbacks.model_route_callback.proxy_handler_instance
```

Optionally override target model IDs via environment variables:

- `LITELLM_PROXY_REASONING_STRENGTH_ROUTE_MODEL` (default: `claude-sonnet-4-20250514`)
- `LITELLM_PROXY_NONE_REASONING_MODEL` (default: `none-reasoning`)
- `LITELLM_PROXY_LOW_REASONING_MODEL` (default: `low-reasoning`)
- `LITELLM_PROXY_MEDIUM_REASONING_MODEL` (default: `medium-reasoning`)
- `LITELLM_PROXY_HIGH_REASONING_MODEL` (default: `high-reasoning`)

## Testing

Sample config: `test_config.yaml`

## Run
```bash
uv run litellm --config test_config.yaml
```
