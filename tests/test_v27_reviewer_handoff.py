from __future__ import annotations

import unittest
from pathlib import Path

from services.reviewer_handoff import run_reviewer_handoff_check, reviewer_handoff_payload
from settings import APP_VERSION

ROOT = Path(__file__).resolve().parents[1]


class V27ReviewerHandoffTests(unittest.TestCase):
    def test_reviewer_handoff_payload_declares_non_claims(self) -> None:
        payload = reviewer_handoff_payload()
        self.assertEqual(payload["status"], "pass")
        text = " ".join(payload["non_claims"]).lower()
        self.assertIn("does not capture", text)
        self.assertTrue("does not transmit" in text or "does not send" in text)
        self.assertIn("does not scan", text)

    def test_reviewer_handoff_check_passes(self) -> None:
        payload = run_reviewer_handoff_check(app_root=ROOT, app_version=APP_VERSION)
        self.assertEqual(payload["status"], "pass")


if __name__ == "__main__":
    unittest.main()
