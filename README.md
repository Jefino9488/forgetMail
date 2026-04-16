# forgetMail

forgetMail is a Linux-native Gmail to Telegram signal bridge.

It polls unread Gmail messages, classifies importance with an LLM, and sends actionable summaries to a Telegram bot chat.

## Features

- Gmail polling with configurable lookback and batch limits
- Importance classification with local Ollama or OpenAI-compatible providers
- Telegram command controls for status and ad-hoc polling
- Watch rules to prioritize specific contexts
- SQLite state tracking to avoid duplicate processing

## Tech Stack

- Python 3.11+
- aiogram (Telegram bot API)
- Google Gmail API (OAuth)
- Ollama or OpenAI-compatible LLM endpoint
- SQLite for local state

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For fish shell:

```fish
source .venv/bin/activate.fish
```

## Development Tooling

Install dev tools:

```bash
pip install -e .[dev]
```

Run lint and format checks:

```bash
ruff check .
ruff format --check .
```

Format and auto-fix locally:

```bash
ruff check . --fix
ruff format .
```

Enable auto-format/lint on commit:

```bash
pre-commit install --config .github/pre-commit-config.yaml
```

## First-Time Onboarding

Run interactive onboarding:

```bash
forgetMail --onboard
```

The wizard will guide you through:

1. Google OAuth setup
2. Telegram bot token validation and chat detection
3. LLM provider/model configuration

## Validate Setup

```bash
forgetMail --check
```

## Run Daemon

```bash
forgetMail --debug
```

## Telegram Bot Commands

- `/help`
- `/status`
- `/signals`
- `/ask <question>`
- `/watchFor <context> [boost]`
- `/watchList`
- `/unwatch <id>`
- `/run`

## Configuration

Runtime config is stored at:

- `~/.config/forgetmail/config.toml`

Secrets are read from environment variables first, then keyring.

## Project Layout

- `src/forgetmail/daemon/`: main loop and orchestration
- `src/forgetmail/notifier/`: Telegram messaging and command polling bridge
- `src/forgetmail/telegram/`: aiogram client layer
- `src/forgetmail/classifier/`: LLM classification pipeline
- `src/forgetmail/store/`: SQLite state and events

## License

Private/internal use unless otherwise specified by the repository owner.
# forgetMail

## Problem
Email inboxes are noisy. Important messages get buried under newsletters, promos, and low-priority updates, so you still have to keep checking Gmail manually.

## What This Solves
forgetMail watches your Gmail, uses an LLM to score message importance, and sends only high-signal alerts to Telegram.

You stop doom-scrolling your inbox and only see what likely needs attention.

## Slogan
Set it up once. Forget it.

## Example Setup
```bash
# from the project root
pip install -e .

# one-time interactive setup (Google OAuth + Telegram + LLM)
forgetMail --onboard

# optional check
forgetMail --check

# run the signal bridge
forgetMail
```
