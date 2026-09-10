from tender_scout.notice import Notice

def render_digest(notices: list[Notice]) -> str:
    blocks: list[str] = ["# Tender digest"]

    for notice in notices:
        blocks.append(
            f"## {notice.title}\n"
            f"- Buyer country: {notice.buyer_country}\n"
            f"- {notice.ted_url}"
        )

    return "\n\n".join(blocks)