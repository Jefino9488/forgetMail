from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

if "httpx" not in sys.modules:
    sys.modules["httpx"] = types.ModuleType("httpx")

if "keyring" not in sys.modules:
    fake_keyring = types.ModuleType("keyring")

    def _get_password(_service: str, _key: str) -> str | None:
        return None

    def _set_password(_service: str, _key: str, _value: str) -> None:
        return None

    fake_keyring.get_password = _get_password
    fake_keyring.set_password = _set_password
    sys.modules["keyring"] = fake_keyring

from forgetmail.classifier import EmailCandidate, _build_system_prompt, _parse_rows


class ClassifierSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.by_id = {
            "m1": EmailCandidate(
                message_id="m1",
                thread_id="t1",
                sender="alice@example.com",
                subject="Need update",
                snippet="Can you send the update today?",
            )
        }

    def test_parse_rows_strict_rejects_invalid_rows(self) -> None:
        rows = [
            {
                "message_id": "m1",
                "important": "yes",
                "score": 0.9,
                "reason": "looks urgent",
            }
        ]

        parsed = _parse_rows(rows, self.by_id, schema_strict=True)
        self.assertEqual(parsed, [])

    def test_parse_rows_non_strict_coerces_fallbacks(self) -> None:
        rows = [
            {
                "message_id": "m1",
                "important": 1,
                "score": "0.8",
                "reason": "looks urgent",
            }
        ]

        parsed = _parse_rows(rows, self.by_id, schema_strict=False)
        self.assertEqual(len(parsed), 1)
        self.assertTrue(parsed[0].important)
        self.assertAlmostEqual(parsed[0].score, 0.8)
        self.assertEqual(parsed[0].reason, "looks urgent")

    def test_build_system_prompt_includes_few_shot_examples(self) -> None:
        prompt = _build_system_prompt(
            {"prompt_style": "caveman"},
            [
                {
                    "important": True,
                    "text": "From: CEO subject: urgent review",
                    "reason": "human urgent ask",
                }
            ],
        )
        self.assertIn("Classify inbox mail", prompt)
        self.assertIn("Examples:", prompt)
        self.assertIn("important=1", prompt)


if __name__ == "__main__":
    unittest.main()
