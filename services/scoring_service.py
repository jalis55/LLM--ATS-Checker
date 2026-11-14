from models.schemas import SkillMatchResult


def calculate_skill_score(result: SkillMatchResult) -> float:
    matched = len(result.matched)
    unmatched = len(result.unmatched)

    total = matched + unmatched

    if total == 0:
        return 0.0

    score = (matched / total) * 100

    return round(score, 2)