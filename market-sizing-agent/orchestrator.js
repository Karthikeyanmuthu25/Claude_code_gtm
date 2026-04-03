#!/usr/bin/env node
/**
 * Market Sizing Orchestrator
 * Coordinates all sub-agents to produce a personalised market sizing report.
 *
 * Usage:
 *   node orchestrator.js                 # interactive CLI mode
 *   node orchestrator.js --json input.json  # batch mode from JSON file
 */

import Anthropic from "@anthropic-ai/sdk";
import readline from "readline";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

import { InputCollectorAgent } from "./agents/input-collector.js";
import { ExaSearchAgent } from "./agents/exa-search.js";
import { MarketAnalysisAgent } from "./agents/market-analysis.js";
import { ReportGeneratorAgent } from "./agents/report-generator.js";
import { AuditLogger } from "./utils/audit-logger.js";
import { ContextManager } from "./utils/context-manager.js";
import { PermissionGate } from "./utils/permission-gate.js";
import { renderMarkdownToHtml } from "./utils/chart-renderer.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ── Config ──────────────────────────────────────────────────────────────────
const CONFIG = {
  model: "claude-opus-4-5",
  maxTokens: 8192,
  outputDir: path.join(__dirname, "reports"),
  exaApiKey: process.env.EXA_API_KEY || "YOUR_EXA_API_KEY_HERE",
  anthropicApiKey: process.env.ANTHROPIC_API_KEY,
};

// ── Orchestrator ─────────────────────────────────────────────────────────────
class MarketSizingOrchestrator {
  constructor() {
    this.client = new Anthropic({ apiKey: CONFIG.anthropicApiKey });
    this.audit = new AuditLogger();
    this.context = new ContextManager();
    this.gate = new PermissionGate();
    this.taskQueue = [];
    this.results = {};
  }

  async run(preloadedInputs = null) {
    console.log("\n🚀  Market Sizing Sub-Agent System\n");
    this.audit.log("ORCHESTRATOR_START", { timestamp: new Date().toISOString() });

    try {
      // ── Phase 1: Collect inputs ──────────────────────────────────────────
      console.log("📋  Phase 1 — Collecting inputs...\n");
      const collector = new InputCollectorAgent(this.client, CONFIG);
      const inputs = preloadedInputs ?? (await collector.collect());
      this.context.set("inputs", inputs);
      this.audit.log("INPUTS_COLLECTED", inputs);

      // ── Phase 2: Exa semantic search ────────────────────────────────────
      console.log("\n🔍  Phase 2 — Semantic search (Exa)...\n");
      const searcher = new ExaSearchAgent(CONFIG.exaApiKey, this.audit);
      const searchData = await searcher.run(inputs);
      this.context.set("searchData", searchData);
      this.audit.log("SEARCH_COMPLETE", { queriesRun: searchData.queriesRun });

      // ── Phase 3: Market analysis ─────────────────────────────────────────
      console.log("\n📊  Phase 3 — Market analysis sub-agent...\n");
      const analyst = new MarketAnalysisAgent(this.client, CONFIG, this.context, this.audit);
      const analysis = await analyst.run();
      this.context.set("analysis", analysis);

      // ── Phase 4: Report generation ───────────────────────────────────────
      console.log("\n📝  Phase 4 — Generating personalised report...\n");
      const reporter = new ReportGeneratorAgent(this.client, CONFIG, this.context, this.audit);
      const report = await reporter.run();

      // ── Write output ─────────────────────────────────────────────────────
      await fs.mkdir(CONFIG.outputDir, { recursive: true });
      const slug = inputs.company
        .toLowerCase()
        .replace(/[^a-z0-9]/g, "-")
        .substring(0, 30);
      const filename = `${slug}-market-sizing-${Date.now()}.md`;
      const outPath = path.join(CONFIG.outputDir, filename);

      // Permission gate for file write
      await this.gate.check("FILE_WRITE", { path: outPath });
      await fs.writeFile(outPath, report, "utf8");
      this.audit.log("REPORT_WRITTEN", { path: outPath });
      console.log(`\n✅  Markdown report saved → ${outPath}`);

      // Auto-render HTML with inline Chart.js charts
      console.log("📊  Rendering interactive HTML with charts...");
      const htmlPath = await renderMarkdownToHtml(outPath);
      this.audit.log("HTML_REPORT_WRITTEN", { path: htmlPath });

      console.log(`\n🎉  Done!`);
      console.log(`    Markdown → ${outPath}`);
      console.log(`    HTML     → ${htmlPath}\n`);
      return { success: true, path: outPath, htmlPath, report };
    } catch (err) {
      this.audit.log("ORCHESTRATOR_ERROR", { error: err.message });
      console.error("\n❌  Orchestrator error:", err.message);
      throw err;
    } finally {
      await this.audit.flush();
    }
  }
}

// ── Entry point ──────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
let preloaded = null;

if (args.includes("--json")) {
  const jsonIndex = args.indexOf("--json") + 1;
  const jsonPath = args[jsonIndex];
  const raw = await fs.readFile(jsonPath, "utf8");
  preloaded = JSON.parse(raw);
}

const orchestrator = new MarketSizingOrchestrator();
await orchestrator.run(preloaded);
