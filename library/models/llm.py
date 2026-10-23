import os
from typing import Callable

from dotenv import load_dotenv

from langchain_core.language_models import BaseChatModel

from library.models.base import LLMProvider

# Reads environment variables from .env file if present, so that LLM_PROVIDER and LLM_MODEL can be set there instead of in the shell.
load_dotenv()

DEFAULT_LLM_PROVIDER = os.getenv("LLM_PROVIDER", os.getenv("DEFAULT_LLM_PROVIDER"))

# One factory per provider; imports are lazy so unused SDKs needn't be installed

def _ollama(model: str, **kwargs) -> BaseChatModel:
    from langchain_ollama import ChatOllama
    return ChatOllama(model=model, **kwargs)


def _openai(model: str, **kwargs) -> BaseChatModel:
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model=model, **kwargs)


def _bedrock(model: str, **kwargs) -> BaseChatModel:
    from langchain_aws import ChatBedrockConverse
    return ChatBedrockConverse(model=model, region_name=os.getenv("AWS_REGION", "eu-west-1"), **kwargs)


def _anthropic(model: str, **kwargs) -> BaseChatModel:
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(model=model, **kwargs)


def _gemini(model: str, **kwargs) -> BaseChatModel:
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(model=model, **kwargs)


# provider name -> (factory, default model used when none is passed)
PROVIDERS: dict[str, tuple[Callable[..., BaseChatModel], str]] = {
    "ollama": (_ollama, "north-mini-code-1.0"),
    "openai": (_openai, "gpt-4o-mini"),
    "bedrock": (_bedrock, "openai.gpt-oss-120b-1:0"),
    "anthropic": (_anthropic, "claude-sonnet-5-5"),
    "gemini": (_gemini, "gemini-2.5-flash"),
}


class llm(LLMProvider):
    def __init__(self, model: str | None = None, llm_provider: str | None = None, **kwargs):
        self.llm_provider = (llm_provider or DEFAULT_LLM_PROVIDER).lower()
        if self.llm_provider not in PROVIDERS:
            raise ValueError(f"Unknown provider '{self.llm_provider}'. Choose from: {list(PROVIDERS)}")
        self.model = model or os.getenv("LLM_MODEL") or PROVIDERS[self.llm_provider][1]
        self.kwargs = kwargs  # e.g. temperature=0, max_tokens=...

    def get_llm(self) -> BaseChatModel:
        print(f"Using LLM provider: {self.llm_provider}, model: {self.model}, kwargs: {self.kwargs}")
        factory, _ = PROVIDERS[self.llm_provider]
        return factory(self.model, **self.kwargs)
