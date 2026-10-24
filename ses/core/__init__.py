"""SES Core submodules with lazy exports."""


def __getattr__(name: str):
    if name == "OfflineRAGEngine":
        from .rag import OfflineRAGEngine
        return OfflineRAGEngine
    if name == "LocalLLMProvider":
        from .llm import LocalLLMProvider
        return LocalLLMProvider
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = ["OfflineRAGEngine", "LocalLLMProvider"]
