/**
 * ContextManager
 * Shared in-memory scratchpad for all sub-agents.
 * Handles get/set with optional summarisation for context-window management.
 */

export class ContextManager {
  constructor() {
    this._store = {};
  }

  set(key, value) {
    this._store[key] = value;
  }

  get(key) {
    return this._store[key];
  }

  getAll() {
    return { ...this._store };
  }

  /**
   * Returns a token-safe summary of a value for inclusion in prompts.
   * Truncates large objects to avoid context overflow.
   */
  summarise(key, maxChars = 3000) {
    const val = this._store[key];
    if (!val) return "";
    const str = typeof val === "string" ? val : JSON.stringify(val);
    return str.length > maxChars ? str.substring(0, maxChars) + "...[truncated]" : str;
  }
}
