#!/usr/bin/env python3
"""Creates projects from the kit, and adds the kit to existing projects.

  python3 tools/new.py init swift|go|typescript DEST [--name AppName] [--module example.com/app] [--owner @you]
  python3 tools/new.py adopt swift|go|typescript PROJECT [--owner @you]

Run it from the kit. Inside a project, agents add slices, use cases, and ports
by copying the reference slice that AGENTS.md names.

Needs Python 3.9 or later and nothing else.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

LANGUAGES = ("swift", "go", "typescript")
PASCAL = re.compile(r"^[A-Z][A-Za-z0-9]*$")


def fail(message):
    print(f"new.py: {message}", file=sys.stderr)
    sys.exit(1)


def separated(name, separator):
    return re.sub(r"(?<!^)(?=[A-Z])", separator, name).lower()


def fill(text, values):
    for key in sorted(values, key=len, reverse=True):
        text = text.replace(key, values[key])
    return text


# ----------------------------------------------------------- init, adopt

# Compiler, linter, and test runner settings. An agent could weaken a check by
# changing them, so they are gate files too. tools/gatecheck.py judges package.json.
TOOL_CONFIG_PATHS = {
    "swift": ["/.swiftlint.yml"],
    "go": ["/.golangci.yml", "/.golangci.yaml"],
    "typescript": ["/tsconfig*.json", "/.oxlintrc.json", "/oxlint.config.*", "/eslint.config.*", "/vitest.config.*", "/pnpm-workspace.yaml", "/.npmrc"],
}


def kit_root():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isdir(os.path.join(root, "templates")):
        fail("init and adopt run from the kit, which has a templates/ directory next to tools/")
    return root


def copy_tree(source, dest, values, overwrite, report):
    for directory, _, files in os.walk(source):
        for file in files:
            if file == ".DS_Store":
                continue
            rel = os.path.relpath(os.path.join(directory, file), source)
            target = os.path.join(dest, fill(rel, values))
            if os.path.exists(target) and not overwrite:
                report.append(f"kept existing {os.path.relpath(target, dest)}")
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(os.path.join(directory, file), encoding="utf-8") as f:
                text = f.read()
            with open(target, "w", encoding="utf-8") as f:
                f.write(fill(text, values))
            shutil.copymode(os.path.join(directory, file), target)


def copy_kit_files(kit, dest, language, values, overwrite, report):
    copy_tree(os.path.join(kit, "templates", "common"), dest, values, overwrite, report)
    os.makedirs(os.path.join(dest, "tools"), exist_ok=True)
    for tool in ("archcheck.py", "gatecheck.py", "agent-stop-check.sh"):
        target = os.path.join(dest, "tools", tool)
        shutil.copy2(os.path.join(kit, "tools", tool), target)
        os.chmod(target, 0o755)
    os.makedirs(os.path.join(dest, "docs", "architecture"), exist_ok=True)
    shutil.copy2(os.path.join(kit, "docs", "ARCHITECTURE.md"), os.path.join(dest, "docs", "ARCHITECTURE.md"))
    shutil.copy2(os.path.join(kit, "docs", "architecture", f"{language}.md"),
                 os.path.join(dest, "docs", "architecture", f"{language}.md"))


def placeholder_values(language, args):
    return {
        "__LANGUAGE__": language,
        "__OWNER__": args.owner,
        "__TOOL_CONFIG_LINES__": "\n".join(f"{path:<30}{args.owner}" for path in TOOL_CONFIG_PATHS[language]),
        "__APP_NAME__": args.name,
        "__PROJECT_NAME__": separated(args.name, "-"),
        "__GO_MODULE__": args.module or f"example.com/{args.name.lower()}",
    }


def init(args):
    kit = kit_root()
    dest = os.path.abspath(args.dest)
    # An empty clone holds only .git, so .git does not count as content.
    if os.path.exists(dest) and [entry for entry in os.listdir(dest) if entry != ".git"]:
        fail(f"{dest} is not empty. Use `adopt` for an existing project.")
    if not PASCAL.match(args.name):
        fail("--name must be a type-style name such as ExpenseTracker")
    values = placeholder_values(args.language, args)
    report = []
    copy_tree(os.path.join(kit, "templates", args.language), dest, values, True, report)
    copy_kit_files(kit, dest, args.language, values, True, report)
    with open(os.path.join(dest, "architecture-baseline.json"), "w", encoding="utf-8") as f:
        f.write("{}\n")
    subprocess.run([sys.executable, "tools/archcheck.py", "--module-map", "docs/architecture/modules.md"], cwd=dest, check=False)
    print(f"Created a {args.language} project in {dest}.\n\nNext:")
    steps = {
        "swift": [
            f"Create an iOS app project named {args.name} in Xcode, saved in {dest}.",
            f"Delete the Swift files Xcode generated, and add App/{args.name}App.swift to the app target.",
            "Add Packages/AppModules as a local package, and link the AppComposition product to the app target.",
        ],
        "go": ["Run `go mod tidy` if you add dependencies."],
        "typescript": [],
    }[args.language]
    steps.append("Describe what the project does in README.md.")
    steps.append("Run ./check.")
    if args.owner == "@OWNER":
        steps.append("Replace @OWNER in .github/CODEOWNERS and .github/workflows/gates.yml with your GitHub user.")
    steps.append("Commit, and set up the ruleset on main that \"Let agents merge\" in the kit's README describes.")
    steps.append("Once your first real slice follows the patterns of the Notes slice, delete Notes and name the new slice as the reference in AGENTS.md.")
    for step in steps:
        print(f"  - {step}")


def adopt(args):
    kit = kit_root()
    dest = os.path.abspath(args.dest)
    if not os.path.isdir(dest):
        fail(f"{dest} does not exist")
    args.name = args.name or "App"
    values = placeholder_values(args.language, args)
    if args.language == "go" and os.path.exists(os.path.join(dest, "go.mod")):
        with open(os.path.join(dest, "go.mod"), encoding="utf-8") as f:
            values["__GO_MODULE__"] = next((l.split()[1] for l in f if l.startswith("module ")), values["__GO_MODULE__"])
    report = []
    copy_kit_files(kit, dest, args.language, values, False, report)
    language_dir = os.path.join(kit, "templates", args.language)
    for rel in ("architecture.json", ".claude/rules/architecture.md", "docs/architecture/stack.md", ".oxlintrc.json"):
        if not os.path.exists(os.path.join(language_dir, rel)):
            continue
        target = os.path.join(dest, rel)
        if os.path.exists(target):
            report.append(f"kept existing {rel}")
            continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(os.path.join(language_dir, rel), encoding="utf-8") as f:
            text = fill(f.read(), values)
        with open(target, "w", encoding="utf-8") as f:
            f.write(text)
    check_target = "check" if not os.path.exists(os.path.join(dest, "check")) else "check.kit"
    shutil.copy2(os.path.join(language_dir, "check"), os.path.join(dest, check_target))
    for line in report:
        print(line)
    print(f"\nAdded the architecture kit to {dest}.\n\nNext:")
    for step in [
        "Edit the modules in architecture.json so that every source directory maps to a kind.",
        "Run `python3 tools/archcheck.py` until no file is reported as unmapped.",
        "Run `python3 tools/archcheck.py --write-baseline` to accept the existing violations.",
        "Describe the project's libraries in docs/architecture/stack.md, and allow them per kind in architecture.json.",
    ] + ([
        "Add the devDependencies oxlint and oxlint-tsgolint at the versions in the kit's templates/typescript/package.json, "
        "edit the paths in .oxlintrc.json to match the project, and fix what `npx oxlint` reports.",
    ] if args.language == "typescript" else []) + [
        f"Wire {check_target} into your build and CI, and adjust its build and test commands to this project.",
        "If CLAUDE.md already existed, add the line `@AGENTS.md` at its top.",
        "Name a reference slice in AGENTS.md: the existing slice that best follows docs/ARCHITECTURE.md, or one you rebuild in that shape.",
        "Fill in GLOSSARY.md, then follow the adoption steps in the kit's README.",
    ]:
        print(f"  - {step}")


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    p = commands.add_parser("init", help="create a project from the kit")
    p.add_argument("language", choices=LANGUAGES)
    p.add_argument("dest")
    p.add_argument("--name", default="App", help="app or service name, such as ExpenseTracker")
    p.add_argument("--module", help="Go module path, such as github.com/you/app")
    p.add_argument("--owner", default="@OWNER", help="code owner for gate files, such as @you")

    p = commands.add_parser("adopt", help="add the kit to an existing project")
    p.add_argument("language", choices=LANGUAGES)
    p.add_argument("dest")
    p.add_argument("--name")
    p.add_argument("--module")
    p.add_argument("--owner", default="@OWNER")

    args = parser.parse_args()
    if args.command == "init":
        return init(args)
    return adopt(args)


if __name__ == "__main__":
    main()
