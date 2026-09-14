from pydantic import BaseModel, Field, ConfigDict
from typing import Protocol

from tender_scout.notice import Notice
from tender_scout.config import Config


class Scorer(Protocol):
    def score(self, notice: Notice, config: Config) -> tuple[int, str]:
        ...


class PlaceholderScorer:
    """Stand in until real llm model scorer"""
    def score(self, notice: Notice, config: Config) -> tuple[int, str]:
        return (1, "This is a placeholder and nothing was really judged")


class ScoredNotice(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    notice: Notice
    score: int = Field(..., ge=1, le=100, strict=True)
    rationale: str


def score_notices(notices: list[Notice], config: Config, scorer: Scorer) -> list[ScoredNotice]:

    scored_notices: list[ScoredNotice] = []
    for notice in notices:
        score, rationale = scorer.score(notice, config)

        if score >= config.min_score:
            scored_notices.append(ScoredNotice(notice=notice, score=score, rationale=rationale))

    sorted_scored_notices = sorted(scored_notices, key=lambda item: item.score, reverse=True)

    return sorted_scored_notices