---
name: leancode-flutter
description: Index of LeanCode's free Flutter glossary (84 topics) and blog (108 articles) with live links - routing, platform integrations (maps, BLE, camera, payments, push), storage, Firebase, release to stores, add-to-app, migration to Flutter (from Xamarin/React Native/native), enterprise and banking apps, design systems, Patrol, accessibility, localization. Use when a Flutter question needs real-world experience or a topic not covered by the flutter-architecture, flutter-state-management, flutter-testing, flutter-performance or flutter-dart-style skills.
---

# LeanCode Flutter knowledge (live links)

For architecture, state management, testing, performance and Dart style, use those skills first. They're verified against current official docs. Use this skill for everything else, or when you want LeanCode's real-project experience.

1. **Search, don't read**: grep the index for the topic, e.g. `grep -i "bluetooth\|ble" references/*.md`.
   - `references/glossary.md`: short topic explainers (what it is, when to use, best practices, common mistakes)
   - `references/blog.md`: in-depth articles, case studies, talks
2. Open only the 1-2 best matches. If a local copy exists (`leancode/<section>/<slug>.md`, created by `scrape.py`), read that. Otherwise fetch the URL with WebFetch, and ask for just what you need (e.g. "extract best practices and common mistakes"). Don't request the whole page.
3. **Check freshness before recommending packages or APIs.** Some articles date back to 2019. Known-outdated advice includes Isar/Hive (use drift or hive_ce), Riverpod 2 APIs, "always use Riverpod codegen", and Patrol `$.native` (now `$.platform`). Cross-check against `generated/package-versions.md` or pub.dev.
4. Cite the URL you used.

Content © LeanCode (leancode.co). This skill ships only titles, links and one-line descriptions.
