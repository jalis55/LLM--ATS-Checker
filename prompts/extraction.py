
from langchain_core.prompts import ChatPromptTemplate

skill_extraction_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert skill extraction assistant.

        Extract technical and professional skills explicitly
        supported by the provided text.

        Rules:
        1. Extract relevant skills.
        2. Normalize common skill names.
        3. Avoid duplicates.
        4. Do not invent skills.
        5. Return only valid JSON.

        {format_instructions}
        """
    ),
    (
        "human",
        "Extract skills from the following text:\n{text}"
    )
])
