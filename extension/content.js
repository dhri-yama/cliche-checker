// Content script: reads tweet text from the rendered X/Twitter page.
// Deep-scrape driver: auto-scrolls the feed while collecting unique tweet texts.

const TWEET_SELECTORS = [
  'article[data-testid="tweet"] [data-testid="tweetText"]',
  '[data-testid="tweetText"]',
];

class TweetDomReader {
  constructor(documentRef = document) {
    this.documentRef = documentRef;
  }

  collect() {
    const texts = new Set();
    for (const selector of TWEET_SELECTORS) {
      for (const node of this.documentRef.querySelectorAll(selector)) {
        const text = (node.innerText ?? "").trim();
        if (text) {
          texts.add(text);
        }
      }
    }
    return [...texts];
  }
}

class FeedScroller {
  constructor(reader, { target = 150, maxScrolls = 30, settleMs = 1500 } = {}) {
    this.reader = reader;
    this.target = target;
    this.maxScrolls = maxScrolls;
    this.settleMs = settleMs;
  }

  async run() {
    let scrolls = 0;
    let stalls = 0;
    const seen = new Set();

    while (scrolls < this.maxScrolls && seen.size < this.target && stalls < 4) {
      const before = seen.size;
      for (const text of this.reader.collect()) {
        seen.add(text);
      }
      window.scrollBy(0, window.innerHeight * 2.2);
      scrolls += 1;
      await this.sleep(this.settleMs);
      stalls = seen.size === before ? stalls + 1 : 0;
    }
    return [...seen];
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== "SCRAPE_TWEETS") {
    return false;
  }
  const reader = new TweetDomReader();
  const scroller = new FeedScroller(reader);
  scroller
    .run()
    .then((tweets) => sendResponse({ ok: true, tweets, count: tweets.length }))
    .catch((error) => sendResponse({ ok: false, error: `${error}` }));
  return true; // async response
});