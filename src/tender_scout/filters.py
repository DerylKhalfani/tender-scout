from tender_scout.notice import Notice
from tender_scout.config import Config

# Filtering logic file

def matches(notice: Notice, config: Config) -> bool:
    """Match notice configurations to original configurations"""

    notice_cpv_codes = set(notice.cpv_codes)
    config_cpv_codes = set(config.cpv_codes)

    # condition to check if atleast they share one cpv_code
    shared_cpv_code = bool(notice_cpv_codes & config_cpv_codes)

    shared_country = notice.buyer_country in config.countries

    return shared_cpv_code and shared_country

def filter_notices(notices: list[Notice], config: Config, seen_ids: set[str]) -> list[Notice]:

    passed_list = []

    for notice in notices:

        value = matches(notice, config)

        if value and notice.id not in seen_ids:
            passed_list.append(notice)

    return passed_list