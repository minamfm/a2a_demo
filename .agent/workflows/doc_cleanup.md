---
description: Audit and clean up project documentation — remove stale files, consolidate scattered docs, maintain doc hygiene
---

# Documentation Cleanup

## 1. Inventory
// turbo
List all `.md` files in project:
```bash
find . -name "*.md" -not -path "./.git/*" | sort
```

For each file note: last modified date, size, content summary.

## 2. Classify

Mark each document as:
- **Active** — Currently referenced, maintained, still accurate
- **Stale** — Outdated but contains useful historical content
- **Orphan** — One-off logs, superseded plans, resolved bug notes, AI-generated reports

## 3. Present to User

Show the classification table and ask for confirmation before proceeding.

## 4. Consolidate

Merge useful content from Stale docs into `docs/architecture/` documents.
Extract relevant decisions into ADRs in `docs/architecture/SYSTEM_ARCHITECTURE.md`.

## 5. Archive or Delete

Move Orphan docs to `docs/.archive/` or delete. **Always ask before deleting.**

## 6. Verify Links

Check all remaining docs for broken internal references.

## 7. Report

Show cleanup summary: files kept, consolidated, removed, total size reduction.

## Orphan Detection Patterns

- `*_SUMMARY.md`, `*_REVIEW.md`, `*_STATUS.md` describing completed work
- Multiple versions (`*_V1.md`, `*_V2.md`) — keep only latest
- AI-generated implementation logs
- Review cycles (`*_REVIEW_CYCLE2.md`)

## Safety Rules

Never auto-delete: `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`, or any file in `docs/architecture/`
