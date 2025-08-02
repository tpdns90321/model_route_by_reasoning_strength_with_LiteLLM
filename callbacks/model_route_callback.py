import os

from litellm.integrations.custom_logger import CustomLogger
from litellm.caching.dual_cache import DualCache
from litellm.proxy.proxy_server import UserAPIKeyAuth
from litellm.types.utils import ModelResponseStream
from typing import Any, AsyncGenerator, Optional, Literal


def delete_unsupported_parameters_recursively(input_schema: dict):
    if input_schema["type"] == "object":
        for props in input_schema["properties"]:
            delete_unsupported_parameters_recursively(input_schema["properties"][props])
    elif input_schema["type"] == "array":
        delete_unsupported_parameters_recursively(input_schema["items"])
        if "minItems" in input_schema:
            input_schema["description"] += (
                "(minimum number of items is " + str(input_schema["minItems"]) + ")"
            )
            del input_schema["minItems"]
    # finding format parameter
    if "format" in input_schema:
        input_schema["description"] += "(format is " + input_schema["format"] + ")"
        del input_schema["format"]

    if "minLength" in input_schema:
        if "description" not in input_schema:
            input_schema["description"] = ""
        input_schema["description"] += (
            "(minimum length is " + str(input_schema["minLength"]) + ")"
        )
        del input_schema["minLength"]


"""
A LiteLLM proxy callback that routes requests to different model variants based on reasoning strength.

This callback intercepts incoming requests and routes them to appropriate models based on the required
reasoning effort, enabling intelligent model selection for different task complexities.

The routing decisions are based on:
- Explicit `reasoning_effort` parameter ('low', 'medium', 'high')
- Implicit `thinking.budget_tokens` in the request payload
  - < 8,000 tokens: low reasoning
  - < 16,000 tokens: medium reasoning
  - >= 16,000 tokens: high reasoning

Usage:
1. Add to proxy_config.yaml:
```yaml
callbacks:
  - callbacks.model_route_callback.proxy_handler_instance
```

2. Make requests with reasoning parameters:
```python
# Using explicit reasoning effort
client.chat.completions.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "..."}],
    reasoning_effort="high"
)

# Using thinking budget tokens
client.chat.completions.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "..."}],
    thinking={
        "budget_tokens": 20000,
        "type": "enabled"
    }
)
```

Environment Variables:
- LITELLM_PROXY_REASONING_STRENGTH_ROUTE_MODEL: Target model to trigger routing (default: claude-sonnet-4-20250514)
- LITELLM_PROXY_NONE_REASONING_MODEL: Model for no reasoning tasks (default: none-reasoning)
- LITELLM_PROXY_LOW_REASONING_MODEL: Model for low reasoning tasks (default: low-reasoning)
- LITELLM_PROXY_MEDIUM_REASONING_MODEL: Model for medium reasoning tasks (default: medium-reasoning)
- LITELLM_PROXY_HIGH_REASONING_MODEL: Model for high reasoning tasks (default: high-reasoning)
"""


class ModelRouteByReasoningStrength(CustomLogger):
    def __init__(self):
        self.disable_parameter = (
            os.getenv("LITELLM_PROXY_DISABLE_PARAMETER", "false").lower() == "true"
        )
        self.target_model = os.getenv(
            "LITELLM_PROXY_REASONING_STRENGTH_ROUTE_MODEL", "claude-sonnet-4-20250514"
        )  # Default model for reasoning strength routing(claude code)
        self.none_model = os.getenv(
            "LITELLM_PROXY_NONE_REASONING_MODEL", "none-reasoning"
        )
        self.low_model = os.getenv("LITELLM_PROXY_LOW_REASONING_MODEL", "low-reasoning")
        self.medium_model = os.getenv(
            "LITELLM_PROXY_MEDIUM_REASONING_MODEL", "medium-reasoning"
        )
        self.high_model = os.getenv(
            "LITELLM_PROXY_HIGH_REASONING_MODEL", "high-reasoning"
        )

    #### CALL HOOKS - proxy only ####

    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal[
            "completion",
            "text_completion",
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription",
            "pass_through_endpoint",
            "rerank",
        ],
    ):
        if data["model"] not in self.target_model:
            return data

        if self.disable_parameter:
            # Iterate data structure without message parameters
            for data_key in list(data.keys()):
                if data_key == "tools":
                    for tool in data["tools"]:
                        delete_unsupported_parameters_recursively(tool["input_schema"])

        reasoning_effort: Literal[None, "low", "medium", "high"] = data.get(
            "reasoning_effort"
        )
        thinking = data.get("thinking")

        reasoning_strength: Literal["none", "low", "medium", "high"] = "none"
        if reasoning_effort is not None:
            reasoning_strength = reasoning_effort
        elif thinking is not None:
            if thinking.get("type", "") != "enabled":
                reasoning_strength = "none"
            elif thinking.get("budget_tokens") is not None:
                if thinking["budget_tokens"] < 8000:
                    reasoning_strength = "low"
                elif thinking["budget_tokens"] < 16000:
                    reasoning_strength = "medium"
                else:
                    reasoning_strength = "high"

        data["model"] = self.none_model
        if reasoning_strength != "none":
            data["model"] = self.low_model
            if reasoning_strength == "medium":
                data["model"] = self.medium_model
            elif reasoning_strength == "high":
                data["model"] = self.high_model

        return data

    async def async_post_call_failure_hook(
        self,
        request_data: dict,
        original_exception: Exception,
        user_api_key_dict: UserAPIKeyAuth,
        traceback_str: Optional[str] = None,
    ):
        pass

    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response,
    ):
        pass

    async def async_moderation_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        call_type: Literal[
            "completion",
            "text_completion",
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription",
            "responses",
        ],
    ):
        pass

    async def async_post_call_streaming_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        response: str,
    ):
        pass

    async def async_post_call_streaming_iterator_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        response: Any,
        request_data: dict,
    ) -> AsyncGenerator[ModelResponseStream, None]:
        """
        Passes the entire stream to the guardrail

        This is useful for plugins that need to see the entire stream.
        """
        async for item in response:
            yield item


proxy_handler_instance = ModelRouteByReasoningStrength()
