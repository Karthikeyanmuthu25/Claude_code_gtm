/**
 * ReportGeneratorAgent
 * Takes the structured analysis and generates a personalised, publication-quality
 * Markdown market sizing report.
 */

import { REPORT_GENERATOR_PROMPT } from "../prompts/report-generator.js";

export class ReportGeneratorAgent {
  constructor(client, config, context, audit) {
    this.client = client;
    this.config = config;
    this.context = context;
    this.audit = audit;
  }

  async run() {
    const inputs = this.context.get("inputs");
    const analysis = this.context.get("analysis");
    const searchData = this.context.get("searchData");

    this.audit.log("REPORT_GENERATION_START", { company: inputs.company });

    // Build source citation list
    const sources = this._collectSources(searchData);

    const userMsg = JSON.stringify({
      inputs,
      analysis,
      sources: sources.slice(0, 20), // top 20 sources for citations
      generatedAt: new Date().toISOString(),
    });

    const response = await this.client.messages.create({
      model: this.config.model,
      max_tokens: this.config.maxTokens,
      system: REPORT_GENERATOR_PROMPT,
      messages: [{ role: "user", content: userMsg }],
    });

    const report = response.content[0].text.trim();
    this.audit.log("REPORT_GENERATION_COMPLETE", { chars: report.length });

    return report;
  }

  _collectSources(searchData) {
    const seen = new Set();
    const sources = [];

    for (const hits of Object.values(searchData.categories)) {
      for (const hit of hits ?? []) {
        if (!seen.has(hit.url)) {
          seen.add(hit.url);
          sources.push({
            title: hit.title,
            url: hit.url,
            domain: hit.domain,
            date: hit.publishedDate,
          });
        }
      }
    }

    return sources;
  }
}
