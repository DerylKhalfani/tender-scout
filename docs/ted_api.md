# TED Search API

What ticket 07 needs to build the client. Everything here was probed live on 2026-09-23.

Docs: <https://docs.ted.europa.eu/api/latest/search.html> ·
Spec: <https://api.ted.europa.eu/api-v3.yaml>

## Endpoint and auth

`POST https://api.ted.europa.eu/v3/notices/search`

No credential. The docs state the API "does not require authentication"; API keys exist only
for submitting notices, which we never do. **`TedClient` holds no secret.**

## Request

```json
{
  "query": "publication-date>=today(-7) AND publication-date<=today(-3) AND classification-cpv=73000000 AND buyer-country=NLD",
  "fields": ["publication-number", "notice-title", "buyer-country", "description-lot", "classification-cpv", "publication-date", "links"],
  "limit": 250,
  "page": 1
}
```

- Clauses join with `AND`; dates use `>=` / `<=`.
- `buyer-country` takes 3-letter codes — `NLD` works, `NL` is rejected.
- CPV is hierarchical: querying `73000000` returns notices carrying `73112000`. One parent
  code covers its whole branch.
- All three constraints run server-side, so the prefilter goes to TED, not to us.

Response envelope: `{notices, totalNoticeCount, iterationNextToken, timedOut}`.

## Field mapping

| `Notice` field | TED field | Shape |
|---|---|---|
| `id` | `publication-number` | `"632803-2026"` |
| `title` | `notice-title` | dict: language → string (`eng`, `deu`, …) |
| `buyer_country` | `buyer-country` | 3-letter code |
| `notice_text` | `description-lot` | dict: language → list of strings |
| `cpv_codes` | `classification-cpv` | list, contains duplicates |
| `publication_date` | `publication-date` | `"2026-09-15+02:00"` |
| `ted_url` | `links.html.ENG` | dict: language → URL |

Not every notice carries every field.

## Pagination

- Default: `page` + `limit`. Caps at **15k retrievable notices**, 250 per page, and 10k
  fields per page (notices x fields). Exceeding one returns an error.
- Scroll mode: `"paginationMode": "ITERATION"` plus `iterationNextToken` from the previous
  response. No 15k cap and consistent across pages.
- No `RateLimit` or `Retry-After` headers — back off on status codes.

## Gotchas

1. An unfiltered 7-day window returned **17,715 notices**, over the 15k cap. Filter
   server-side or use scroll mode, or the client silently drops notices.
2. `publication-date` carries a UTC offset; Pydantic's `date` won't take it raw.
3. `classification-cpv` returns duplicates — dedup on the way in.
4. Language dicts may lack `eng`; decide the fallback.
5. Send an unsupported `fields` value and the error lists all 1830 valid field names.
