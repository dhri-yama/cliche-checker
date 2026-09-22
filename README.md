# cliche-checker

Grade whether a social post draft is **original or cliché** — judged against the tweets
actually dominating a hashtag right now.

No scraping APIs, no API keys shipped in the browser: a **Chrome MV3 extension** reads the
tweets already rendered on the X/Twitter hashtag page you have open, and a **Python FastAPI
backend** (hexagonal architecture) asks **TypeSafe Jev** to grade your draft with
typed, calibrated answers instead of free-form LLM prose.

```
┌─────────────────────────── Chrome extension ───────────────────────────┐
│  popup: paste draft → Grade                                           │
│     │                                                                 │
│     ├─► background.js ──► content.js (auto-scroll + read tweetText)   │
│     │                       ~150 tweets from the open hashtag page    │
│     └─► POST http://127.0.0.1:8000/check {draft, tweets}              │
└────────────────────────────────────────────────────────────────────────┘
                                 │
┌───────────────────────────────▼───────────────────────────────────────┐
│  FastAPI backend (hexagonal: domain · ports · adapters · services)    │
│     clean ─► budget ─► StateBuilder ─► questions ─► Jev (TypeSafe)    │
│     returns: originality 0-100 · verdict · saturated · latency       │
└────────────────────────────────────────────────────────────────────────┘
```

## What you get

| Output | Type primitive | Meaning |
|---|---|---|
| `originality` | `Score` (0–100) | How fresh your draft is vs. the corpus — recurring themes score low |
| `verdict` | `Choice` | `rework` / `refine` / `publish` — what to do with the draft |
| `verdict_confidence` | (on Choice) | How certain the model is about the verdict |
| `saturated` | `Noul` (0–1) | Probability the draft re-hashes an angle already hammered |
| `jev_ms` | — | Jev round-trip time (backend-side, excludes scraping) |

## How it works

1. Open a hashtag page on **x.com**, e.g. `x.com/hashtag/productivity` on the **Top** tab.
2. Click the extension icon → popup opens with the hashtag prefilled from the URL.
3. Paste your draft (≤ 280 chars) → **Grade**.
4. The content script **auto-scrolls** the feed, collecting unique tweet texts until it
   reaches ~150 posts, the feed stalls, or it hits its scroll/timeout cap.
5. The popup sends `{draft, tweets}` to the backend.
6. The backend **cleans** the corpus (drops retweets/URL-only posts, strips `@mentions`,
   `#hashtags`, and links, dedupes), applies a **token budget** (evenly samples down to fit
   Jev's 32k-token state limit), and calls `system_one` with three typed questions.
7. The popup renders `originality /100`, `verdict`, `saturated %`, and latency.

## Architecture

Layered **hexagonal / ports-and-adapters** design:

```
backend/
├── config.py           # Settings (frozen dataclass, loads .env once)
├── domain/             # Pure domain: models, rubric, exceptions (no framework deps)
├── ports/              # Protocols (abstractions only): Cleaner, BudgetPolicy,
│                       #   QuestionFactory, Judge
├── adapters/           # Concrete implementations of each port
├── services/           # GradingService — the single orchestration point
├── container.py        # Composition root (DI wiring)
└── api/                # FastAPI app factory, DTOs, controllers (HTTP only)
```

## Project structure

```
cliche-checker/
├── plan.md                      # Full implementation plan & decisions
├── requirements.txt             # typesafe-sdk, fastapi, uvicorn, python-dotenv
├── .env                         # TYPESAFE_API_KEY (never committed)
├── backend/                     # Python backend (hexagonal architecture)
│   ├── config.py
│   ├── domain/                  # models.py · rubrics.py · exceptions.py
│   ├── ports/                   # Protocols: cleaner · budget · question_factory · judge
│   ├── adapters/                # text_cleaner · token_budget · state_builder
│   │                            # jev_questions · jev_judge · stub_judge
│   ├── services/grading_service.py
│   ├── container.py             # Composition root (DI)
│   └── api/
│       ├── app_factory.py       # create_app() + CORS
│       ├── schemas.py           # Pydantic DTOs
│       └── routes/              # health_controller · check_controller
└── extension/                   # Chrome MV3 extension
    ├── manifest.json
    ├── background.js            # Message relay between popup and content script
    ├── content.js               # TweetDomReader + FeedScroller (auto-scroll scrape)
    ├── popup/                   # popup.html · popup.css · popup.js (ES modules)
    └── lib/                     # page_scraper · grading_api · view
```

## Setup

### Prerequisites
- Python **≥ 3.10** (TypeSafe SDK requirement)
- A [TypeSafe AI](https://docs.typesafe.ai) account + `TYPESAFE_API_KEY`
- Google Chrome (or any Chromium browser) for the extension

### 1. Backend

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# .env — your key, gitignored
echo "TYPESAFE_API_KEY=your-key-here" > .env

# start the server
.venv/bin/uvicorn backend.api.app_factory:app --reload
```

Without a key, run in **stub mode** (deterministic answers, full pipeline works for dev/tests):

```bash
RUN_MODE=stub .venv/bin/uvicorn backend.api.app_factory:app
```

### 2. Extension

1. Open `chrome://extensions`
2. Toggle **Developer mode** (top-right)
3. **Load unpacked** → select the `extension/` folder
4. Navigate to `x.com/hashtag/<your-topic>` (Top tab)
5. Click the extension icon → paste draft → **Grade**

## Configuration

| Env var | Default | Description |
|---|---|---|
| `TYPESAFE_API_KEY` | — | TypeSafe API key (required for `live` mode) |
| `RUN_MODE` | `live` | `live` → real Jev calls; `stub` → deterministic `StubJudge` |
| `TYPESAFE_MODEL` | `jev-latest` | Jev model id |
| `MAX_STATE_TOKENS` | `30000` | Corpus is sampled down to fit this state budget |
| `HOST` | `127.0.0.1` | Bind address |
| `PORT` | `8000` | Server port |

## API reference

### `GET /health`

```json
{ "status": "ok", "mode": "stub" }
```

### `POST /check`

```json
// request
{ "draft": "Hustle culture is toxic. Rest is the real work.", "tweets": ["...", "..."] }

// response (200)
{ "originality": 75, "verdict": "publish", "verdict_confidence": 0.9, "saturated": 0.1, "jev_ms": 0.0 }
```

Errors: `422` empty corpus after cleaning · `503` missing API key · `502` judge failure.

```bash
curl -s http://127.0.0.1:8000/check \
  -H 'Content-Type: application/json' \
  -d '{"draft":"Just start. You will never be ready.","tweets":["Discipline over motivation.","Consistency beats intensity."]}'
```

## Design decisions & risks

- **Token budget:** Jev's `state` limit is 32k tokens; the corpus (~100–200 tweets) fits
  comfortably. `TokenSamplingBudget` evenly samples down if it ever exceeds `MAX_STATE_TOKENS`.
- **Rubric** lives in `backend/domain/rubrics.py`: 5 ordered `Score` levels (overdone cliché →
  genuinely distinctive), a 3-option `verdict` `Choice`, and a `saturated` `Noul`. The
  `corpus_note` in the state tells Jev that recurrence across posts = cliché baseline — Jev is
  literal, so stating how to read the corpus matters.
- **No Apify:** the open page *is* the source. This keeps costs at zero and keeps the key out
  of the browser, but it means you must be on the page you want to grade against.
- **X.com DOM is brittle:** `content.js` uses `article[data-testid="tweet"] [data-testid="tweetText"]`
  with a fallback selector; if X changes its markup, update `TWEET_SELECTORS`.
- **Deep scrape is capped** (scrolls/timeout/stall detection) so the popup never hangs on an
  infinite feed.
- **Keys are never in the extension** — only the backend reads `.env`, which is gitignored.

## Development

```bash
# backend
RUN_MODE=stub .venv/bin/uvicorn backend.api.app_factory:app --reload
python -m compileall backend

# extension — edit files, then reload it on chrome://extensions
```

## License

Private / unlicensed unless otherwise stated.
