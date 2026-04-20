from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Sequence

from .parser import build_parser


def _install_user_service() -> None:
    service_dir = Path.home() / ".config" / "systemd" / "user"
    service_dir.mkdir(parents=True, exist_ok=True)
    service_path = service_dir / "forgetmail.service"
    exec_start = f"{sys.executable} -m forgetmail.cli"
    unit_text = f"""[Unit]
Description=forgetMail Gmail to Telegram bridge
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart={exec_start}
Restart=on-failure
RestartSec=5
WorkingDirectory={Path.home()}
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
"""
    service_path.write_text(unit_text, encoding="utf-8")

    print(f"Wrote systemd user unit: {service_path}")
    print("Recommended follow-up: loginctl enable-linger $USER")

    try:
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "--user", "enable", "forgetmail.service"], check=True)
        subprocess.run(["systemctl", "--user", "start", "forgetmail.service"], check=True)
        print("Enabled and started forgetmail.service")
    except Exception as exc:
        print(f"Systemd activation could not be completed automatically: {exc}")
        print("Run these commands manually if needed:")
        print("  systemctl --user daemon-reload")
        print("  systemctl --user enable forgetmail.service")
        print("  systemctl --user start forgetmail.service")


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

    if args.install_service:
        _install_user_service()
        return 0

    from forgetmail.daemon import run_daemon

    run_daemon(debug=args.debug)
    return 0
