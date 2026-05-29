"""
routers/providers.py
Per-agent AI provider clients for Polynovea M3 Show Engineering Council.

Each agent has its own named API key in .env:
  NVIDIA_API_KEY_NEMOTRON_120B — Agents 1 + 7
  NVIDIA_API_KEY_LLAMA_70B     — Agent 2
  NVIDIA_API_KEY_DEEPSEEK_FLASH — Agent 3
  NVIDIA_API_KEY_QWEN_122B     — Agent 4
  NVIDIA_API_KEY_DEEPSEEK_PRO  — Agent 5
  NVIDIA_API_KEY_MISTRAL_LARGE — Agent 6

Base URL:  NVIDIA_BASE_URL  (default: https://integrate.api.nvidia.com/v1)
"""

import os
from dataclasses import dataclass

from openai import AsyncOpenAI

_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")


@dataclass
class AgentClient:
    client: AsyncOpenAI
    model: str
    name: str


def _make_client(env_key: str, model: str, name: str) -> AgentClient | None:
    key = os.getenv(env_key, "").strip()
    if not key:
        return None
    return AgentClient(
        client=AsyncOpenAI(api_key=key, base_url=_BASE_URL),
        model=model,
        name=name,
    )


def get_nemotron_client() -> AgentClient | None:
    """Nemotron Super 120B — Council R1 proposer + synthesiser + Agents 1 & 7."""
    return _make_client(
        "NVIDIA_API_KEY_NEMOTRON_120B",
        os.getenv("NVIDIA_MODEL_NEMOTRON", "nvidia/nemotron-3-super-120b-a12b"),
        "nemotron",
    )


def get_deepseek_r1_client() -> AgentClient | None:
    """DeepSeek R1 — Council R2 challenger (fast path via Flash)."""
    return _make_client(
        "NVIDIA_API_KEY_DEEPSEEK_FLASH",
        os.getenv("NVIDIA_MODEL_DEEPSEEK_FLASH", "deepseek-ai/deepseek-v4-flash"),
        "deepseek_flash",
    )


def get_deepseek_pro_client() -> AgentClient | None:
    """DeepSeek V4 Pro — Agent 5 Integrator."""
    return _make_client(
        "NVIDIA_API_KEY_DEEPSEEK_PRO",
        os.getenv("NVIDIA_MODEL_DEEPSEEK_PRO", "deepseek-ai/deepseek-v4-pro"),
        "deepseek_pro",
    )


def get_llama_client() -> AgentClient | None:
    """Llama 3.3 70B — Agent 2 Behavioral RAG."""
    return _make_client(
        "NVIDIA_API_KEY_LLAMA_70B",
        os.getenv("NVIDIA_MODEL_LLAMA", "meta/llama-3.3-70b-instruct"),
        "llama_70b",
    )


def get_qwen_client() -> AgentClient | None:
    """Qwen 3.5-122B — Agent 4 Neuroacoustic RAG."""
    return _make_client(
        "NVIDIA_API_KEY_QWEN_122B",
        os.getenv("NVIDIA_MODEL_QWEN", "qwen/qwen3.5-122b-a10b"),
        "qwen_122b",
    )


def get_mistral_client() -> AgentClient | None:
    """Mistral Large — Agent 6 Prescriber."""
    return _make_client(
        "NVIDIA_API_KEY_MISTRAL_LARGE",
        os.getenv("NVIDIA_MODEL_MISTRAL", "mistralai/mistral-large-3-675b-instruct-2512"),
        "mistral_large",
    )
