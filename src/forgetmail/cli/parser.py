from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forgetMail",
        description="Gmail to Telegram signal bridge",
    )
    parser.add_argument(
        "--onboard",
        action="store_true",
        help="Run interactive onboarding for Google, Telegram, and LLM",
    )
    parser.add_argument(
        "--auth",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate saved credentials and config",
    )
    parser.add_argument(
        "--install-service",
        action="store_true",
        help="Install or update the user-level systemd service",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug logging",
    )
    return parser
