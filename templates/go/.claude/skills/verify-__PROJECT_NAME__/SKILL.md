---
name: verify-__PROJECT_NAME__
description: Drives the __APP_NAME__ HTTP service the way a client does, and keeps each request and response as evidence. Use it to show that a change works in the running service, to reproduce a bug before fixing it, and wherever a pstack playbook proves a change in the running app.
---

# Verify __APP_NAME__

`scripts/app` in this directory starts a disposable instance of the service, checks it, records every request and response, and stops it. Run it from the repository root. Each run gets its own id, port, and data directory under `.verify/<run>/`, so runs never share state. Git ignores `.verify/`.

```bash
app=.claude/skills/verify-__PROJECT_NAME__/scripts/app
```

## Launch

```bash
run=$($app start)
```

`start` builds `./cmd/server`, picks a free port, starts the server on an empty data directory, and returns the run id once the port answers. The instance is usable when `start` returns. If the port does not answer within 30 seconds, `start` prints the server log, cleans up, and exits with code 1.

## Doctor

```bash
$app doctor "$run"
```

Run it first whenever anything looks off. It prints `ok` with the URL, the process id, and the data directory when the process that this run started is alive and its port answers. Otherwise it prints `FAIL` with the reason and the log path. Drive only an instance that `doctor` reports as `ok`.

## Drive

```bash
$app call "$run" <name> <METHOD> <path> ['<json body>']
```

`call` sends one request to the run's instance and prints the request, the response body, and `< status <code>`. `features/README.md` lists what the service does, and each feature file gives the exact calls and the result that proves the feature works.

## Evidence

Every `call` saves its output as `.verify/<run>/evidence/<name>.txt`. A proof shows the action and the resulting state, so after a write, read the value back with a second call. Cite the evidence files in the reply or the pull request.

## Cleanup

```bash
$app stop "$run"
```

`stop` stops only the process that this run started, and deletes the run's data directory and binary. The evidence stays in `.verify/<run>/evidence/`.

## Helpers

- `$app start` starts an instance and prints its run id.
- `$app doctor <run>` checks the run's instance.
- `$app call <run> <name> <METHOD> <path> [body]` sends one request and saves it as evidence.
- `$app stop <run>` stops the instance and keeps the evidence.
- `$app --help` prints this list.
