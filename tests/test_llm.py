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

from forgetmail.llm import LLMError, _resolve_temperature, _validate_answer_payload


class LLMValidationTests(unittest.TestCase):
    def test_validate_answer_payload_happy_path(self) -> None:
        payload = {
            "answer": "It is likely in the Monday thread.",
            "confidence": 0.74,
            "citations": [
                {
                    "message_id": "m1",
                    "subject": "Monday update",
                    "why": "same timeline",
                },
                {
                    "message_id": "m2",
                    "subject": "Planning",
                    "why": "mentions deliverable",
                },
            ],
        }

        validated = _validate_answer_payload(payload, max_citations=1)
        self.assertEqual(validated["answer"], payload["answer"])
        self.assertAlmostEqual(validated["confidence"], 0.74)
        self.assertEqual(len(validated["citations"]), 1)

    def test_validate_answer_payload_requires_answer(self) -> None:
        with self.assertRaises(LLMError):
            _validate_answer_payload({"citations": []}, max_citations=2)

    def test_resolve_temperature_bounds(self) -> None:
        self.assertEqual(_resolve_temperature({"temperature": -1}), 0.0)
        self.assertEqual(_resolve_temperature({"temperature": 3}), 1.0)
        self.assertEqual(_resolve_temperature({"temperature": "bad"}), 0.1)


if __name__ == "__main__":
    unittest.main()
