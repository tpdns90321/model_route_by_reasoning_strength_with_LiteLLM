# model-route-by-reasoning-effort

A Python callback for the LiteLLM proxy that routes requests to different model variants based on reasoning strength (`none`, `low`, `medium`, `high`). This project serves as a bridge between Claude Code and other LLM providers, enabling intelligent routing based on task complexity.

## How It Works

This callback intercepts requests to the LiteLLM proxy and routes them to appropriate models based on reasoning requirements:

- **Reasoning strength detection**: Analyzes explicit `reasoning_effort` or `thinking.budget_tokens` to determine level
- **Model routing**: Routes to provider-specific model IDs configured for each strength
- **Seamless integration**: Unified interface across multiple providers

## Installation

```bash
uv sync
```

## Usage

Configure your LiteLLM proxy to load this callback in your `proxy_config.yaml`:

```yaml
callbacks:
  - callbacks.model_route_callback.proxy_handler_instance
``` 

### Provider Example: Cerebras

```yaml
# test_config_for_cerebras.yaml
model_list:
  - model_name: claude-sonnet-4-20250514
    litellm_params:
      model: claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
  - model_name: none-reasoning
    litellm_params:
      model: cerebras/qwen-3-coder-480b
      api_key: os.environ/CERABRAS_API_KEY
  - model_name: low-reasoning
    litellm_params:
      model: cerebras/qwen-3-235b-a22b-thinking-2507
      api_key: os.environ/CERABRAS_API_KEY
  - model_name: medium-reasoning
    litellm_params:
      model: cerebras/qwen-3-235b-a22b-thinking-2507
      api_key: os.environ/CERABRAS_API_KEY
  - model_name: high-reasoning
    litellm_params:
      model: cerebras/qwen3-235b-a22b-thinking-2507
      api_key: os.environ/CERABRAS_API_KEY
litellm_settings:
  callbacks: callbacks.model_route_callback.proxy_handler_instance
  drop_params: true
```

### Provider Example: OpenRouter + Cerebras

```yaml
# test_config_for_cerebras_openrouter.yaml
model_list:
  - model_name: claude-sonnet-4-20250514
    litellm_params:
      model: claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
  - model_name: none-reasoning
    litellm_params:
      model: openrouter/qwen/qwen3-coder
      api_key: os.environ/OPENROUTER_API_KEY
      provider:
        order: ["cerebras"]
  - model_name: low-reasoning
    litellm_params:
      model: openrouter/qwen/qwen3-235b-a22b-thinking-2507
      api_key: os.environ/OPENROUTER_API_KEY
      provider:
        order: ["cerebras"]
  - model_name: medium-reasoning
    litellm_params:
      model: openrouter/qwen/qwen3-235b-a22b-thinking-2507
      api_key: os.environ/OPENROUTER_API_KEY
      provider:
        order: ["cerebras"]
  - model_name: high-reasoning
    litellm_params:
      model: openrouter/qwen/qwen3-235b-a22b-thinking-2507
      api_key: os.environ/OPENROUTER_API_KEY
      provider:
        order: ["cerebras"]
litellm_settings:
  callbacks: callbacks.model_route_callback.proxy_handler_instance
  drop_params: true
``` 

### Provider Example: OpenAI

```yaml
# test_config_for_openai.yaml
model_list:
  - model_name: claude-sonnet-4-20250514
    litellm_params:
      model: claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
  - model_name: none-reasoning
    litellm_params:
      model: openai/o4-mini
      api_key: os.environ/OPENAI_API_KEY
      reasoning_effort: low
  - model_name: low-reasoning
    litellm_params:
      model: openai/o4-mini
      api_key: os.environ/OPENAI_API_KEY
      reasoning_effort: medium
  - model_name: medium-reasoning
    litellm_params:
      model: openai/o4-mini
      api_key: os.environ/OPENAI_API_KEY
      reasoning_effort: high
  - model_name: high-reasoning
    litellm_params:
      model: openai/o3
      api_key: os.environ/OPENAI_API_KEY
      reasoning_effort: high
litellm_settings:
  callbacks: callbacks.model_route_callback.proxy_handler_instance
  drop_params: true
``` 

## Environment Variables

- `LITELLM_PROXY_REASONING_STRENGTH_ROUTE_MODEL` (default: `claude-sonnet-4-20250514`)
- `LITELLM_PROXY_NONE_REASONING_MODEL` (default: `none-reasoning`)
- `LITELLM_PROXY_LOW_REASONING_MODEL` (default: `low-reasoning`)
- `LITELLM_PROXY_MEDIUM_REASONING_MODEL` (default: `medium-reasoning`)
- `LITELLM_PROXY_HIGH_REASONING_MODEL` (default: `high-reasoning`)
- `LITELLM_PROXY_CEREBRAS_PROVIDER` (default: `false`)
- `LITELLM_PROXY_OPENROUTER_PROVIDER` (default: `false`)

## Testing

Sample config: `test_config_for_cerebras.yaml`, `test_config_for_cerebras_openrouter.yaml`, `test_config_for_openai.yaml`

## Run

```bash
uv run litellm --config test_config_for_cerebras.yaml
ANTHROPIC_BASE_URL="http://127.0.0.1:4000" ANTHROPIC_AUTH_TOKEN="0000" npx @anthropic-ai/claude-code
```