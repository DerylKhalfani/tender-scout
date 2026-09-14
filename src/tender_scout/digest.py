from tender_scout.scoring import ScoredNotice

HEADING = "# Tender digest"

def render_digest(scored_notices: list[ScoredNotice]) -> str:
    blocks: list[str] = [HEADING]

    if not scored_notices:
        return f"{HEADING}\n\nNo matching notices"

    for scored_notice in scored_notices:

        notice = scored_notice.notice

        blocks.append(
            f"## {notice.title}\n"
            f"- Buyer country: {notice.buyer_country}\n"
            f"- Score: {scored_notice.score}\n"
            f"- Rationale: {scored_notice.rationale}\n"
            f"- {notice.ted_url}"
        )

    return "\n\n".join(blocks)