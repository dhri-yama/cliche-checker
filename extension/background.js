// Background service worker: relays tab messages and routes scrape requests.

class BackgroundRouter {
  constructor() {
    this.messageHandlers = new Map();
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handle(message, sender).then(sendResponse);
      return true; // keep the message channel open for async responses
    });
  }

  async handle(message, sender) {
    const handler = this.messageHandlers.get(message?.type);
    if (handler) {
      return handler(message, sender);
    }
    return { ok: false, error: `Unknown message type: ${message?.type}` };
  }
}

class ScrapeRelay {
  /** Ask the content script in the given tab to deep-scrape tweet text. */
  static async request(tabId) {
    if (tabId == null) {
      return { ok: false, error: "No active tab." };
    }
    try {
      const response = await chrome.tabs.sendMessage(tabId, { type: "SCRAPE_TWEETS" });
      return response ?? { ok: false, error: "No response from content script." };
    } catch (error) {
      return { ok: false, error: `Could not reach the page scraper: ${error?.message ?? error}` };
    }
  }
}

const router = new BackgroundRouter();
router.messageHandlers.set("SCRAPE", (message) => ScrapeRelay.request(message.tabId));

chrome.runtime.onInstalled.addListener(() => {
  console.log("[cliche-checker] installed");
});