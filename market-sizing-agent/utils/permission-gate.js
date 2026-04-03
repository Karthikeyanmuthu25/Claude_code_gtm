/**
 * PermissionGate
 * Checks all tool calls and file operations against an allow/deny policy
 * before execution. Destructive actions require explicit confirmation.
 */

import readline from "readline";

const POLICY = {
  // Auto-allow
  FILE_WRITE: { autoAllow: true, paths: ["reports/", "audit-logs/"] },
  EXA_SEARCH: { autoAllow: true },
  CLAUDE_API: { autoAllow: true },

  // Require confirmation
  FILE_DELETE: { autoAllow: false },
  NETWORK_EXTERNAL: { autoAllow: false },
};

export class PermissionGate {
  async check(action, context = {}) {
    const policy = POLICY[action];

    if (!policy) {
      console.warn(`  ⚠️  Unknown action "${action}" — blocking by default.`);
      throw new Error(`Permission denied: unknown action "${action}"`);
    }

    if (policy.autoAllow) {
      return true; // silently allowed
    }

    // Require human confirmation for non-auto-allow actions
    return this._askHuman(action, context);
  }

  async _askHuman(action, context) {
    return new Promise((resolve, reject) => {
      const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
      console.log(`\n  🔐  Permission required`);
      console.log(`  Action: ${action}`);
      console.log(`  Context: ${JSON.stringify(context)}`);
      rl.question("  Allow? (y/n): ", (ans) => {
        rl.close();
        if (ans.trim().toLowerCase() === "y") {
          resolve(true);
        } else {
          reject(new Error(`Permission denied by user for action: ${action}`));
        }
      });
    });
  }
}
