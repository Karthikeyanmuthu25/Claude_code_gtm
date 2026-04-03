/**
 * InputCollectorAgent
 * Interactively gathers all required fields from the user via CLI.
 * Falls back to defaults for optional fields.
 */

import readline from "readline";

const FIELDS = [
  {
    key: "website",
    prompt: "Company website URL",
    example: "https://acme.com",
    required: true,
    validate: (v) => /^https?:\/\/.+/.test(v) || "Must be a valid URL (https://...)",
  },
  {
    key: "targetLocation",
    prompt: "Target market location",
    example: "United States, India, APAC",
    required: true,
  },
  {
    key: "name",
    prompt: "Your name",
    example: "Priya Krishnan",
    required: true,
  },
  {
    key: "email",
    prompt: "Your email address",
    example: "priya@acme.com",
    required: true,
    validate: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || "Must be a valid email",
  },
  {
    key: "company",
    prompt: "Company name",
    example: "Acme Corp",
    required: true,
  },
  {
    key: "stage",
    prompt: "Company stage",
    example: "Seed / Series A / Series B / Growth / Enterprise",
    required: true,
    choices: ["Pre-seed", "Seed", "Series A", "Series B", "Series C+", "Growth", "Public"],
  },
  {
    key: "space",
    prompt: "Product / market space (what category is this?)",
    example: "B2B SaaS for HR tech / DevTools / FinTech / HealthTech",
    required: true,
  },
  {
    key: "primaryBuyer",
    prompt: "Primary buyer persona",
    example: "CTO, VP Engineering, Head of HR",
    required: true,
  },
  {
    key: "expectedACV",
    prompt: "Expected ACV (Annual Contract Value) in USD",
    example: "25000",
    required: true,
    validate: (v) => (!isNaN(Number(v)) && Number(v) > 0) || "Must be a positive number",
    transform: (v) => Number(v),
  },
  {
    key: "gtmMotion",
    prompt: "Primary GTM motion",
    example: "PLG / Sales-led / Channel / Community-led",
    required: true,
    choices: ["Product-led (PLG)", "Sales-led", "Channel / Partner", "Community-led", "Hybrid"],
  },
];

export class InputCollectorAgent {
  constructor(client, config) {
    this.client = client;
    this.config = config;
  }

  async collect() {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    const ask = (question) =>
      new Promise((resolve) => rl.question(question, resolve));

    console.log("━".repeat(60));
    console.log("  Market Sizing Input Collector");
    console.log("━".repeat(60));
    console.log("  Answer each question — press Enter to submit.\n");

    const answers = {};

    for (const field of FIELDS) {
      let value;
      let valid = false;

      while (!valid) {
        // Show choices if available
        let choiceHint = "";
        if (field.choices) {
          choiceHint = `\n  Options: ${field.choices.join(" | ")}`;
        }

        const raw = await ask(
          `\n  ${field.prompt}${choiceHint}\n  Example: ${field.example}\n  ▶ `
        );
        const trimmed = raw.trim();

        if (!trimmed && field.required) {
          console.log(`  ⚠️  This field is required.`);
          continue;
        }

        if (field.validate && trimmed) {
          const result = field.validate(trimmed);
          if (result !== true) {
            console.log(`  ⚠️  ${result}`);
            continue;
          }
        }

        value = field.transform ? field.transform(trimmed) : trimmed;
        valid = true;
      }

      answers[field.key] = value;
    }

    rl.close();

    console.log("\n  ✅  All inputs collected.\n");
    console.log("━".repeat(60));

    // Use Claude to enrich / normalise inputs
    const enriched = await this._enrich(answers);
    return enriched;
  }

  async _enrich(raw) {
    const msg = await this.client.messages.create({
      model: this.config.model,
      max_tokens: 1024,
      system: `You are a market research assistant. Given raw user inputs, return a JSON object with:
- All original fields preserved exactly
- "industry" — inferred industry vertical from space + website (e.g. "HR Tech", "DevTools", "FinTech")
- "acvTier" — "SMB" (<$10k), "Mid-Market" ($10k–$100k), or "Enterprise" (>$100k) based on expectedACV
- "icp" — concise Ideal Customer Profile sentence
- "geographyCode" — ISO region code(s) e.g. "US", "IN", "APAC"
Return ONLY valid JSON, no markdown fences.`,
      messages: [{ role: "user", content: JSON.stringify(raw) }],
    });

    try {
      const text = msg.content[0].text.trim();
      return JSON.parse(text);
    } catch {
      return raw; // fallback to raw if parse fails
    }
  }
}
