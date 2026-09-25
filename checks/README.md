# Skill snippet checks

Compiles the code examples used in `.claude/skills/*` against the current SDK and packages.
Run after upgrading Flutter/Dart or bumping package versions; a failure means a skill teaches outdated code.

```sh
(cd checks/dart && dart pub get && dart analyze)
(cd checks/flutter && flutter pub get && dart analyze && flutter test)
```
Covers: Dart 3.13 syntax (primary constructors, dot shorthands, null-aware elements, patterns), Riverpod 3 notifier + mutation + ProviderContainer.test, Cubit + Page/View + blocTest, Flutter Command/Result MVVM, Alchemist config, Widget Previews, Patrol `$.platform`.

Last verified: 2026-09-25, Flutter 3.47.4 / Dart 3.13.3, flutter_riverpod 3.4.3, flutter_bloc 9.1.1, bloc_test 10.0.0, alchemist 0.14.0, patrol 4.10.0.
Known conflict: alchemist 0.14 requires equatable ^2 (equatable is pinned to 2.x here).
