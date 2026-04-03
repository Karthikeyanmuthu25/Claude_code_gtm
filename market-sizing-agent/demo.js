/**
 * Demo script — runs the full pipeline with hardcoded sample inputs.
 * No interactive prompts. Good for testing the pipeline end-to-end.
 *
 * Usage: node demo.js
 */

import { MarketSizingOrchestrator } from "./orchestrator.js";

// Patch orchestrator to accept preloaded inputs directly
import Anthropic from "@anthropic-ai/sdk";
import { ExaSearchAgent } from "./agents/exa-search.js";
import { MarketAnalysisAgent } from "./agents/market-analysis.js";
import { ReportGeneratorAgent } from "./agents/report-generator.js";
import { AuditLogger } from "./utils/audit-logger.js";
import { ContextManager } from "./utils/context-manager.js";
import { PermissionGate } from "./utils/permission-gate.js";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const CONFIG = {
  model: "claude-opus-4-5",
  maxTokens: 8192,
  outputDir: path.join(__dirname, "reports"),
  exaApiKey: process.env.EXA_API_KEY || "YOUR_EXA_API_KEY_HERE",
  anthropicApiKey: process.env.ANTHROPIC_API_KEY,
};

// ── Sample inputs (replace with real values to test) ─────────────────────────
const DEMO_INPUTS = {
  website: "https://acme-hrtech.com",
  targetLocation: "United States",
  name: "Priya Krishnan",
  email: "priya@acme-hrtech.com",
  company: "Acme HRTech",
  stage: "Series A",
  space: "AI-powered HR performance management software",
  primaryBuyer: "VP of People / CHRO",
  expectedACV: 45000,
  gtmMotion: "Sales-led",
  // Enriched fields (normally added by InputCollectorAgent)
  industry: "HR Tech",
  acvTier: "Mid-Market",
  icp: "Mid-market companies (200-2000 employees) with VP People or CHRO as primary buyer",
  geographyCode: "US",
};

async function runDemo() {
  console.log("\n🚀  Market Sizing Agent — DEMO MODE\n");
  console.log("  Using pre-configured inputs for: Acme HRTech\n");

  const client = new Anthropic({ apiKey: CONFIG.anthropicApiKey });
  const audit = new AuditLogger();
  const context = new ContextManager();
  const gate = new PermissionGate();

  try {
    // Phase 1: Skip collection, use demo inputs
    context.set("inputs", DEMO_INPUTS);
    audit.log("DEMO_INPUTS_SET", DEMO_INPUTS);

    // Phase 2: Exa search
    console.log("🔍  Phase 2 — Semantic search (Exa)...\n");
    const searcher = new ExaSearchAgent(CONFIG.exaApiKey, audit);
    const searchData = await searcher.run(DEMO_INPUTS);
    context.set("searchData", searchData);

    // Phase 3: Market analysis
    console.log("\n📊  Phase 3 — Market analysis...\n");
    const analyst = new MarketAnalysisAgent(client, CONFIG, context, audit);
    const analysis = await analyst.run();
    context.set("analysis", analysis);

    // Phase 4: Report generation
    console.log("\n📝  Phase 4 — Generating report...\n");
    const reporter = new ReportGeneratorAgent(client, CONFIG, context, audit);
    const report = await reporter.run();

    // Save
    await fs.mkdir(CONFIG.outputDir, { recursive: true });
    const outPath = path.join(CONFIG.outputDir, `demo-acme-hrtech-${Date.now()}.md`);
    await fs.writeFile(outPath, report, "utf8");
    console.log(`\n✅  Demo report saved → ${outPath}\n`);
    console.log("─".repeat(60));
    console.log(report.substring(0, 500) + "\n...\n");
  } catch (err) {
    console.error("❌  Demo error:", err.message);
  } finally {
    await audit.flush();
  }
}

runDemo();
