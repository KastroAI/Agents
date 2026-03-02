# Changelog

## 0.2.0 — Unreleased

### Changed
- Migrated to `src/` package layout.
- Cleaned up dependencies: removed unused `chromadb` and `PyYAML`, added `pinecone-client`.
- Added optional dependency groups: `gmail`, `dev`.

### Added
- `.env.example` template.
- Unit tests for memory, telegram, and pinecone modules.
- GitHub Actions CI (lint + test).
- `ruff` linter/formatter configuration.
- `py.typed` markers for PEP 561 compliance.

### Removed
- `FILE_BREAKDOWN.md` (auto-generated, superseded by README).

## 0.1.0 — 2026-02-01

Initial release with `agent_tools` and `comms` packages.
