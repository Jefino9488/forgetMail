from __future__ import annotations

from typing import Any


class ConfigError(RuntimeError):
    pass


def validate_config(config: dict[str, Any]) -> None:
    required_sections = ("telegram", "gmail", "llm", "embeddings", "log")
    for section in required_sections:
        if section not in config or not isinstance(config[section], dict):
            raise ConfigError(f"Missing or invalid [{section}] section in config.")

    chat_id = config["telegram"].get("chat_id")
    if not isinstance(chat_id, int) or chat_id == 0:
        raise ConfigError("telegram.chat_id must be a non-zero integer.")

    interval = config["gmail"].get("poll_interval_seconds")
    if not isinstance(interval, int) or interval < 30:
        raise ConfigError("gmail.poll_interval_seconds must be an integer >= 30.")

    idle_interval = config["gmail"].get("idle_poll_interval_seconds", interval)
    if not isinstance(idle_interval, int) or idle_interval < 30:
        raise ConfigError("gmail.idle_poll_interval_seconds must be an integer >= 30.")

    lookback_days = config["gmail"].get("lookback_days")
    if not isinstance(lookback_days, int) or lookback_days < 1:
        raise ConfigError("gmail.lookback_days must be an integer >= 1.")

    max_messages = config["gmail"].get("max_messages_per_poll")
    if not isinstance(max_messages, int) or max_messages < 1:
        raise ConfigError("gmail.max_messages_per_poll must be an integer >= 1.")

    provider = config["llm"].get("provider")
    if not isinstance(provider, str) or not provider.strip():
        raise ConfigError("llm.provider must be a non-empty string.")

    provider_name = provider.strip().lower()

    model = config["llm"].get("model")
    if not isinstance(model, str) or not model.strip():
        raise ConfigError("llm.model must be a non-empty string.")

    base_url = config["llm"].get("base_url")
    if not isinstance(base_url, str):
        raise ConfigError("llm.base_url must be a string.")
    if provider_name != "ollama" and not base_url.strip():
        raise ConfigError("llm.base_url must be set for non-Ollama providers.")
    if provider_name == "ollama" and not base_url.strip():
        raise ConfigError("llm.base_url must be set for Ollama provider.")

    threshold = config["llm"].get("importance_threshold")
    if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
        raise ConfigError("llm.importance_threshold must be a number between 0 and 1.")

    timeout_seconds = config["llm"].get("timeout_seconds")
    if not isinstance(timeout_seconds, int) or timeout_seconds < 5:
        raise ConfigError("llm.timeout_seconds must be an integer >= 5.")

    batch_size = config["llm"].get("batch_size")
    if not isinstance(batch_size, int) or batch_size < 1:
        raise ConfigError("llm.batch_size must be an integer >= 1.")

    prompt_style = config["llm"].get("prompt_style", "caveman")
    if not isinstance(prompt_style, str) or prompt_style.strip().lower() not in {
        "caveman",
        "verbose",
    }:
        raise ConfigError("llm.prompt_style must be 'caveman' or 'verbose'.")

    temperature = config["llm"].get("temperature", 0.1)
    if not isinstance(temperature, (int, float)) or not 0 <= float(temperature) <= 1:
        raise ConfigError("llm.temperature must be a number between 0 and 1.")

    schema_strict = config["llm"].get("schema_strict", True)
    if not isinstance(schema_strict, bool):
        raise ConfigError("llm.schema_strict must be true or false.")

    ask_enabled = config["llm"].get("ask_enabled", True)
    if not isinstance(ask_enabled, bool):
        raise ConfigError("llm.ask_enabled must be true or false.")

    ask_top_k = config["llm"].get("ask_top_k", 6)
    if not isinstance(ask_top_k, int) or ask_top_k < 1:
        raise ConfigError("llm.ask_top_k must be an integer >= 1.")

    ask_timeout_seconds = config["llm"].get("ask_timeout_seconds", 90)
    if not isinstance(ask_timeout_seconds, int) or ask_timeout_seconds < 5:
        raise ConfigError("llm.ask_timeout_seconds must be an integer >= 5.")

    ask_max_context_chars = config["llm"].get("ask_max_context_chars", 3500)
    if not isinstance(ask_max_context_chars, int) or ask_max_context_chars < 500:
        raise ConfigError("llm.ask_max_context_chars must be an integer >= 500.")

    ask_max_citations = config["llm"].get("ask_max_citations", 3)
    if (
        not isinstance(ask_max_citations, int)
        or ask_max_citations < 1
        or ask_max_citations > 8
    ):
        raise ConfigError("llm.ask_max_citations must be an integer between 1 and 8.")

    few_shot_max_examples = config["llm"].get("few_shot_max_examples", 4)
    if (
        not isinstance(few_shot_max_examples, int)
        or few_shot_max_examples < 0
        or few_shot_max_examples > 12
    ):
        raise ConfigError(
            "llm.few_shot_max_examples must be an integer between 0 and 12."
        )

    embeddings_cfg = config["embeddings"]

    enabled = embeddings_cfg.get("enabled", False)
    if not isinstance(enabled, bool):
        raise ConfigError("embeddings.enabled must be true or false.")

    enable_vector_upsert = embeddings_cfg.get("enable_vector_upsert", True)
    if not isinstance(enable_vector_upsert, bool):
        raise ConfigError("embeddings.enable_vector_upsert must be true or false.")

    enable_vector_query = embeddings_cfg.get("enable_vector_query", False)
    if not isinstance(enable_vector_query, bool):
        raise ConfigError("embeddings.enable_vector_query must be true or false.")

    query_top_k = embeddings_cfg.get("query_top_k", 6)
    if not isinstance(query_top_k, int) or query_top_k < 1:
        raise ConfigError("embeddings.query_top_k must be an integer >= 1.")

    min_similarity_for_boost = embeddings_cfg.get("min_similarity_for_boost", 0.78)
    if (
        not isinstance(min_similarity_for_boost, (int, float))
        or not 0 <= float(min_similarity_for_boost) <= 1
    ):
        raise ConfigError(
            "embeddings.min_similarity_for_boost must be a number between 0 and 1."
        )

    max_similarity_boost = embeddings_cfg.get("max_similarity_boost", 0.20)
    if (
        not isinstance(max_similarity_boost, (int, float))
        or not 0 <= float(max_similarity_boost) <= 1
    ):
        raise ConfigError(
            "embeddings.max_similarity_boost must be a number between 0 and 1."
        )

    min_important_neighbors = embeddings_cfg.get("min_important_neighbors", 1)
    if not isinstance(min_important_neighbors, int) or min_important_neighbors < 1:
        raise ConfigError("embeddings.min_important_neighbors must be an integer >= 1.")

    embedding_provider = embeddings_cfg.get("provider")
    if not isinstance(embedding_provider, str) or not embedding_provider.strip():
        raise ConfigError("embeddings.provider must be a non-empty string.")
    embedding_provider_name = embedding_provider.strip().lower()
    if embedding_provider_name != "ollama":
        raise ConfigError("embeddings.provider currently supports only 'ollama'.")

    embedding_model = embeddings_cfg.get("model")
    if not isinstance(embedding_model, str) or not embedding_model.strip():
        raise ConfigError("embeddings.model must be a non-empty string.")

    embedding_base_url = embeddings_cfg.get("base_url")
    if not isinstance(embedding_base_url, str) or not embedding_base_url.strip():
        raise ConfigError("embeddings.base_url must be a non-empty string.")

    embedding_timeout_seconds = embeddings_cfg.get("timeout_seconds")
    if not isinstance(embedding_timeout_seconds, int) or embedding_timeout_seconds < 3:
        raise ConfigError("embeddings.timeout_seconds must be an integer >= 3.")

    embedding_batch_size = embeddings_cfg.get("batch_size")
    if not isinstance(embedding_batch_size, int) or embedding_batch_size < 1:
        raise ConfigError("embeddings.batch_size must be an integer >= 1.")

    persist_path = embeddings_cfg.get("persist_path")
    if not isinstance(persist_path, str) or not persist_path.strip():
        raise ConfigError("embeddings.persist_path must be a non-empty string.")

    collection = embeddings_cfg.get("collection")
    if not isinstance(collection, str) or not collection.strip():
        raise ConfigError("embeddings.collection must be a non-empty string.")

    enable_corrections = embeddings_cfg.get("enable_corrections", True)
    if not isinstance(enable_corrections, bool):
        raise ConfigError("embeddings.enable_corrections must be true or false.")

    corrections_collection = embeddings_cfg.get(
        "corrections_collection", "email_corrections"
    )
    if (
        not isinstance(corrections_collection, str)
        or not corrections_collection.strip()
    ):
        raise ConfigError(
            "embeddings.corrections_collection must be a non-empty string."
        )

    corrections_top_k = embeddings_cfg.get("corrections_top_k", 2)
    if not isinstance(corrections_top_k, int) or corrections_top_k < 1:
        raise ConfigError("embeddings.corrections_top_k must be an integer >= 1.")

    corrections_min_similarity = embeddings_cfg.get("corrections_min_similarity", 0.72)
    if (
        not isinstance(corrections_min_similarity, (int, float))
        or not 0 <= float(corrections_min_similarity) <= 1
    ):
        raise ConfigError(
            "embeddings.corrections_min_similarity must be a number between 0 and 1."
        )

    log_level = config["log"].get("level")
    if not isinstance(log_level, str) or not log_level.strip():
        raise ConfigError("log.level must be a non-empty string.")

    log_file = config["log"].get("file", "")
    if not isinstance(log_file, str):
        raise ConfigError("log.file must be a string.")

    http_debug = config["log"].get("http_debug", False)
    if not isinstance(http_debug, bool):
        raise ConfigError("log.http_debug must be true or false.")
