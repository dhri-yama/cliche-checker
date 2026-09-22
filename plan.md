# cliche-checker — Implementation Plan

Grade whether a social post draft is original or cliché within a niche.
No scraping API: the browser extension reads tweets from the hashtag page the
user already has open; a Python FastAPI backend runs the Jev judgment.

## Goal
On an open X/Twitter hashtag page (Top tab):
- User pastes a draft in the extension popup
- Content script auto-scrolls and collects rendered tweet text (~150 posts)
- Backend cleans the corpus and asks TypeSafe Jev `system_one` to grade
- Popup shows:
  - `originality` — 0–100 freshness score
  - `verdict`    — rework / refine / publish (Choice)
  - `saturated`  — rehashed-angle probability (Noul)

## Structure
```
cliche-checker/
├── plan.md
├── .env                  # TYPESAFE_API_KEY (gitignored)
├── .gitignore
├── requirements.txt      # typesafe-sdk fastapi uvicorn[standard] python-dotenv
├── backend/
│   ├── config.py         # Settings (frozen; loads .env once)
│   ├── domain/           # models, rubrics, exceptions
│   ├── ports/            # Protocols: Cleaner, BudgetPolicy, QuestionFactory, Judge
│   ├── adapters/         # text_cleaner, token_budget, state_builder, jev_questions, judges
│   ├── services/         # GradingService orchestrator
│   ├── container.py      # composition root (DI)
│   └── api/              # FastAPI app_factory, schemas, routes (controllers)
└── extension/            # Chrome MV3
    ├── manifest.json
    ├── background.js
    ├── content.js        # TweetDomReader: selector extraction + auto-scroll
    ├── popup/            # popup.html/.css/.js
    └── lib/              # page_scraper.js, grading_api.js, view.js
```

## SOLID mapping
| Principle | Where |
|---|---|
| SRP | One job per class: cleaners clean, budget samples, StateBuilder assembles, JevQuestionFactory defines questions, JevJudge calls the API, GradingService orchestrates, controllers do HTTP only |
| OCP | Swap Judge / Cleaner / BudgetPolicy / Rubric via the container |
| LSP | StubJudge and JevJudge share the Judge contract → interchangeable in dev/tests |
| ISP | Four narrow protocols instead of one fat interface |
| DIP | GradingService depends on Protocols, injected from Container |

## Flow
1. User opens `x.com/hashtag/xyz` (Top tab) → clicks extension icon
2. Popup opens, hashtag pre-filled from tab URL, user pastes draft → Grade
3. PageScraper asks content.js to deep-scrape tweet text (scroll cap / timeout)
4. `POST /check {draft, tweets}` → Cleaning → TokenSamplingBudget → StateBuilder
   → JevQuestionFactory → JevJudge
5. Popup renders originality /100, verdict, saturated %, latency

## Design decisions
- Jev budget: 32k tokens for state + longest question; corpus ≈ 10–15k tokens safe
- Corpus note in state defines recurrence-as-cliché baseline
- Token guard: even-sample corpus down to ~30k-token budget when oversized
- Stub judge available so `/check` runs without an API key (dev/tests/LSP)

## Verification
- Backend: uvicorn → curl /health; curl POST /check (real + stub)
- Extension: chrome://extensions → Load unpacked → extension/
- E2E: cliché draft vs fresh draft on a real hashtag page; Jev < 1s; no Apify

## Risks
- X.com DOM selectors are brittle → one fallback strategy, validated on real page
- Deep-scrape capped so popup never hangs on infinite feeds