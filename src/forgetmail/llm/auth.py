from forgetmail.secrets import get_secret, set_secret

LLM_API_KEY_SECRET = "llm_api_key"


def cache_llm_api_key(api_key: str) -> None:
    if not set_secret(LLM_API_KEY_SECRET, api_key):
        raise RuntimeError(
            "Could not store LLM API key in keyring. "
            "Set FORGETMAIL_LLM_API_KEY as an environment variable."
        )


def get_llm_api_key() -> str | None:
    return get_secret(LLM_API_KEY_SECRET)
