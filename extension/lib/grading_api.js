// Talks to the Python backend; owns the backend base URL.

export class GradingApiClient {
  constructor(baseUrl = "http://127.0.0.1:8000") {
    this.baseUrl = baseUrl;
  }

  async grade(draft, tweets) {
    const response = await fetch(`${this.baseUrl}/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ draft, tweets }),
    });
    if (!response.ok) {
      const detail = await response.json().then((body) => body.detail).catch(() => response.statusText);
      throw new Error(`${detail ?? "Backend error"} (${response.status})`);
    }
    return response.json();
  }
}