/**
 * AuditLogger
 * Immutable append-only log of all agent actions and tool calls.
 * Written to ./audit-logs/ on flush.
 */

import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export class AuditLogger {
  constructor() {
    this.entries = [];
    this.startTime = Date.now();
  }

  log(event, data = {}) {
    const entry = {
      ts: new Date().toISOString(),
      elapsed: `${((Date.now() - this.startTime) / 1000).toFixed(2)}s`,
      event,
      ...data,
    };
    this.entries.push(entry);
  }

  async flush() {
    const logDir = path.join(__dirname, "..", "audit-logs");
    await fs.mkdir(logDir, { recursive: true });
    const filename = `audit-${Date.now()}.json`;
    const outPath = path.join(logDir, filename);
    await fs.writeFile(outPath, JSON.stringify(this.entries, null, 2), "utf8");
    console.log(`\n📋  Audit log → ${outPath}`);
  }
}
