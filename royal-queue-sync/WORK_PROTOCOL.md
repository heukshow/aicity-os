# Work Result Return Protocol

Purpose: eliminate user copy/paste between ChatGPT Work mode and the main prince/orchestrator chat.

## Mandatory rule
Every Work handoff for this project must publish its final result to the shared result channel before finishing.

1. Write a structured result JSON into the local royal-queue `shared_queue/done`, `failed`, or `waiting_human` folder using the same UUID as the task whenever one exists.
2. Ensure the GitHub bridge syncs that result to the `royal-queue` branch under `royal-queue-sync/{done,failed,waiting_human}/`.
3. Update `royal-queue-sync/status/latest.json` through the existing bridge/index flow.
4. Do not require the user to copy the Work response back into the main chat.
5. The prince/orchestrator will read `status/latest.json` and then the individual result JSON directly via the GitHub connector.
6. If local result publication fails, report that as the actual blocker and retry automatically when safe. Do not silently fall back to asking the user for copy/paste.
7. Only request user action for CAPTCHA, payment approval, legal consent, forced human verification, or unavoidable product UI acceptance required to enter Work mode.

## Completion definition
A Work task is not considered fully returned until its result exists in the GitHub `royal-queue` result path and is readable by the prince/orchestrator.
