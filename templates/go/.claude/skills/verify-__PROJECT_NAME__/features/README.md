# __APP_NAME__ verification map

This directory lists what the service does for its clients, and how to prove that each feature works. Read it before you drive the service, then follow the matching feature file. `$app` is `.claude/skills/verify-__PROJECT_NAME__/scripts/app`, run from the repository root.

## Baseline preconditions

- Start a run with `run=$($app start)`. Its data directory starts empty.
- Run `$app doctor "$run"` and require `ok`.
- Never drive an instance that this run did not start.

## Driving conventions

- Start every recipe from the baseline state unless its preconditions say otherwise.
- Send every request with `$app call`, so that it is saved as evidence.
- Treat every command as literal. Keep quoted names and bodies unchanged.

## Proof and skip reporting

- Capture the request and the resulting state, not only the response to a write.
- The proof of a write includes a second request that reads the stored value back.
- Name the evidence file of each step in the report.
- Report an unreachable path with the attempted command and the unmet precondition.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph that describes what a client can do. It then has four H2 sections in this order: `Sub-features`, `How to get to it (user POV)`, `Driving it with scripts/app`, and `Gotchas`.

## Features

- [Create a note](./create-note.md) covers creating a note, and the errors for an empty and a too-long title.
- [List notes](./list-notes.md) covers listing notes, newest first.

When a change adds or changes what clients can do, change the feature files in the same pull request. When the Notes slice goes, its feature files go too.
