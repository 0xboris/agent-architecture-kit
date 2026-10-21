# pstack in Claude Code

pstack skills use Cursor names. In Claude Code, read this file once per session, then map each Cursor name in a skill with the tables below. `<pstack>` means the folder that holds `skills/` and `docs/`. If a Cursor field has no row, drop it and say so. Never pass a field or value the tool schema rejects.

## Tools

| Cursor | Claude Code |
| --- | --- |
| `Task` | `Agent` |
| `AskQuestion` | `AskUserQuestion`. In `-p` mode it is absent, so ask in plain text. |
| Open a todolist | Use `TodoWrite` if the session offers it. Otherwise keep the list in your reply and update it at each phase. |
| Run another pstack skill (`/name` or "the **name** skill") | `Read` `<pstack>/skills/<name>/SKILL.md` and follow it. The `Skill` tool refuses most pstack skills. When you tell the user to type it, write `/pstack:<name>`. |
| `Grep`, `Glob` | `Bash` with `rg` when the session has no `Grep` or `Glob`. |

## Subagent fields

| Cursor | Claude Code |
| --- | --- |
| `subagent_type: generalPurpose` | `subagent_type: "general-purpose"` |
| `poteto-agent`, `comment-sicko` | `pstack:poteto-agent`, `pstack:comment-sicko` |
| `readonly: true` | `subagent_type: "Explore"`. It keeps `Bash`, so the brief also says "do not edit files", and you check `git status` afterward. |
| `readonly: false` | `general-purpose`. It keeps the session's MCP servers. |
| `environment: "cloud"` | `isolation: "worktree"`. Name the branch or commit the worker checks out. |
| `environment: "local"` | Omit. |
| `cloud_base_branch: <b>` | Tell the worker to check out `<b>` first. |
| `run_in_background: true` | Omit. Subagents run in the background by default and notify you when they finish. |
| `resume` | Spawn a new agent and paste the earlier result into its brief. |
| `file_attachments` | List the paths in the brief. |

## Models

| Cursor | Claude Code |
| --- | --- |
| `claude-<family>-<version>-<effort>[-fast]`, such as `claude-opus-5-5-xhigh` | `model: "opus"` and `effort: "xhigh"`. `model` takes only `opus`, `sonnet`, `haiku`, `fable`. Drop `-fast`. |
| A `grok-*`, `gpt-*`, or other non-Claude slug | Omit `model` so the agent runs on the session model, and say so. |
| `auto` or `inherit-parent` | Omit `model`. |
| The `pstack-models.mdc` rule, `~/.cursor/rules/pstack-models.mdc` | `~/.claude/rules/pstack-models.md`. Claude Code loads it into every new session, so its role lines are already in context. If they are not, read the file. If the file or the role's line is missing, use the skill's default slug. |
| A role value `<model> <effort>`, such as `opus high` | `model: "opus"` and `effort: "high"`. |

## setup-pstack

Claude Code loads every `.md` file in `~/.claude/rules/` into each new session, so `setup-pstack` writes its rule there. Follow its steps with these changes:

- Detect. The detected models are the `model` values that the `Agent` tool schema lists, each with an effort from its `effort` values. Write a real model as `<model> <effort>`, such as `opus xhigh`. The effort is the last token, so the budget step works as written.
- Defaults. Map each default slug with the rows above: `claude-opus-5-5-xhigh` is `opus xhigh`, and `grok-4.7-xhigh-fast` is `inherit-parent`.
- Write. Write `~/.claude/rules/pstack-models.md` with no frontmatter, then the comment lines, the `# budget` line, and one line per role from step 5. Overwrite the whole file. Never put the role lines in `CLAUDE.md` or `AGENTS.md`.

## Paths

| Cursor | Claude Code |
| --- | --- |
| `.cursor/skills/`, `~/.cursor/skills/` | `.claude/skills/`, `~/.claude/skills/` |
| `~/.cursor/plugins/`, `.cursor-plugin/plugin.json` | `~/.claude/plugins/`, `.claude-plugin/plugin.json` |
| `.cursor/rules/*.mdc`, always-applied rules | `CLAUDE.md`, or `AGENTS.md` when no `CLAUDE.md` exists. Claude Code never reads `.mdc` files. The model rule is the exception. See Models. |
| `https://github.com/cursor/plugins/blob/main/pstack/<path>` | `<pstack>/<path>` when that file exists. The plugin ships the skills, `docs/guide/`, and `README.md`. Read the local copy and never fetch it. Give the user the URL when they need a link. |
| Transcripts in `~/.cursor/projects/<slug>/agent-transcripts/` | `~/.claude/projects/<slug>/<session>.jsonl`. The slug is the workspace path with each `/` and `.` changed to `-`, so `/Users/you/proj` is `-Users-you-proj`. The newest `.jsonl` directly in that folder is the current session. Its `<session>/subagents/` folder holds subagent transcripts. Read only this workspace's folder. |

## Cursor-only features

Claude Code has no Cursor Automations, Bugbot, or Cursor cloud agents, and only a cloud session has a built-in PR tool. When a step needs one, put one line in your reply, `Skipped in Claude Code: <step>. <reason>.`, then go on to the next step. Do not stop, ask, or retry. When a later step needs what the skipped step made, such as a URL or a key, leave a placeholder and name it in the line.

| Cursor | Claude Code |
| --- | --- |
| Cursor Automations: routines, `update_state` routine calls, `api2.cursor.sh/automations` webhooks, routine wakes, and `SendToUser` secret requests | Skip with the line. |
| Bugbot | Bugbot comments on a GitHub PR are ordinary review threads, so triage them with the forge command that the step gives. Skip a step that starts, waits for, or configures Bugbot when the PR has no Bugbot check or comment. |
| Cursor cloud agents | `environment: "cloud"` maps to a worktree, as in Subagent fields. Skip a step that needs the cloud agent itself, such as its dashboard status or its own machine. |
| A built-in PR tool | In a cloud session, the GitHub MCP tools, as in GitHub in cloud sessions. Elsewhere, use the forge command that the step gives, such as `gh pr create`. Neither is a skip, so write no line. |

## GitHub in cloud sessions

A Claude Code cloud session blocks GitHub's GraphQL API. Every `gh pr` command fails there, and so does `scripts/watch-pr/watch-pr`, which reads GitHub through `gh pr` and GraphQL. Before the first GitHub step of a session, run `gh api graphql -f query='{viewer{login}}'`. When it fails with "not available from Claude Code sessions", the session is a cloud session, and every GitHub step follows this section. These are substitutes, not skips, so write no skip line.

The GitHub MCP tools (`mcp__github__*`) are the cloud session's built-in PR tool. For anything they do not cover, use `gh api` with a REST path, such as `repos/<owner>/<repo>/pulls/<pr>`. REST works in a cloud session.

| Forge command | In a cloud session |
| --- | --- |
| `gh pr create` | `mcp__github__create_pull_request` with `draft: false`. |
| `gh pr edit <pr> --base <branch>`, and title or body edits | `mcp__github__update_pull_request` with `base`, `title`, or `body`. |
| `gh pr ready <pr>` | `mcp__github__update_pull_request` with `draft: false`. |
| `gh pr view <pr> --json ...` | `mcp__github__pull_request_read` with method `get`. `merged` and `merged_at` say whether it merged, `base.ref` names its base, `head.sha` its head, and `mergeable_state` its merge state. |
| `gh pr list` | `mcp__github__list_pull_requests`, filtered by `head` as `<owner>:<branch>`, `base`, or `state`. Its `merged` field reads `false` even for a merged PR, so read a PR's merge state with method `get`. |
| `gh pr checks <pr>` | `mcp__github__pull_request_read` with method `get_check_runs`, and with method `get_status` for commit statuses. |
| Review threads | `mcp__github__pull_request_read` with method `get_review_comments`. Reply with `mcp__github__add_reply_to_pull_request_comment`, and resolve with `mcp__github__resolve_review_thread` and the thread's id. |
| `gh pr merge <pr> --squash` | `mcp__github__merge_pull_request` with `merge_method: "squash"` and `expectedHeadSha` set to the head that the verdict covers. Read the PR back afterward, as the step says. |
| `gh pr merge <pr> --auto` | `mcp__github__enable_pr_auto_merge`. |
| Re-running a failed CI job | `mcp__github__actions_run_trigger` with method `rerun_failed_jobs`. |
| `orch frontier set` | It reads PRs with `gh pr list`, so it fails. Run the Orchestrate playbook from a session outside the cloud. |

Without the MCP tools, use `gh api` REST paths, and these routes for what REST lacks: `GET repos/<owner>/<repo>/pulls/<pr>/ccr/review_threads`, `POST repos/<owner>/<repo>/pulls/<pr>/ccr/comments/<comment_id>/resolve`, `PUT` or `DELETE repos/<owner>/<repo>/pulls/<pr>/ccr/auto_merge`, and `POST repos/<owner>/<repo>/pulls/<pr>/ccr/ready_for_review`.

### Watching a PR in a cloud session

Where a playbook runs `scripts/watch-pr/watch-pr`, do this instead:

1. Subscribe the session to each PR with `subscribe_pr_activity` from the `claude-code-remote` MCP server. CI results, reviews, comments, and the merge then wake the session as new turns, so the playbook needs no `/loop` and no poll loop. Only the session receives these events, not its subagents. The session that runs the playbook subscribes, and hands each event to the PR's owner.
2. At each wake, and before each decision the playbook makes, read the PR's current state with the table above: the PR, its checks and statuses, and its review threads. Apply the playbook's rules to that state as you would to the watcher's verdict. Ready means `mergeable_state` reads `clean`. `unknown` means GitHub is still computing it, so read it again. A green check list alone is not ready.
3. Some changes wake no session, such as a conflict from a push to the base, another person's push, CI that reports only a commit status, or a lost event. While a PR waits, schedule a check-in about an hour out with `send_later` from the same server, and reread the PR when it fires.
4. For Shipping's queued stack, subscribe to every PR in the stack, and at each wake reread them from the bottom up. The run is complete when the top PR reads merged with trunk as its base.
5. Unsubscribe with `unsubscribe_pr_activity` once the PR merges or closes, or when the operator says to stop.
