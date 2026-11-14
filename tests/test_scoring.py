import unittest

from models.schemas import SkillMatchResult
from services.scoring_service import calculate_skill_score


class ScoringTests(unittest.TestCase):
    def test_skill_coverage_and_rounding(self):
        cases = [([], [], 0.0), ([], ["Python"], 0.0),
                 (["Python"], [], 100.0),
                 (["Python"], ["Docker"], 50.0),
                 (["Python"], ["Docker", "AWS"], 33.33)]
        for matched, unmatched, expected in cases:
            with self.subTest(matched=matched, unmatched=unmatched):
                result = SkillMatchResult(matched=matched, unmatched=unmatched)
                self.assertEqual(calculate_skill_score(result), expected)
