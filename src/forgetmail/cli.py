import argparse
from typing import Sequence


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
        "--debug",
        action="store_true",
        help="Enable verbose debug logging",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.onboard or args.auth:
        from forgetmail.auth.wizard import run_onboarding_wizard

        run_onboarding_wizard()
        return 0

    if args.check:
        from forgetmail.auth.wizard import validate_all

        validate_all()
        return 0

    from forgetmail.daemon import run_daemon

    run_daemon(debug=args.debug)
    return 0
