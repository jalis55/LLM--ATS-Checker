
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda

from models.schemas import ExtractedSkills
from prompts.extraction import skill_extraction_prompt


def create_extraction_chain(model):
    parser = PydanticOutputParser(
        pydantic_object=ExtractedSkills
    )

    return (
        skill_extraction_prompt.partial(
            format_instructions=parser.get_format_instructions()
        )
        | model
        | parser
    )


def create_parallel_extraction(model):
    extraction_chain = create_extraction_chain(model)

    return RunnableParallel(
        cv_skills=(
            RunnableLambda(lambda x: {"text": x["cv"]})
            | extraction_chain
        ),
        jd_skills=(
            RunnableLambda(lambda x: {"text": x["jd"]})
            | extraction_chain
        )
    )
