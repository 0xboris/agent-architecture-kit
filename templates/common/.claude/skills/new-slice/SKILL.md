---
name: new-slice
description: Creates a feature slice in the shape of the reference slice that AGENTS.md names. Use when a task adds a new capability, such as a new screen group, a group of endpoints, or a background job with its settings.
---

1. Pick the slice name from `GLOSSARY.md`. Add the concept to the glossary if it is new.
2. Read the reference slice that `AGENTS.md` names, and the slice layout in `docs/architecture/<language>.md`.
3. Create the slice's files by copying the reference slice's structure:
   - the use case module, with one use case and its test
   - the UI module, with its entry points and their test
   - the wiring file in the composition root, and the call to it from the container
   - in Swift, the targets and their dependencies in `Package.swift`
4. Put every business decision in a domain rule and call it from the use case. Use cases only orchestrate.
5. When the use case needs something from outside the process, follow the new-port skill.
6. When another slice needs the same rule or type, move it into the domain. Slices never import each other, and use cases are never shared.
7. Test the use case against the real adapters that run locally, as the reference slice does, and assert what reads back. Use the test support's failing store or fakes only for errors and for time, ids, and remote services.
8. Decide in the wiring file which middleware this slice receives, and extend the composition test if the choice matters.
9. In a repository with several apps, create the slice under the same name in each app that needs it. Start with the API: its routes, then the regenerated contract. Then build each client's slice on the regenerated client. Rules that both apps need go into the shared domain.
10. When a page shows the slice's UI, add it to a screen. When the slice's UI needs something from another slice, such as a name for an id, take it as a parameter or a slot, and let the screen fill it.
11. Add the slice's entries to the feature map of the verification skill in `.claude/skills/verify-*/`, in the shape of the Notes feature files. Keep them in the slice's pull request. The skill and the wiring file are gate files, so the owner reviews that pull request.
12. Run `./check` after each step. Finish when it passes and the verification skill shows each new entry point working, with the evidence named in your report.
