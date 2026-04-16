from __future__ import annotations

from typing import Sequence

from .parser import build_parser


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
