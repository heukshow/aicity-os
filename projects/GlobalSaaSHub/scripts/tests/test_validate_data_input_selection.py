import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

PROJECT_DIR = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_DIR / "scripts" / "validate_data.py"
WORKFLOW_PATH = PROJECT_DIR.parents[1] / ".github" / "workflows" / "daily-deploy.yml"

spec = importlib.util.spec_from_file_location("validate_data_input_selection", SCRIPT_PATH)
validate_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_data)


def write_dataset(path, count, prefix):
    path.write_text(json.dumps([{"id": f"{prefix}-{i}"} for i in range(count)]), encoding="utf-8")


class InputSelectionTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.tempdir.name)
        self.data_dir = self.project_dir / "data"
        self.data_dir.mkdir()
        self.patches = [
            mock.patch.object(validate_data, "PROJECT_DIR", str(self.project_dir)),
            mock.patch.object(validate_data, "DATA_DIR", str(self.data_dir.resolve())),
            mock.patch.object(validate_data, "DEFAULT_INPUT", str(self.data_dir / "tools.json")),
        ]
        for patcher in self.patches:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patches):
            patcher.stop()
        self.tempdir.cleanup()

    def test_default_uses_production_when_stale_candidate_exists(self):
        write_dataset(self.data_dir / "tools.json", 150, "production")
        write_dataset(self.data_dir / "tools.next.json", 142, "candidate")
        tools, selected = validate_data.load_target_dataset()
        self.assertEqual(len(tools), 150)
        self.assertEqual(Path(selected), (self.data_dir / "tools.json").resolve())

    def test_explicit_candidate_uses_only_candidate(self):
        write_dataset(self.data_dir / "tools.json", 150, "production")
        write_dataset(self.data_dir / "tools.next.json", 142, "candidate")
        tools, selected = validate_data.load_target_dataset("data/tools.next.json")
        self.assertEqual(len(tools), 142)
        self.assertEqual(Path(selected), (self.data_dir / "tools.next.json").resolve())

    def test_missing_input_has_clear_error(self):
        with self.assertRaisesRegex(FileNotFoundError, "Target dataset file not found"):
            validate_data.load_target_dataset("data/missing.json")

    def test_input_outside_data_directory_is_rejected(self):
        outside = self.project_dir / "outside.json"
        write_dataset(outside, 1, "outside")
        with self.assertRaisesRegex(ValueError, "inside the project data directory"):
            validate_data.load_target_dataset(str(outside))

    def test_workflow_passes_candidate_input_explicitly(self):
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        validator_calls = workflow.count("python projects/GlobalSaaSHub/scripts/validate_data.py")
        explicit_inputs = workflow.count("--input projects/GlobalSaaSHub/data/tools.next.json")
        self.assertEqual(validator_calls, 2)
        self.assertEqual(explicit_inputs, validator_calls + 1)
        self.assertIn("python projects/GlobalSaaSHub/scripts/validate_system.py", workflow)


if __name__ == "__main__":
    unittest.main()