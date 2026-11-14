
from langchain_core.prompts import ChatPromptTemplate

skill_matching_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert technical skill matching assistant.

        Compare the skills required by the job description
        against the skills found in the candidate's CV.

        Rules:
        1. Evaluate every JD skill.
        2. Match skills when they are equivalent or when
           the CV skill clearly demonstrates the JD skill.
        3. Do not treat merely related technologies as equivalent.
        4. Put each JD skill in exactly one category:
           matched or unmatched.
        5. Do not invent skills.
        6. Return only valid JSON matching the schema.

        {format_instructions}
        """
    ),
    (
        "human",
        """
        CV skills:
        {cv_skills}

        JD skills:
        {jd_skills}
        """
    )
])
