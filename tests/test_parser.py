import unittest

from langchain_core.exceptions import OutputParserException
from langchain_core.runnables import RunnableLambda

from services.skill_extraction_service import (
    create_extraction_chain, create_parallel_extraction,
)


class ExtractionTests(unittest.TestCase):
    def test_routes_each_document_to_its_own_extraction(self):
        def respond(prompt):
            text = prompt.to_messages()[-1].content
            if text.endswith("Resume: Python"):
                return '{"skills": ["Python"]}'
            if text.endswith("Job: Docker"):
                return '{"skills": ["Docker"]}'
            self.fail(f"Unexpected extraction input: {text}")

        result = create_parallel_extraction(RunnableLambda(respond)).invoke(
            {"cv": "Resume: Python", "jd": "Job: Docker"}
        )
        self.assertEqual(result["cv_skills"].skills, ["Python"])
        self.assertEqual(result["jd_skills"].skills, ["Docker"])

    def test_empty_skill_list_is_valid(self):
        chain = create_extraction_chain(RunnableLambda(lambda _: '{"skills": []}'))
        self.assertEqual(chain.invoke({"text": "No skills"}).skills, [])

    def test_rejects_malformed_model_output(self):
        for response in ['not JSON', '{"skills": "Python"}']:
            with self.subTest(response=response):
                chain = create_extraction_chain(RunnableLambda(lambda _, value=response: value))
                with self.assertRaises(OutputParserException):
                    chain.invoke({"text": "Python"})
