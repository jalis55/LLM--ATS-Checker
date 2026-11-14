import unittest
from unittest.mock import patch

from langchain_core.exceptions import OutputParserException
from langchain_core.runnables import RunnableLambda

from services.ats_pipeline_service import create_ats_pipeline
from services.skill_matching_service import create_matching_chain


class MatchingTests(unittest.TestCase):
    def test_matching_receives_both_skill_lists(self):
        def respond(prompt):
            text = prompt.to_messages()[-1].content
            self.assertIn("Python", text)
            self.assertIn("Docker", text)
            return '{"matched": ["Python"], "unmatched": ["Docker"]}'

        result = create_matching_chain(RunnableLambda(respond)).invoke(
            {"cv_skills": ["Python"], "jd_skills": ["Python", "Docker"]}
        )
        self.assertEqual(result.matched, ["Python"])
        self.assertEqual(result.unmatched, ["Docker"])

    def test_rejects_invalid_matching_output(self):
        chain = create_matching_chain(RunnableLambda(lambda _: '{"matched": 42}'))
        with self.assertRaises(OutputParserException):
            chain.invoke({"cv_skills": [], "jd_skills": []})

    def test_full_pipeline_passes_extracted_skills_to_matching(self):
        def respond(prompt):
            text = prompt.to_messages()[-1].content
            if text.startswith("Extract skills"):
                return ('{"skills": ["Python"]}' if text.endswith("Resume")
                        else '{"skills": ["Python", "Docker"]}')
            self.assertIn("['Python']", text)
            self.assertIn("['Python', 'Docker']", text)
            self.assertNotIn("Resume", text)
            return '{"matched": ["Python"], "unmatched": ["Docker"]}'

        with patch("services.ats_pipeline_service.get_model",
                   return_value=RunnableLambda(respond)) as get_model:
            result = create_ats_pipeline(temperature=0.1, max_retries=1, timeout=20).invoke(
                {"cv": "Resume", "jd": "Job description"}
            )
            get_model.assert_called_once_with(temperature=0.1, max_retries=1, timeout=20)
        self.assertEqual(result.matched, ["Python"])
        self.assertEqual(result.unmatched, ["Docker"])
