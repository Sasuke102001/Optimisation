from __future__ import annotations

import os
from typing import TypeVar

import instructor
from openai import OpenAI
from pydantic import BaseModel


SchemaT = TypeVar("SchemaT", bound=BaseModel)


class OpenAIStructuredExtractor:
    def __init__(self, model: str = "gpt-4.1-mini", api_key_env: str = "OPENAI_API_KEY", base_url: str | None = None) -> None:
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise RuntimeError(f"{api_key_env} is not set")
        self.client = instructor.from_openai(OpenAI(api_key=api_key, base_url=base_url))
        self.model = model

    def extract(self, prompt: str, schema: type[SchemaT]) -> SchemaT:
        return self.client.chat.completions.create(
            model=self.model,
            response_model=schema,
            messages=[{"role": "user", "content": prompt}],
        )


class NvidiaStructuredExtractor(OpenAIStructuredExtractor):
    def __init__(self, model: str = "deepseek-ai/deepseek-v4-pro", base_url: str | None = None) -> None:
        resolved_base_url = base_url or os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        super().__init__(model=model, api_key_env="NVIDIA_API_KEY", base_url=resolved_base_url)


def build_structured_extractor(provider: str, model: str = "", base_url: str = "") -> OpenAIStructuredExtractor | NvidiaStructuredExtractor | None:
    if provider == "none":
        return None
    if provider == "openai":
        return OpenAIStructuredExtractor(model=model or "gpt-4.1-mini", base_url=base_url or None)
    if provider == "nvidia":
        return NvidiaStructuredExtractor(model=model or "deepseek-ai/deepseek-v4-pro", base_url=base_url or None)
    raise ValueError(f"Unsupported llm provider: {provider}")
