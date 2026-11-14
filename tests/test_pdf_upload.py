import unittest
from unittest.mock import patch

from models.schemas import SkillMatchResult
from io import BytesIO
from pathlib import Path

import pymupdf
from streamlit.testing.v1 import AppTest

from utils.pdf_extractor import extract_text_from_pdf


class PDFUploadTests(unittest.TestCase):
    def make_pdf(self, texts, encrypted=False):
        with pymupdf.open() as document:
            for text in texts:
                page = document.new_page()
                if text:
                    page.insert_text((72, 72), text)
            options = {}
            if encrypted:
                options = dict(encryption=pymupdf.PDF_ENCRYPT_AES_256,
                               owner_pw="owner", user_pw="secret")
            return BytesIO(document.tobytes(**options))

    def test_extracts_all_pages_and_preserves_upload(self):
        upload = self.make_pdf(["Python Django", "Docker AWS"])
        upload.seek(7)
        self.assertEqual(extract_text_from_pdf(upload), "Python Django\n\nDocker AWS")
        self.assertEqual(upload.tell(), 7)
        self.assertFalse(upload.closed)
        self.assertIn("Docker", extract_text_from_pdf(upload))

    def test_rejects_empty_invalid_blank_and_locked_files(self):
        for upload, message in [
            (BytesIO(), "empty"),
            (BytesIO(b"not a PDF"), "valid, undamaged"),
            (self.make_pdf([""]), "No readable text"),
            (self.make_pdf(["Private"], encrypted=True), "password-protected"),
        ]:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    extract_text_from_pdf(upload)

    def test_repeated_analysis_reuses_result_and_changed_input_runs_again(self):
        with patch("services.ats_pipeline_service.create_ats_pipeline") as factory:
            factory.return_value.invoke.return_value = SkillMatchResult(
                matched=["Python"], unmatched=["Docker"]
            )
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "ats_checker.py")).run()
            app.text_area(key="cv_text").set_value("Python\n\n  developer")
            app.text_area(key="jd_text").set_value("Python Docker")
            app.button[0].click().run()
            self.assertFalse(app.exception)
            factory.return_value.invoke.assert_called_once_with(
                {"cv": "Python developer", "jd": "Python Docker"}
            )
            app.button[0].click().run()
            self.assertFalse(app.exception)
            self.assertEqual(factory.return_value.invoke.call_count, 1)
            app.text_area(key="jd_text").set_value("Python AWS")
            app.button[0].click().run()
            self.assertFalse(app.exception)
            self.assertEqual(factory.return_value.invoke.call_count, 2)

    def test_failed_analysis_can_be_retried(self):
        with patch("services.ats_pipeline_service.create_ats_pipeline") as factory:
            factory.return_value.invoke.side_effect = [
                RuntimeError("Service unavailable"),
                SkillMatchResult(matched=["Python"]),
            ]
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "ats_checker.py")).run()
            app.text_area(key="cv_text").set_value("Python")
            app.text_area(key="jd_text").set_value("Python")
            app.button[0].click().run()
            self.assertFalse(app.exception)
            self.assertIn("Service unavailable", app.error[0].value)
            self.assertIsNone(app.session_state.analysis_result)
            app.button[0].click().run()
            self.assertFalse(app.exception)
            self.assertEqual(factory.return_value.invoke.call_count, 2)
            self.assertEqual(app.session_state.analysis_score, 100.0)

    def test_changed_settings_invalidate_completed_analysis(self):
        with patch("services.ats_pipeline_service.create_ats_pipeline") as factory:
            factory.return_value.invoke.return_value = SkillMatchResult(matched=["Python"])
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "ats_checker.py")).run()
            app.text_area(key="cv_text").set_value("Python")
            app.text_area(key="jd_text").set_value("Python")
            app.button[0].click().run()
            app.slider[0].set_value(0.3)
            app.button[0].click().run()
            self.assertFalse(app.exception)
            self.assertEqual(factory.return_value.invoke.call_count, 2)
            self.assertEqual(factory.call_args.kwargs["temperature"], 0.3)

    def test_app_offers_pdf_for_both_documents(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "ats_checker.py")).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.text_area), 2)
        app.radio(key="cv_method").set_value("Upload PDF")
        app.radio(key="jd_method").set_value("Upload PDF")
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("file_uploader")), 2)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.warning)


if __name__ == "__main__":
    unittest.main()
