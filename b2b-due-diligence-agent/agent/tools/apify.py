"""
Apify — Web scraping for LinkedIn profiles, company pages, and domain signals.
Docs: https://docs.apify.com/api/v2
"""

import time
import httpx

from agent.config import (
    APIFY_ACTOR_LINKEDIN,
    APIFY_ACTOR_WEBSITE,
    APIFY_ACTOR_GOOGLE,
    APIFY_TIMEOUT_S,
    APIFY_WEBSITE_PAGES,
    APIFY_GOOGLE_RESULTS,
)


class ApifyScraper:
    BASE_URL = "https://api.apify.com/v2"

    def __init__(self, api_key: str):
        self._api_key = api_key

    def _run_actor(self, actor_id: str, input_data: dict, timeout: int = None) -> dict:
        """Start an Apify actor run, poll until done, return dataset items."""
        if timeout is None:
            timeout = APIFY_TIMEOUT_S
        try:
            with httpx.Client(timeout=30) as client:
                r = client.post(
                    f"{self.BASE_URL}/acts/{actor_id}/runs",
                    params={"token": self._api_key},
                    json=input_data,
                )
                if r.status_code not in (200, 201):
                    return {"error": f"Actor start failed [{actor_id}]: {r.status_code} — {r.text[:250]}"}

                run_data = r.json().get("data", {})
                run_id   = run_data.get("id")
                if not run_id:
                    return {"error": "No run ID returned from Apify"}

                deadline = time.time() + timeout
                status   = "RUNNING"
                while time.time() < deadline:
                    time.sleep(4)
                    sr = client.get(
                        f"{self.BASE_URL}/actor-runs/{run_id}",
                        params={"token": self._api_key},
                    )
                    status = sr.json().get("data", {}).get("status", "")
                    if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
                        break

                if status != "SUCCEEDED":
                    return {"error": f"Actor run ended with status: {status}"}

                dataset_id = sr.json().get("data", {}).get("defaultDatasetId")
                items_r = client.get(
                    f"{self.BASE_URL}/datasets/{dataset_id}/items",
                    params={"token": self._api_key, "limit": 10},
                )
                items = items_r.json()
                return {"status": "success", "actor": actor_id, "items": items}

        except Exception as e:
            return {"error": str(e)}

    # ── Public methods ────────────────────────────────────────────────────────

    def scrape_linkedin_profile(self, linkedin_url: str) -> dict:
        """Scrape a LinkedIn personal profile page."""
        return self._run_actor(
            APIFY_ACTOR_LINKEDIN,
            {"profileUrls": [linkedin_url]},
            timeout=APIFY_TIMEOUT_S,
        )

    def scrape_website(self, url: str, max_pages: int = None) -> dict:
        """Crawl a company website — extract text content and metadata."""
        if max_pages is None:
            max_pages = APIFY_WEBSITE_PAGES
        return self._run_actor(
            APIFY_ACTOR_WEBSITE,
            {
                "startUrls":    [{"url": url}],
                "maxCrawlPages": max_pages,
                "crawlerType":  "cheerio",
            },
            timeout=APIFY_TIMEOUT_S,
        )

    def google_search(self, query: str, max_results: int = None) -> dict:
        """Run a Google search and return organic results."""
        if max_results is None:
            max_results = APIFY_GOOGLE_RESULTS
        return self._run_actor(
            APIFY_ACTOR_GOOGLE,
            {
                "queries":          query,
                "maxPagesPerQuery": 1,
                "resultsPerPage":   max_results,
                "outputFormats":    ["json"],
            },
            timeout=90,
        )
