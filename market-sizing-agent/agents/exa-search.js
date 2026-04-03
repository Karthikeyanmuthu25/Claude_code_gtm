/**
 * ExaSearchAgent
 * Performs semantic searches via Exa API across multiple data source categories
 * to gather market sizing intelligence.
 *
 * Data source categories:
 *  1. Industry reports (Gartner, Forrester, IDC, G2, Statista)
 *  2. Crunchbase / funding data
 *  3. LinkedIn / company data
 *  4. News & press releases
 *  5. Competitor landscape
 *  6. Regulatory / compliance
 */

import fetch from "node-fetch";

const EXA_API = "https://api.exa.ai/search";

// Data source domains per category
const DATA_SOURCES = {
  industryReports: [
    "gartner.com",
    "forrester.com",
    "idc.com",
    "g2.com",
    "statista.com",
    "grandviewresearch.com",
    "marketsandmarkets.com",
    "mordorintelligence.com",
    "businesswire.com",
    "globenewswire.com",
  ],
  fundingData: [
    "crunchbase.com",
    "pitchbook.com",
    "techcrunch.com",
    "venturebeat.com",
  ],
  companyData: [
    "linkedin.com",
    "glassdoor.com",
    "builtwith.com",
    "similarweb.com",
  ],
  news: [
    "reuters.com",
    "bloomberg.com",
    "wsj.com",
    "ft.com",
    "forbes.com",
    "inc.com",
  ],
  competitors: [
    "producthunt.com",
    "capterra.com",
    "g2.com",
    "getapp.com",
    "trustradius.com",
  ],
};

export class ExaSearchAgent {
  constructor(apiKey, audit) {
    this.apiKey = apiKey;
    this.audit = audit;
    this.results = {};
  }

  /**
   * Build all search queries from inputs and run them in parallel batches.
   */
  async run(inputs) {
    const queries = this._buildQueries(inputs);
    console.log(`  Running ${queries.length} semantic searches across ${Object.keys(DATA_SOURCES).length} source categories...`);

    // Run in parallel batches of 5 to avoid rate limits
    const BATCH_SIZE = 5;
    const allResults = [];

    for (let i = 0; i < queries.length; i += BATCH_SIZE) {
      const batch = queries.slice(i, i + BATCH_SIZE);
      const batchResults = await Promise.all(batch.map((q) => this._search(q)));
      allResults.push(...batchResults);
      if (i + BATCH_SIZE < queries.length) {
        await this._sleep(500); // polite pause between batches
      }
    }

    // Aggregate by category
    const aggregated = {};
    for (const result of allResults) {
      if (!aggregated[result.category]) aggregated[result.category] = [];
      aggregated[result.category].push(...(result.hits ?? []));
    }

    return {
      queriesRun: queries.length,
      categories: aggregated,
      rawInputs: inputs,
    };
  }

  _buildQueries(inputs) {
    const { space, targetLocation, primaryBuyer, expectedACV, gtmMotion, industry, acvTier } = inputs;

    return [
      // ── Industry reports ────────────────────────────────────────────────
      {
        query: `${space} market size TAM SAM SOM ${targetLocation} 2024 2025`,
        category: "industryReports",
        includeDomains: DATA_SOURCES.industryReports,
        numResults: 8,
      },
      {
        query: `${industry || space} total addressable market forecast growth rate`,
        category: "industryReports",
        includeDomains: DATA_SOURCES.industryReports,
        numResults: 6,
      },
      {
        query: `${space} industry revenue statistics ${targetLocation} enterprise`,
        category: "industryReports",
        includeDomains: DATA_SOURCES.industryReports,
        numResults: 5,
      },

      // ── Funding / competitive landscape ─────────────────────────────────
      {
        query: `${space} startup funding rounds 2023 2024 venture capital investment`,
        category: "fundingData",
        includeDomains: DATA_SOURCES.fundingData,
        numResults: 8,
      },
      {
        query: `${space} ${targetLocation} series A B funding valuation`,
        category: "fundingData",
        includeDomains: DATA_SOURCES.fundingData,
        numResults: 6,
      },

      // ── Buyer / ICP data ─────────────────────────────────────────────────
      {
        query: `${primaryBuyer} ${space} buying decisions budget software ${targetLocation}`,
        category: "buyerData",
        includeDomains: [...DATA_SOURCES.companyData, ...DATA_SOURCES.industryReports],
        numResults: 6,
      },
      {
        query: `${primaryBuyer} pain points challenges ${space} solutions 2024`,
        category: "buyerData",
        includeDomains: [...DATA_SOURCES.news, ...DATA_SOURCES.companyData],
        numResults: 5,
      },

      // ── Competitor landscape ─────────────────────────────────────────────
      {
        query: `best ${space} software tools ${targetLocation} alternatives competitors`,
        category: "competitors",
        includeDomains: DATA_SOURCES.competitors,
        numResults: 8,
      },
      {
        query: `${space} market share leaders ${targetLocation} top companies`,
        category: "competitors",
        includeDomains: [...DATA_SOURCES.industryReports, ...DATA_SOURCES.fundingData],
        numResults: 6,
      },

      // ── GTM benchmarks ───────────────────────────────────────────────────
      {
        query: `${gtmMotion} ${space} SaaS benchmark ACV ${acvTier || ""} ${targetLocation}`,
        category: "gtmBenchmarks",
        includeDomains: [...DATA_SOURCES.industryReports, ...DATA_SOURCES.news],
        numResults: 5,
      },
      {
        query: `SaaS ${space} average contract value pricing model ${targetLocation}`,
        category: "gtmBenchmarks",
        includeDomains: DATA_SOURCES.industryReports,
        numResults: 5,
      },

      // ── News & trends ────────────────────────────────────────────────────
      {
        query: `${space} market trends disruption 2024 2025 ${targetLocation}`,
        category: "news",
        includeDomains: DATA_SOURCES.news,
        numResults: 6,
      },
      {
        query: `${industry || space} regulatory compliance changes ${targetLocation} 2024`,
        category: "news",
        includeDomains: DATA_SOURCES.news,
        numResults: 4,
      },
    ];
  }

  async _search({ query, category, includeDomains, numResults = 5 }) {
    this.audit.log("EXA_SEARCH", { query, category, numResults });

    try {
      const response = await fetch(EXA_API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": this.apiKey,
        },
        body: JSON.stringify({
          query,
          numResults,
          includeDomains,
          useAutoprompt: true,
          type: "neural",
          contents: {
            text: { maxCharacters: 800 },
            highlights: { numSentences: 3, highlightsPerUrl: 2 },
          },
        }),
      });

      if (!response.ok) {
        const err = await response.text();
        console.warn(`  ⚠️  Exa search failed [${category}]: ${response.status} — ${err}`);
        return { category, hits: [] };
      }

      const data = await response.json();
      const hits = (data.results ?? []).map((r) => ({
        title: r.title,
        url: r.url,
        snippet: r.text?.substring(0, 600) ?? "",
        highlights: r.highlights ?? [],
        publishedDate: r.publishedDate,
        domain: new URL(r.url).hostname,
      }));

      console.log(`  ✓ [${category}] "${query.substring(0, 50)}..." → ${hits.length} results`);
      return { category, hits };
    } catch (err) {
      console.warn(`  ⚠️  Exa error [${category}]: ${err.message}`);
      return { category, hits: [] };
    }
  }

  _sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }
}
