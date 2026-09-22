// Popup entry: wires hashtag prefill → deep scrape → backend grade → result render.

import { GradingApiClient } from "../lib/grading_api.js";
import { PageScraper } from "../lib/page_scraper.js";
import { ResultView } from "../lib/view.js";

const elements = {
  grade: document.querySelector("#grade"),
  draft: document.querySelector("#draft"),
  hashtag: document.querySelector("#hashtag"),
  status: document.querySelector("#status"),
};

const api = new GradingApiClient();
const scraper = new PageScraper();
const view = new ResultView(document);

async function init() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const hashtag = PageScraper.hashtagFromUrl(tab?.url ?? "");
  if (hashtag) {
    elements.hashtag.value = hashtag;
  }
}

async function onGrade() {
  const draft = elements.draft.value.trim();
  if (!draft) {
    setStatus("Paste a draft first.", true);
    return;
  }

  setLoading(true);
  try {
    setStatus("Reading tweets from this page...");
    const tweets = await scraper.scrapeActiveTab();
    if (tweets.length === 0) {
      setStatus("No tweets found yet on this page.", true);
      return;
    }
    setStatus(`Grading against ${tweets.length} tweets...`);
    const result = await api.grade(draft, tweets);
    view.show(result);
    setStatus(`Done — ${tweets.length} tweets scanned.`);
  } catch (error) {
    setStatus(error?.message ?? "Something went wrong.", true);
  } finally {
    setLoading(false);
  }
}

function setLoading(loading) {
  elements.grade.disabled = loading;
  elements.grade.textContent = loading ? "Working..." : "Grade";
}

function setStatus(message, isError = false) {
  elements.status.textContent = message;
  elements.status.classList.toggle("error", isError);
}

elements.grade.addEventListener("click", onGrade);
init();