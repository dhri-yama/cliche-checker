// DOM rendering for the grading result.

export class ResultView {
  constructor(root = document) {
    this.root = root;
    this.results = root.querySelector("#results");
    this.score = root.querySelector("#score-value");
    this.verdict = root.querySelector("#verdict-value");
    this.confidence = root.querySelector("#confidence-value");
    this.saturated = root.querySelector("#saturated-value");
    this.latency = root.querySelector("#latency-value");
  }

  show(result) {
    this.score.textContent = String(result.originality);
    this.score.parentElement.classList.remove("good", "mid", "bad");
    this.score.parentElement.classList.add(this._bucket(result.originality));
    this.verdict.textContent = result.verdict;
    this.confidence.textContent = `${(result.verdict_confidence * 100).toFixed(0)}%`;
    this.saturated.textContent = `${(result.saturated * 100).toFixed(0)}%`;
    this.latency.textContent = `${result.jev_ms.toFixed(0)} ms`;
    this.results.classList.remove("hidden");
  }

  _bucket(score) {
    if (score >= 67) return "good";
    if (score >= 34) return "mid";
    return "bad";
  }
}