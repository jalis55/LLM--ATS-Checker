import unittest

import pymupdf

from models.schemas import SkillMatchResult
from utils.report_generator import generate_ats_report


class ReportTests(unittest.TestCase):
    def test_report_contains_score_counts_and_escaped_skill_names(self):
        report = generate_ats_report(
            SkillMatchResult(matched=["Python", "R&D <tools>"], unmatched=["Docker"]),
            66.67,
        )
        self.assertTrue(report.startswith(b"%PDF-"))
        with pymupdf.open(stream=report, filetype="pdf") as document:
            text = "\n".join(page.get_text() for page in document)
        for expected in ["66.7%", "Python", "R&D <tools>", "Docker",
                         "Matched Skills", "Missing Skills", "Total Required Skills"]:
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_empty_results_still_generate_readable_report(self):
        report = generate_ats_report(SkillMatchResult(), 0.0)
        with pymupdf.open(stream=report, filetype="pdf") as document:
            text = "\n".join(page.get_text() for page in document)
        self.assertIn("0.0%", text)
        self.assertEqual(text.count("None identified."), 2)
