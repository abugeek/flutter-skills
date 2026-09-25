# Roadmap

Status 2026-09-25: 6 skills done and eval'd (round 2: 33/33 with skill vs 71% without). Snippets compile (`checks/`).

## Done: automation (2026-09-25)
`update.py` (fetch → diff → generate → stale scan → checks → UPDATE_REPORT.md), `grade.py` + `evals/checks.json` (regex grading, matches hand grading 11/12), generated migrations table (53 entries), versions table, skills index.

## Next batch (planned for a fresh session / new usage window)
Revised budget with automation: **~400-600k tokens total** (was 1.3-2.1M). Rules: write only what the model gets wrong (check baseline failures), generate tables by script, grade by regex, re-run with-skill only.

| # | Task | Sources (free, fetch via script) | Output |
|---|---|---|---|
| 1 | Deprecated Flutter APIs → replacements | ✅ table generated: `generated/flutter-breaking-changes.md` | small `flutter-migrations` SKILL.md (~40 lines) pointing to it + `dart fix` workflow |
| 2 | Latest Flutter capabilities (3.38–3.47) | `release/whats-new`, release blog posts, `tools/widget-previewer`, `platform-integration/web/wasm`, SwiftPM, Kotlin built-in | fold into `flutter-migrations` ("use this now") |
| 3 | On-device databases | Flutter `app-architecture/design-patterns/offline-first`, drift docs (simolus3/drift), sqflite, hive_ce, shared_preferences async API, flutter_secure_storage | `flutter-local-data` skill (choose DB, schema migrations, reactive queries, isolates, testing with in-memory DB) + compile check |
| 4 | Custom lints | dart.dev `tools/analyzer-plugins`, `analysis_server_plugin`, `tools/analysis`, leancode_lint / riverpod_lint as examples | `flutter-custom-lints` skill + a working example plugin in `checks/` |
| 5 | Clean code / folder structure fine-tune | Effective Dart design (already in `sources/dart`), VGV code_style, existing skills | tighten `flutter-dart-style` + `flutter-architecture` |
| 6 | Discoverability | — | `flutter-skills-index` (router listing every skill + when to use), sharper descriptions, cross-links, trigger eval (small: ~10 queries/skill, 1 run) |
| 7 | Evals | reuse `skills-workspace` pattern | 1–2 evals per new skill, with-skill vs baseline, Sonnet |

## Token budget notes
- Start a **fresh session** (read this file + skills list) — continuing a long session re-sends its whole context on every tool call.
- Research content is condensed by script before reading; only "what changed" is read in full.
- Full automated description optimization (`run_loop`, ~20 queries × 3 runs × 5 iterations × 7 skills) is the most expensive item — use the small manual trigger eval instead unless triggering is visibly bad.
