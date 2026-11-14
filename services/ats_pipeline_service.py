
from langchain_core.runnables import RunnableLambda

from .llm_model_service import get_model
from .skill_extraction_service import create_parallel_extraction
from .skill_matching_service import create_matching_chain


def prepare_matching_input(result: dict) -> dict:
    return {
        "cv_skills": result["cv_skills"].skills,
        "jd_skills": result["jd_skills"].skills
    }


def create_ats_pipeline(
    temperature: float = 0.2,
    max_retries: int = 3,
    timeout: float = 60.0
):
    model = get_model(
        temperature=temperature,
        max_retries=max_retries,
        timeout=timeout
    )

    extraction = create_parallel_extraction(model)
    matching = create_matching_chain(model)

    return (
        extraction
        | RunnableLambda(prepare_matching_input)
        | matching
    )
