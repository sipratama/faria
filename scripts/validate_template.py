#!/usr/bin/env python3
"""Basic structural validator for Annotasi Template and initialized projects."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TEMPLATE_FILES = [
    "README.md",
    "README.en.md",
    "AGENTS.md",
    "CLAUDE.md",
    "docs/PROJECT_INITIALIZATION.md",
    "docs/00_product/PRODUCT_BRIEF.md",
    "docs/00_product/PRD.md",
    "docs/00_product/ROADMAP.md",
    "docs/01_features/FEATURE_TEMPLATE.md",
    "docs/02_architecture/SYSTEM_ARCHITECTURE.md",
    "docs/02_architecture/DATA_MODEL.md",
    "docs/02_architecture/NON_FUNCTIONAL_REQUIREMENTS.md",
    "docs/02_architecture/adr/ADR_TEMPLATE.md",
    "docs/03_design/UX_FLOWS.md",
    "docs/03_design/DESIGN_SYSTEM.md",
    "docs/04_engineering/TEST_STRATEGY.md",
    "docs/04_engineering/THREAT_MODEL.md",
    "docs/05_operations/DEVELOPER_SETUP.md",
    "docs/05_operations/CONFIGURATION.md",
    "docs/05_operations/DEPLOYMENT.md",
    "docs/05_operations/RUNBOOK.md",
    "docs/06_delivery/RISKS.md",
    "docs/06_delivery/RELEASE_CHECKLIST.md",
    "docs/06_delivery/KNOWN_LIMITATIONS.md",
]

REQUIRED_TEMPLATE_FILES += [
    f"docs/standards/{name}"
    for name in [
        "00_STANDARD_INDEX.md",
        "01_ENGINEERING_WORKFLOW.md",
        "02_CODE_QUALITY.md",
        "03_ARCHITECTURE.md",
        "04_BACKEND_STANDARD.md",
        "05_FRONTEND_STANDARD.md",
        "06_API_INTEGRATION_STANDARD.md",
        "07_DATA_PERSISTENCE_STANDARD.md",
        "08_SECURITY_STANDARD.md",
        "09_TESTING_STANDARD.md",
        "10_OBSERVABILITY_RELIABILITY.md",
        "11_PERFORMANCE_STANDARD.md",
        "12_DEPENDENCY_SUPPLY_CHAIN.md",
        "13_CI_CD_RELEASE.md",
        "14_AI_ASSISTED_DEVELOPMENT.md",
    ]
]

PROJECT_SPECIFIC_DOCS = [
    "docs/00_product/PRODUCT_BRIEF.md",
    "docs/00_product/PRD.md",
    "docs/00_product/ROADMAP.md",
    "docs/02_architecture/SYSTEM_ARCHITECTURE.md",
    "docs/02_architecture/DATA_MODEL.md",
    "docs/02_architecture/NON_FUNCTIONAL_REQUIREMENTS.md",
    "docs/03_design/UX_FLOWS.md",
    "docs/03_design/DESIGN_SYSTEM.md",
    "docs/04_engineering/TEST_STRATEGY.md",
    "docs/04_engineering/THREAT_MODEL.md",
    "docs/05_operations/DEVELOPER_SETUP.md",
    "docs/05_operations/CONFIGURATION.md",
    "docs/05_operations/DEPLOYMENT.md",
    "docs/05_operations/RUNBOOK.md",
    "docs/06_delivery/RISKS.md",
    "docs/06_delivery/RELEASE_CHECKLIST.md",
    "docs/06_delivery/KNOWN_LIMITATIONS.md",
]

CORE_PROJECT_PLACEHOLDERS = [
    "<PROJECT_NAME>",
    "<OWNER>",
    "<AUTHOR>",
    "<YYYY-MM-DD>",
]

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCED_CODE_BLOCK_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def remove_fenced_code_blocks(text: str) -> str:
    visible_lines = []
    fence_char = None
    fence_length = 0

    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")

        if fence_char is not None:
            if re.fullmatch(
                rf" {{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ \t]*",
                content,
            ):
                fence_char = None
                fence_length = 0
            continue

        match = FENCED_CODE_BLOCK_RE.match(content)
        if match:
            marker, info = match.groups()
            if marker[0] == "`" and "`" in info:
                visible_lines.append(line)
                continue
            fence_char = marker[0]
            fence_length = len(marker)
            continue

        visible_lines.append(line)

    return "".join(visible_lines)


def check_structure() -> list[str]:
    errors = []
    for rel in REQUIRED_TEMPLATE_FILES:
        if not (ROOT / rel).exists():
            errors.append(f"missing required template file: {rel}")
    return errors


def check_local_markdown_links() -> list[str]:
    errors = []
    for md in ROOT.rglob("*.md"):
        text = remove_fenced_code_blocks(md.read_text(encoding="utf-8"))
        for raw in MARKDOWN_LINK_RE.findall(text):
            target = raw.strip().split()[0].strip("<>")
            if (
                not target
                or target.startswith(("http://", "https://", "mailto:", "#"))
            ):
                continue

            target = unquote(target.split("#", 1)[0])
            if not target:
                continue

            resolved = (md.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(
                    f"{md.relative_to(ROOT)}: link escapes repository: {raw}"
                )
                continue

            if not resolved.exists():
                errors.append(
                    f"{md.relative_to(ROOT)}: broken local link: {raw}"
                )
    return errors


def check_project_placeholders() -> list[str]:
    errors = []
    for rel in PROJECT_SPECIFIC_DOCS:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for placeholder in CORE_PROJECT_PLACEHOLDERS:
            if placeholder in text:
                errors.append(
                    f"{rel}: unresolved project metadata placeholder {placeholder}"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-mode",
        action="store_true",
        help="also report unresolved core metadata placeholders in active project docs",
    )
    args = parser.parse_args()

    errors = []
    if not args.project_mode:
        errors.extend(check_structure())

    errors.extend(check_local_markdown_links())

    if args.project_mode:
        errors.extend(check_project_placeholders())

    if errors:
        print("Validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    mode = "project" if args.project_mode else "template"
    print(f"Validation passed ({mode} mode).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
