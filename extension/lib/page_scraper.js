// Coordinates the deep scrape with the content script in the active tab.

export class PageScraper {
  async scrapeActiveTab() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || tab.id == null) {
      throw new Error("No active tab found.");
    }
    if (!this._looksLikeTweetPage(tab.url)) {
      throw new Error("Open a tweet or hashtag page on x.com first.");
    }

    const response = await chrome.runtime.sendMessage({ type: "SCRAPE", tabId: tab.id });
    if (!response?.ok) {
      throw new Error(response?.error ?? "Scrape failed.");
    }
    return response.tweets ?? [];
  }

  static hashtagFromUrl(url) {
    try {
      const parsed = new URL(url);
      const match = parsed.pathname.match(/\/hashtag\/([^/?]+)/);
      return match ? decodeURIComponent(match[1]) : "";
    } catch {
      return "";
    }
  }

  _looksLikeTweetPage(url) {
    return url && /(x\.com|twitter\.com)\//.test(url);
  }
}