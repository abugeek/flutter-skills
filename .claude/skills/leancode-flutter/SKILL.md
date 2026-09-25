---
name: leancode-flutter
description: Flutter reference knowledge from LeanCode - glossary of 84 Flutter topics plus 108 in-depth blog articles (architecture, state management/BLoC, routing, testing/Patrol, performance, CI/CD, native interop, accessibility, migration to Flutter). Use when writing, reviewing, or designing Flutter/Dart code, or when choosing a Flutter package or approach.
---

Knowledge base lives in `leancode/` next to this repo's `scrape.py`.

For these topics, prefer the distilled skills first. They hold the key rules, verified against current official docs: `flutter-architecture`, `flutter-state-management`, `flutter-testing`, `flutter-performance`, `flutter-dart-style`.

**LeanCode articles date from 2019-2026, and some are outdated** (e.g. Hive/Isar advice, Riverpod 2 APIs, "always use Riverpod codegen", `$.native` in Patrol). Check the `published`/`source` date and cross-check package advice against `sources/packages.json` (pub.dev versions) or the official docs in `sources/` before recommending it. Use this skill for everything else (routing, platform integrations, storage, release, Firebase, migration, etc.) or when you need the full source article.

1. Grep or read the indexes (one line per page): `leancode/glossary/INDEX.md` for short definitions and best practices, `leancode/blog/INDEX.md` for deep dives and real-world experience.
2. Open only the matching `<slug>.md` files. Frontmatter has `related:` glossary slugs to follow, and `videos:` links for talks.
3. Blog posts are long; grep for the relevant `## ` heading and read that section instead of the whole file.
4. When advising, prefer "Best practices" / "Common mistakes" sections and cite the `source:` URL.

Do not read whole folders. Content © LeanCode (leancode.co).
