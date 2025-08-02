import os

from litellm.integrations.custom_logger import CustomLogger
from litellm.caching.dual_cache import DualCache
from litellm.proxy.proxy_server import UserAPIKeyAuth
from litellm.types.utils import ModelResponseStream
from typing import Any, AsyncGenerator, Optional, Literal


# This file includes the custom callbacks for LiteLLM Proxy
# Once defined, these can be passed in proxy_config.yaml
class ModelRouteByReasoningStrength(
    CustomLogger
):  # https://docs.litellm.ai/docs/observability/custom_callback#callback-class
    # Class variables or attributes
    def __init__(self):
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
        print("model: " + data.get("model", "unknown"))
        if data["model"] not in self.target_model:
            return data

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
