# CLAUDE.md

## Execution mode: fully autonomous, no mid-run confirmations

Once the user provides the input, the agent should run automatically from start to finish
without asking any follow-up questions, including Yes/No confirmations.

The only interaction from the user should be updating the input or context if needed. After
receiving the input, the agent should execute the entire workflow, generate all outputs, save
them to the respective files/folders, and then notify the user with a message such as:

"The agent has completed the run. The outputs have been generated and saved to the respective
folder. Please review the results."

No additional prompts or confirmations should interrupt the execution.
