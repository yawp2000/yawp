"""
LLM Provider Abstraction Layer
Unified interface for multiple AI model providers
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    def generate(self, prompt: str, system: Optional[str] = None,
                 max_tokens: int = 4096, temperature: float = 1.0) -> str:
        """Generate completion from prompt"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return model identifier"""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, model: str = "claude-sonnet-4-20250514", api_key: Optional[str] = None):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            self.model = model
        except ImportError:
            raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

    def generate(self, prompt: str, system: Optional[str] = None,
                 max_tokens: int = 4096, temperature: float = 1.0) -> str:
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def get_model_name(self) -> str:
        return f"anthropic/{self.model}"


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""

    def __init__(self, model: str = "gpt-4-turbo-preview", api_key: Optional[str] = None):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = model
        except ImportError:
            raise RuntimeError("openai package not installed. Run: pip install openai")

    def generate(self, prompt: str, system: Optional[str] = None,
                 max_tokens: int = 4096, temperature: float = 1.0) -> str:
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content

    def get_model_name(self) -> str:
        return f"openai/{self.model}"


class GoogleProvider(LLMProvider):
    """Google Gemini provider"""

    def __init__(self, model: str = "gemini-pro", api_key: Optional[str] = None):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
            self.model_obj = genai.GenerativeModel(model)
            self.model = model
        except ImportError:
            raise RuntimeError("google-generativeai package not installed. Run: pip install google-generativeai")

    def generate(self, prompt: str, system: Optional[str] = None,
                 max_tokens: int = 4096, temperature: float = 1.0) -> str:
        # Gemini handles system prompt differently
        full_prompt = f"{system}\n\n{prompt}" if system else prompt

        response = self.model_obj.generate_content(
            full_prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature
            }
        )

        return response.text

    def get_model_name(self) -> str:
        return f"google/{self.model}"


class OllamaProvider(LLMProvider):
    """Ollama local models provider"""

    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate(self, prompt: str, system: Optional[str] = None,
                 max_tokens: int = 4096, temperature: float = 1.0) -> str:
        import requests

        full_prompt = f"{system}\n\n{prompt}" if system else prompt

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            }
        )

        response.raise_for_status()
        return response.json()["response"]

    def get_model_name(self) -> str:
        return f"ollama/{self.model}"


def get_provider(provider_type: str, model: Optional[str] = None,
                 api_key: Optional[str] = None, **kwargs) -> LLMProvider:
    """Factory function to get LLM provider"""

    providers = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "google": GoogleProvider,
        "ollama": OllamaProvider
    }

    if provider_type not in providers:
        raise ValueError(f"Unknown provider: {provider_type}. Available: {list(providers.keys())}")

    provider_class = providers[provider_type]

    # Build kwargs for provider
    init_kwargs = {}
    if model:
        init_kwargs["model"] = model
    if api_key:
        init_kwargs["api_key"] = api_key

    # Add any extra kwargs (like base_url for Ollama)
    init_kwargs.update(kwargs)

    return provider_class(**init_kwargs)


# Predefined model configurations
MODELS = {
    # Anthropic
    "claude-opus": {"provider": "anthropic", "model": "claude-opus-4-20250514"},
    "claude-sonnet": {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
    "claude-haiku": {"provider": "anthropic", "model": "claude-haiku-4-20251001"},

    # OpenAI
    "gpt4": {"provider": "openai", "model": "gpt-4-turbo-preview"},
    "gpt4-turbo": {"provider": "openai", "model": "gpt-4-turbo-preview"},
    "gpt-35": {"provider": "openai", "model": "gpt-3.5-turbo"},

    # Google
    "gemini": {"provider": "google", "model": "gemini-pro"},
    "gemini-pro": {"provider": "google", "model": "gemini-pro"},

    # Ollama (local)
    "llama2": {"provider": "ollama", "model": "llama2"},
    "mistral": {"provider": "ollama", "model": "mistral"},
}


def get_provider_by_name(name: str, api_key: Optional[str] = None) -> LLMProvider:
    """Get provider by friendly name (e.g., 'claude-sonnet', 'gpt4')"""

    if name not in MODELS:
        raise ValueError(f"Unknown model name: {name}. Available: {list(MODELS.keys())}")

    config = MODELS[name]
    return get_provider(config["provider"], config["model"], api_key)


if __name__ == "__main__":
    # Test providers
    import sys

    if len(sys.argv) < 2:
        print("Usage: python llm_provider.py <provider_name>")
        print(f"Available: {list(MODELS.keys())}")
        sys.exit(1)

    provider_name = sys.argv[1]

    try:
        provider = get_provider_by_name(provider_name)
        print(f"Testing {provider.get_model_name()}...")

        response = provider.generate(
            "What is 2+2? Answer in one sentence.",
            system="You are a helpful assistant.",
            max_tokens=100
        )

        print(f"Response: {response}")
        print(f"[OK] {provider_name} working")

    except Exception as e:
        print(f"[FAIL] {provider_name}: {e}")
        sys.exit(1)
