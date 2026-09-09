# tender-scout

Scouts EU public-procurement tenders on behalf of a single company and produces a
daily digest of the ones worth bidding on. Built as a learning project; the reference
company is Fugro (a Geo-data firm), used as a stand-in — this project is not affiliated
with Fugro.

## Language

**Tender**:
A public buyer's announcement that it intends to award a contract, open for bids until
a stated deadline. In this project a tender always originates from TED.
_Avoid_: Bid (that is what the supplier submits in response), Opportunity, RFP.

**Notice**:
One published record on TED describing a tender. The atomic unit tender-scout fetches,
filters, scores, and reports. Each has a stable identifier used for deduplication.
_Avoid_: Listing, Posting, Entry.

**TED**:
Tenders Electronic Daily (`ted.europa.eu`), the EU's official publication channel for
above-threshold public contracts. The sole data source.
_Avoid_: OJEU, "the EU portal".

**CPV code**:
A code from the Common Procurement Vocabulary, the EU's standard classification of
what a contract is for. Every notice carries one or more. Used as the primary cheap
filter for whether a notice could concern the company.
_Avoid_: Category, Sector code, Tag.

**Prefilter**:
The non-AI narrowing step: keep only notices whose CPV codes and country match the
configured lists. Runs before any scoring.
_Avoid_: Layer 1, Screening, Pre-selection.

**Company profile**:
A short prose description of what the company does, written by the user. The text the
relevance score is judged against.
_Avoid_: Bio, Description, Persona.

**Relevance score**:
An integer from 1 to 100 expressing how well a prefiltered notice fits the company
profile, assigned by a language model. Only meaningful in broad bands, not point values.
_Avoid_: Rating, Rank, Confidence, Match percentage.

**Rationale**:
The one-sentence explanation, in English, that accompanies each relevance score.
_Avoid_: Reason, Justification, Note.

**Digest**:
The output artifact of a run: notices that scored at or above the threshold, sorted by
score, each with its rationale and a link to the notice on TED.
_Avoid_: Report, Feed, Summary, Newsletter.

**Run**:
One end-to-end execution: fetch, prefilter, score, threshold, write digest, record what
was seen. Happens once per day when deployed, or on demand from the CLI.
_Avoid_: Job, Cycle, Pass.

**Seen**:
The state of a notice having been included in a previous digest. Seen notices are
excluded from future digests. A notice is marked seen only after a run succeeds for it.
_Avoid_: Processed, Handled, Done, Archived.

**Fetch window**:
The fixed span of time a run asks TED for — the last 7 days — regardless of when the
previous run happened. Overlap between runs is expected and absorbed by the seen state.
_Avoid_: Lookback, Range, Since-time.
