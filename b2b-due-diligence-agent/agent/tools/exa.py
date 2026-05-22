"""
Exa Search — Neural web search for real-time company/person intelligence.
Docs: https://docs.exa.ai
"""

import httpx


class ExaSearch:
    BASE_URL = "https://api.exa.ai"

    def __init__(self, api_key: str):
        self._headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }

    def _post(self, path: str, payload: dict) -> dict:
        try:
            with httpx.Client(timeout=30) as client:
                r = client.post(f"{self.BASE_URL}{path}", headers=self._headers, json=payload)
                r.raise_for_status()
                return r.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text[:300]}"}
        except Exception as e:
            return {"error": str(e)}

    def search(self, query: str, num_results: int = 5,
               include_domains: list = None,
               exclude_domains: list = None,
               use_autoprompt: bool = True) -> dict:
        """Neural semantic search returning relevant web results."""
        payload = {
            "query":        query,
            "numResults":   num_results,
            "useAutoprompt": use_autoprompt,
            "contents":     {"text": {"maxCharacters": 1000}},
        }
        if include_domains:
            payload["includeDomains"] = include_domains
        if exclude_domains:
            payload["excludeDomains"] = exclude_domains
        return self._post("/search", payload)

    def search_company_intel(self, company_name: str, domain: str = None) -> dict:
        """Stage 2/6 — Search for company news, reviews, red flags, and background."""
        if domain:
            query = f'"{company_name}" OR site:{domain} company review news reputation fraud complaints'
        else:
            query = f'"{company_name}" company review news background fraud scam complaint'
        return self.search(query, num_results=8)

    def search_person_intel(self, name: str, company: str = None, title: str = None) -> dict:
        """Stage 2 — Search for person's professional background and credibility."""
        query = f'"{name}"'
        if company:
            query += f' "{company}"'
        if title:
            query += f' {title}'
        query += " LinkedIn profile career background"
        return self.search(query, num_results=6)

    def verify_domain(self, domain: str) -> dict:
        """Stage 3 — Verify domain credibility, web presence, and signals."""
        return self.search(
            f'site:{domain} OR "{domain}" company about contact information',
            num_results=5,
            use_autoprompt=False,
        )

    def search_risk_signals(self, company_name: str, person_name: str = None) -> dict:
        """Stage 4 — Targeted search for risk, legal, and reputation signals."""
        query = f'"{company_name}" fraud OR scam OR lawsuit OR complaint OR investigation OR warning'
        if person_name:
            query += f' OR "{person_name}" fraud complaint'
        return self.search(query, num_results=6)

    def search_evidence(self, company_name: str, domain: str = None) -> dict:
        """Stage 6 — Gather supporting evidence: awards, news, partnerships, press."""
        query = f'"{company_name}" award OR partnership OR press OR announcement OR achievement'
        if domain:
            query += f' OR site:{domain}'
        return self.search(query, num_results=6)
