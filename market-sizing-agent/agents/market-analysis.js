/**
 * MarketAnalysisAgent
 * Uses Claude to synthesise Exa search data into structured market sizing metrics:
 * TAM / SAM / SOM, competitive landscape, ICP fit, GTM fit score, and key risks.
 */

import { MARKET_ANALYSIS_PROMPT } from "../prompts/market-analysis.js";

export class MarketAnalysisAgent {
  constructor(client, config, context, audit) {
    this.client = client;
    this.config = config;
    this.context = context;
    this.audit = audit;
  }

  async run() {
    const inputs = this.context.get("inputs");
    const searchData = this.context.get("searchData");

    // Build a condensed evidence package to fit context window
    const evidence = this._condenseEvidence(searchData);

    this.audit.log("MARKET_ANALYSIS_START", {
      evidenceSnippets: evidence.totalSnippets,
      categories: Object.keys(evidence.byCategory),
    });

    const userMsg = JSON.stringify({
      inputs,
      evidence: evidence.byCategory,
    });

    const response = await this.client.messages.create({
      model: this.config.model,
      max_tokens: this.config.maxTokens,
      system: MARKET_ANALYSIS_PROMPT,
      messages: [{ role: "user", content: userMsg }],
    });

    const raw = response.content[0].text.trim();

    // Parse JSON analysis
    let analysis;
    try {
      // Strip markdown fences if present
      const cleaned = raw.replace(/^```json\s*/i, "").replace(/\s*```$/, "");
      analysis = JSON.parse(cleaned);
    } catch {
      console.warn("  ⚠️  Analysis JSON parse failed, using raw text");
      analysis = { raw };
    }

    this.audit.log("MARKET_ANALYSIS_COMPLETE", {
      tam: analysis.tam,
      sam: analysis.sam,
      som: analysis.som,
    });

    return analysis;
  }

  /**
   * Condense Exa results into a token-efficient evidence package.
   * Caps each category at 5 snippets × 400 chars to stay within context.
   */
  _condenseEvidence(searchData) {
    const { categories } = searchData;
    const byCategory = {};
    let totalSnippets = 0;

    for (const [cat, hits] of Object.entries(categories)) {
      const topHits = (hits ?? []).slice(0, 6).map((h) => ({
        title: h.title,
        url: h.url,
        snippet: (h.snippet ?? "").substring(0, 400),
        highlights: (h.highlights ?? []).slice(0, 2),
        date: h.publishedDate,
      }));
      byCategory[cat] = topHits;
      totalSnippets += topHits.length;
    }

    return { byCategory, totalSnippets };
  }
}
