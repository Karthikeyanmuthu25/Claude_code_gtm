# Agent rules for this repository

## The full pipeline must run non-interactively, start to finish

Once the user provides input, the agent must run the ENTIRE workflow
automatically — no follow-up questions, no Yes/No confirmations, no
pauses mid-run. The only interaction the user should ever need is editing
the input file/context beforehand.

This is implemented as the `run` subcommand:

```bash
cd market_discovery_agent
python agent.py run --input input_template.json --session my-session
```

`cmd_run` in `agent.py` reads a single JSON input file (see
`market_discovery_agent/input_template.json` for the schema) and chains
through every phase — init, discover, plan, all 7 secondary-research
agents, synthesize, icp, market-sizing, target-accounts,
customer-discovery, validate (if interview notes were supplied),
gtm — calling each phase's existing `cmd_*` handler directly. It ends
with exactly one message:

> The agent has completed the run. The outputs have been generated and
> saved to the respective folder. Please review the results.

**Rule for future changes:** any new phase or agent added to this
pipeline must NOT introduce a hard-blocking `input()` call with no
bypass. If a phase needs new human-provided data, add it as an optional
field to `input_template.json` and thread it through as a pre-supplied
argument — the same pattern `cmd_init` (`founder_input`), `cmd_competitor`
(`competitors`), and `cmd_validate` (`interviews`) already use to accept
data programmatically instead of prompting. `cmd_run` must keep working
unattended after any such change.

The one legitimate exception is Validation (Phase 6): it's skipped, not
faked, when the input supplies no real interview notes — there's no way
to validate against customer interviews that haven't happened yet. GTM
(Phase 7) still runs regardless; it already scopes itself down to a
validation-first motion when Phase 6 hasn't run (see `gtm.py`), so running
it unconditionally is correct.

The step-by-step interactive commands (`init`, `competitor`, `validate`,
etc.) still exist and still prompt when run directly — `run` is an
additional, non-interactive entrypoint layered on top of them, not a
replacement.
