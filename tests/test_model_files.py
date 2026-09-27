import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from forge_auto_censor import model_files


class LocalModelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.models = self.root / "models"
        self.patch_dir = patch.object(model_files, "MODEL_DIR", self.models)
        self.patch_dir.start()
        self.addCleanup(self.patch_dir.stop)

    def test_imported_model_survives_removal_of_original_cache(self):
        cached = self.root / "cached.onnx"
        cached.write_bytes(b"cached model content")
        with patch.object(model_files, "_find_cached_model", return_value=cached), \
                patch.object(model_files, "_download_model") as download:
            local = model_files.ensure_model_file("s")
            download.assert_not_called()
        self.assertEqual(local, self.models / "censor_detect_v1.0_s.onnx")
        self.assertFalse(local.is_symlink())
        cached.unlink()
        with patch.object(model_files, "_find_cached_model", side_effect=AssertionError("cache used")), \
                patch.object(model_files, "_download_model", side_effect=AssertionError("network used")):
            self.assertEqual(model_files.ensure_model_file("s"), local)
            self.assertEqual(local.read_bytes(), b"cached model content")

    def test_download_is_saved_separately_for_each_selected_model(self):
        for level in ("s", "n"):
            source = self.root / f"download-{level}.onnx"
            source.write_bytes(level.encode())
            with patch.object(model_files, "_find_cached_model", return_value=None), \
                    patch.object(model_files, "_download_model", return_value=source) as download:
                local = model_files.ensure_model_file(level)
                download.assert_called_once_with(f"censor_detect_v1.0_{level}")
            self.assertEqual(local.read_bytes(), level.encode())
        self.assertEqual(len(list(self.models.glob("*.onnx"))), 2)

    def test_download_failure_names_manual_destination_without_creating_model(self):
        with patch.object(model_files, "_find_cached_model", return_value=None), \
                patch.object(model_files, "_download_model", side_effect=OSError("offline")):
            with self.assertRaisesRegex(RuntimeError, "censor_detect_v1.0_n.onnx"):
                model_files.ensure_model_file("n")
        self.assertFalse(list(self.models.glob("*.onnx")))

    def test_interrupted_copy_is_not_treated_as_a_saved_model(self):
        def interrupted_copy(source, destination):
            Path(destination).write_bytes(b"partial")
            raise OSError("disk full")

        cached = self.root / "cached.onnx"
        cached.write_bytes(b"complete")
        with patch.object(model_files, "_find_cached_model", return_value=cached), \
                patch.object(model_files.shutil, "copyfile", side_effect=interrupted_copy):
            with self.assertRaisesRegex(OSError, "disk full"):
                model_files.ensure_model_file("s")
        self.assertEqual(list(self.models.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
