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
7. Test the use case with stubs of its ports. Give the stubs each result the ports can return, and check which port methods the use case calls and with which arguments.
8. Decide in the wiring file which middleware this slice receives, and extend the composition test if the choice matters.
9. Run `./check` after each step, and finish when it passes.
