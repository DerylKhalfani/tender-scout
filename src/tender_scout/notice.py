from datetime import date

from pydantic import BaseModel, ConfigDict


class Notice(BaseModel):
    """Plain data model for one TED record"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    title: str
    buyer_country: str
    notice_text: str
    cpv_codes: list[str]
    publication_date: date
    ted_url: str
