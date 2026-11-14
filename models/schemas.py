from pydantic import BaseModel, Field


class AtsScore(BaseModel):
    score: int = Field(
        ge=0,
        le=100,
        description="CV Score"
    )

    matched_requirements: list[str] = Field(
        default_factory=list,
        description="Matched Requirements"
    )

    unmatched_requirements: list[str] = Field(
        default_factory=list,
        description="Unmatched Requirements"
    )

    recommendation: str = Field(
        default="",
        description="Recommendation to increase CV score"
    )



class ExtractedSkills(BaseModel):
    skills: list[str] = Field(default_factory=list)


class SkillMatchResult(BaseModel):
    matched: list[str] = Field(default_factory=list)
    unmatched: list[str] = Field(default_factory=list)
