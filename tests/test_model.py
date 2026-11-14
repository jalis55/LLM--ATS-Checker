import os
import unittest
from unittest.mock import patch

from services.llm_model_service import get_model


class ModelConfigurationTests(unittest.TestCase):
    def test_missing_api_key_fails_before_creating_client(self):
        with patch.dict(os.environ, {}, clear=True), \
                patch("services.llm_model_service.ChatGroq") as client:
            with self.assertRaisesRegex(ValueError, "GROQ_API_KEY"):
                get_model()
            client.assert_not_called()

    def test_model_selection_and_request_settings(self):
        for configured, explicit, expected in [
            (None, None, "openai/gpt-oss-120b"),
            ("configured-model", None, "configured-model"),
            ("configured-model", "explicit-model", "explicit-model"),
        ]:
            with self.subTest(configured=configured, explicit=explicit):
                environment = {"GROQ_API_KEY": "test-key"}
                if configured:
                    environment["AI_MODEL"] = configured
                with patch.dict(os.environ, environment, clear=True), \
                        patch("services.llm_model_service.ChatGroq") as client:
                    get_model(model_name=explicit, temperature=0.1,
                              max_retries=1, timeout=20, max_tokens=512)
                    client.assert_called_once_with(
                        model=expected, temperature=0.1, max_retries=1,
                        timeout=20, max_tokens=512,
                    )
