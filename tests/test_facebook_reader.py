from __future__ import annotations

import tempfile
import unittest
import zipfile
import re
import json
from pathlib import Path

from recovery_engine.readers.facebook.reader import process_facebook_export
from recovery_engine.validation.privacy import scan_public_tree


ROOT = Path(__file__).resolve().parents[1]


class FacebookReaderTests(unittest.TestCase):
    def test_sample_folder_generates_canonical_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = process_facebook_export(
                source=ROOT / "examples/facebook_sample",
                case_id="TEST_FACEBOOK_SAMPLE",
                output_root=Path(tmp),
                strict=False,
            )

            self.assertEqual(result.validation_status, "pass")
            self.assertGreater(result.object_count, 0)
            self.assertTrue((result.case_root / "00_README.md").exists())
            self.assertTrue((result.case_root / "03_WORKBOOKS/messages.xlsx").exists())
            self.assertTrue((result.case_root / "04_REPORTS/summary.md").exists())
            self.assertTrue((result.case_root / "06_PROVENANCE/source_to_output_map.json").exists())

    def test_sample_zip_generates_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "sample.zip"
            with zipfile.ZipFile(zip_path, "w") as archive:
                for path in (ROOT / "examples/facebook_sample").rglob("*"):
                    if path.is_file():
                        archive.write(path, path.relative_to(ROOT / "examples/facebook_sample").as_posix())

            result = process_facebook_export(
                source=zip_path,
                case_id="TEST_FACEBOOK_ZIP",
                output_root=Path(tmp) / "out",
            )

            self.assertEqual(result.validation_status, "pass")
            self.assertTrue((result.case_root / "OUTPUT_INDEX.json").exists())

    def test_html_sample_generates_conversation_and_messages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = process_facebook_export(
                source=ROOT / "examples/facebook_html_sample",
                case_id="TEST_FACEBOOK_HTML",
                output_root=Path(tmp),
            )

            self.assertEqual(result.validation_status, "pass")
            conversations_path = result.case_root / "02_DERIVED/conversations/conversations.jsonl"
            messages_path = result.case_root / "01_MASTER/messages/messages.jsonl"
            conversations = [json.loads(line) for line in conversations_path.read_text(encoding="utf-8").splitlines()]
            messages = [json.loads(line) for line in messages_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(conversations), 1)
            self.assertEqual(len(messages), 2)
            self.assertTrue(all(message["sender_ref"] for message in messages))
            self.assertNotIn("THREAD_0002", {message["content_exact"] for message in messages})

    def test_public_tree_privacy_scan_passes(self) -> None:
        result = scan_public_tree(ROOT)
        self.assertEqual(result["status"], "pass", result["findings"])

    def test_examples_use_synthetic_identifiers_only(self) -> None:
        forbidden_patterns = [
            re.compile(r"@"),
            re.compile(r"https?://", re.IGNORECASE),
            re.compile(r"www\.", re.IGNORECASE),
            re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
            re.compile(r"\b\d{3}-\d{3}-\d{4}\b"),
            re.compile(r"\b\d{1,5}\s+[A-Za-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr)\b", re.IGNORECASE),
            re.compile(r"\b(Alex|Jordan|Sample User|Fictional Example)\b", re.IGNORECASE),
        ]
        forbidden_path_terms = re.compile(r"alex|jordan|sample_user|sample-user|fictional-example", re.IGNORECASE)

        for path in (ROOT / "examples").rglob("*"):
            self.assertIsNone(forbidden_path_terms.search(path.name), str(path))
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden_patterns:
                self.assertIsNone(pattern.search(text), f"{pattern.pattern} in {path}")


if __name__ == "__main__":
    unittest.main()
