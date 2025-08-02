# model-route-by-reasoning-effort

A Python callback for the LiteLLM proxy that routes requests to different model variants based on reasoning strength (`none`, `low`, `medium`, `high`). This project serves as a bridge between Claude Code and other LLM models, enabling intelligent routing based on task complexity.

## How It Works

This callback intercepts requests to the LiteLLM proxy and routes them to appropriate models based on reasoning requirements:

- **Reasoning strength detection**: The system analyzes both explicit `reasoning_effort` parameters and implicit `thinking.budget_tokens` to determine required reasoning level
- **Model routing**: Requests are automatically routed to models optimized for the required reasoning strength
- **Seamless integration**: Provides a unified interface while leveraging different models for different complexity levels

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
ANTHROPIC_BASE_URL="http://127.0.0.1:4000" ANTHROPIC_AUTH_TOKEN="0000" npx @anthropic-ai/claude-code
```

## Known Issues
- Cerebras supports `tools` and `tool_choice` only with `qwen3-235B-A22B-Instruct-2507`, now. ~~Fastest Supports Please!~~
- Some Function calling failed, because unstable function calling support in other models.
