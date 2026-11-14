
from langchain_core.output_parsers import PydanticOutputParser

from models.schemas import SkillMatchResult
from prompts.matching import skill_matching_prompt


def create_matching_chain(model):
    parser = PydanticOutputParser(
        pydantic_object=SkillMatchResult
    )

    return (
        skill_matching_prompt.partial(
            format_instructions=parser.get_format_instructions()
        )
        | model
        | parser
    )
