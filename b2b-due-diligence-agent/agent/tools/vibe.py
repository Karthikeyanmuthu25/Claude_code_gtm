"""
Vibe Prospecting — Company & contact enrichment via Explorium backend.
Note: Free-tier Vibe keys may have limited REST API access.
The pipeline continues using Exa + Apify as fallbacks if Vibe is unavailable.
"""

import httpx

# Single authoritative endpoint to try — fail fast if unavailable
_BASE = "https://api.explorium.ai"
_TIMEOUT = 8


class VibeProspecting:
    def __init__(self, api_key: str):
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _post(self, path: str, payload: dict) -> dict:
        try:
            with httpx.Client(timeout=_TIMEOUT, follow_redirects=True) as c:
                r = c.post(f"{_BASE}{path}", headers=self._headers, json=payload)
                if r.status_code < 400:
                    return r.json()
                return {"status": "unavailable", "http_status": r.status_code}
        except Exception as e:
            return {"status": "unavailable", "error": str(e)[:100]}

    def enrich_company(self, domain: str = None, company_name: str = None) -> dict:
        payload_item = {}
        if domain:
            payload_item["domain"] = domain
        if company_name:
            payload_item["name"] = company_name
        return self._post("/v1/businesses/match", {"businesses": [payload_item]})

    def enrich_person(self, email: str = None, linkedin_url: str = None,
                      first_name: str = None, last_name: str = None,
                      company_domain: str = None) -> dict:
        payload_item = {}
        if email:
            payload_item["email"] = email
        if linkedin_url:
            payload_item["linkedin_url"] = linkedin_url
        if first_name:
            payload_item["first_name"] = first_name
        if last_name:
            payload_item["last_name"] = last_name
        if company_domain:
            payload_item["company_domain"] = company_domain
        return self._post("/v1/prospects/match", {"prospects": [payload_item]})

    def search_companies(self, query: str, limit: int = 5) -> dict:
        return self._post("/v1/companies/search", {"query": query, "limit": limit})
