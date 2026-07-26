# Agent Operating Rules — B2B Due Diligence Agent

## Autonomous execution — no mid-task confirmations

Once the user provides input (a company/decision-maker record, a file, a JSON blob, or a request to run/fix/test something), execute the full workflow end-to-end without pausing to ask follow-up questions or yes/no confirmations (e.g. "Want me to run it?", "Should I proceed?", "Do you want me to continue?").

The only interaction expected from the user is updating the input or context if needed — not approving each step.

After execution:
1. Generate all outputs.
2. Save them to the appropriate files/folders (e.g. `reports/` for pipeline runs).
3. Notify the user with a single completion message, for example:

   > "The agent has completed the run. The outputs have been generated and saved to the respective folder. Please review the results."

No additional prompts or confirmations should interrupt execution once input has been given.

This does not override the standing safety rules for genuinely destructive or irreversible actions (force-push, `git reset --hard`, deleting uncommitted work, etc.) — those still warrant a check-in. It applies to routine execution: running the pipeline, running tests, applying fixes, verifying changes.
