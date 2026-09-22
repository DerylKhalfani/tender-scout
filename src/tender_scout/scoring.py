import logging
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from tender_scout.config import Config
from tender_scout.notice import Notice

logger = logging.getLogger(__name__)


class Scorer(Protocol):
    def score(self, notice: Notice, config: Config) -> tuple[int, str]: ...


class PlaceholderScorer:
    """Stand in until real llm model scorer"""

    def score(self, notice: Notice, config: Config) -> tuple[int, str]:
        return (1, "This is a placeholder and nothing was really judged")


class ScoredNotice(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    notice: Notice
    score: int = Field(..., ge=1, le=100, strict=True)
    rationale: str


def score_notices(
    notices: list[Notice], config: Config, scorer: Scorer
) -> list[ScoredNotice]:

    scored_notices: list[ScoredNotice] = []
    for notice in notices:
        try:
            score, rationale = scorer.score(notice, config)

        except Exception:
            logger.exception("Scoring failed for notice: %s", notice.id)
            continue

        scored_notices.append(
            ScoredNotice(notice=notice, score=score, rationale=rationale)
        )

    return scored_notices


def select_for_digest(scored: list[ScoredNotice], config: Config) -> list[ScoredNotice]:

    kept: list[ScoredNotice] = []
    for scored_notice in scored:
        if scored_notice.score >= config.min_score:
            kept.append(scored_notice)

    return sorted(kept, key=lambda item: item.score, reverse=True)
