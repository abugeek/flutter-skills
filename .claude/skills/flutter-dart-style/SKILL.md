---
name: flutter-dart-style
description: Write modern, concise, idiomatic Dart 3.13 / Flutter 3.47 code - primary constructors, private named parameters, dot shorthands, null-aware elements, patterns and sealed classes, records, extension types, widget-class conventions, const, lints (very_good_analysis/flutter_lints), Effective Dart naming. Use this whenever writing or refactoring any Dart/Flutter code, generating widgets, models or classes, reviewing code style, or when code looks verbose, outdated (pre-Dart-3) or full of `!` and if/else chains - apply it by default to all Flutter code you write.
---

# Modern Dart & Flutter code style

Verified 2026-09-25: **Flutter 3.47.5 / Dart 3.13.4** (stable). Language features depend on the package's SDK constraint. Check `environment: sdk:` in `pubspec.yaml` before using a feature. The minimum language version is noted on each item below.

Goal: **less code, same behavior, and mistakes caught by the compiler instead of at runtime.** Don't write code the SDK, the language, or an existing dependency already provides.

## 1. Classes & models

- **Primary constructors (3.13)** declare fields and constructor in the header:
  ```dart
  class Point(final int x, final int y);                  // immutable fields x, y
  class const Money(final int cents, final String currency); // const primary constructor
  class User({required final String _id, final String? nickname}); // 3.12 private named param: caller passes `id:`
  class Admin(super.name, final Set<String> roles) extends User; // super parameters
  class Temp(final double celsius) { this : assert(celsius > -273.15); } // validation
  ```
  Widgets too (compile-checked):
  ```dart
  class const Greeting({super.key, required final String name}) extends StatelessWidget {
    @override
    Widget build(BuildContext context) => Padding(padding: const .all(16), child: Text('Hi $name'));
  }
  ```
  `var`/`final` in the header creates a field. Without it, the parameter is just a parameter. Since 3.13, `final`/`var` on ordinary function parameters is a compile error.
- **Concise constructors (3.13)** in class bodies: `new(this.x, this.y);`, `new origin() : x = 0, y = 0;`, `factory fromJson(Map<String, Object?> j) => ...;`, `const new();`.
- **Private named parameters (3.12)**: `Point({required this._x})` is called as `Point(x: 1)`.
- Before 3.13, the equivalent is `const Point({required this.x, required this.y}); final int x; final int y;`.
- Immutable by default: `final` fields, `const` constructors, `copyWith` via codegen (freezed/dart_mappable) only when you need it.
- **Sealed hierarchies** for states/results/events. `switch` is exhaustive, so no `default` is needed:
  ```dart
  sealed class Shape {}
  final class Circle(final double r) extends Shape;
  final class Square(final double side) extends Shape;
  double area(Shape s) => switch (s) { Circle(:final r) => 3.14159 * r * r, Square(:final side) => side * side };
  ```
- Class modifiers: `final class` (no subclassing outside the library), `interface class`, `base class`, `sealed class`, `abstract interface class` for pure contracts (repositories).
- **Extension types** give a zero-cost typed wrapper: `extension type UserId(String value) {}`, so you can't pass an `OrderId` where a `UserId` is expected. Also `extension type Json(Map<String, Object?> m) { String get name => m['name'] as String; }`.
- **Records** for small multi-returns. Destructure them immediately: `final (user, token) = await login();` rather than `result.$1`. Use a real class once the value travels across files.

## 2. Null safety & control flow

- `if (x case final v?) use(v);` / `if (json case {'name': String name, 'age': int age}) ...` instead of `x != null` + `x!`.
- Avoid `!` on values you don't control (API data, maps). Handle `null` explicitly.
- `switch` expressions over if/else chains and nested ternaries. Use `when` guards: `.foo2 when data != null => Foo2Widget(data)`.
- **Dot shorthands (3.10)** when the type is inferable: `mainAxisAlignment: .center`, `padding: const .all(16)`, `Status s = .running;`, `case .dark =>`. Don't use them where the context type isn't obvious to a reader.
- Collections, declaratively: `[header, ?maybeBanner, if (isAdmin) adminTile, for (final i in items) Tile(i), ...?extra]`. `?maybeBanner` is a **null-aware element (3.8)**.
- `final (a, b) = await (fa, fb).wait;` for parallel futures. Don't write `async` + `return await` just to pass a Future through.
- `async`/`await` over `.then()` chains.

## 3. Widgets

- **Widget classes, not `Widget _buildX()` methods.** Classes get their own element, can be `const`, and rebuild independently.
- `const` constructors and `const` instances everywhere possible (`prefer_const_constructors` lint).
- One public widget per file. The file name matches the class (`booking_screen.dart` → `BookingScreen`).
- Screens: `XxxScreen`/`XxxPage` (route + DI) and `XxxView` (pure UI).
- Use single-purpose widgets over `Container` when only one property is used: `Padding`, `ColoredBox`, `DecoratedBox`, `SizedBox`, `Align`/`Center`. Use `Container` when combining several.
- Use `EdgeInsets.symmetric` / `.only` over `.fromLTRB` for readability.
- Prefix sliver-returning widgets with `Sliver` (`SliverHeader`).
- Keep `build()` pure and cheap. There are no side effects, no object creation that must persist, and no heavy computation.
- Theme values come from `Theme.of(context)` / `ThemeExtension`s. There are no hard-coded colors or text styles in features.
- Hooks (`flutter_hooks`) remove controller init/dispose boilerplate. Keep each hook small.

## 4. Naming & structure (Effective Dart)

- `UpperCamelCase` types and extensions, `lowerCamelCase` members and constants (`const defaultTimeout`, not `DEFAULT_TIMEOUT`), `snake_case` files and packages.
- Name booleans as predicates (`isEmpty`, `hasError`, `canSubmit`). Name methods as verbs, getters as nouns.
- Name magic numbers (`static const _maxRetries = 3;`).
- Explain every `// ignore:` with a comment above it.
- Doc comments (`///`) on public APIs. Say *why*, not *what*.
- Barrel files (`models.dart` exporting a folder) only at package/feature boundaries. Don't barrel-export everything.

## 5. Errors & logging

- Define specific exception types (`class PaymentDeclinedException implements Exception`). Document which calls throw. Never `catch (e)` and swallow the error.
- Across layer boundaries, prefer returning a sealed `Result<T>` over throwing.
- Pass the error and stack trace to the logger as arguments: `log.warning('Upload failed', error, stackTrace)`.

## 6. Lints & tooling (set up once, then trust them)

```yaml
# analysis_options.yaml
include: package:very_good_analysis/analysis_options.yaml   # v11 (strict) — or package:flutter_lints/flutter.yaml (v6, baseline)
analyzer:
  language: { strict-casts: true, strict-inference: true, strict-raw-types: true }
```
- `dart fix --apply` after SDK upgrades. It migrates deprecated APIs automatically.
- `dart format` is language-versioned: raising the SDK constraint can reformat code, so do it in its own commit.
- `dart run build_runner watch -d` while developing with codegen.
- Pin the Flutter version (`environment: flutter: 3.47.x`, or FVM) so the whole team and CI match.

## 7. Deprecated APIs

Run `dart fix --apply`, then `flutter analyze`. For anything left, look up the old API in `generated/flutter-breaking-changes.md` (53 migrations since Flutter 3.27, with before/after code; regenerated by `update.py`). Don't write APIs that are listed there as removed.

## 8. Before you add code, check

1. Does the SDK or `package:collection` already do it (`Isolate.run`, `ListenableBuilder`, `ValueListenableBuilder`, `firstWhereOrNull`, `groupListsBy`)?
2. Does an existing dependency already do it?
3. Can a language feature replace it (primary constructor, pattern, extension type, collection `if`)?
4. Only then write it, and write the smallest version.

## Sources

dart.dev (language/primary-constructors, constructors, patterns, class-modifiers, extension-types, dot-shorthands, collections, records, resources/language/evolution, effective-dart/style + design), docs.flutter.dev/perf/best-practices, engineering.verygood.ventures (code_style, ui/widgets, barrel_files, error_handling), leancode.co/blog/flutter-coding-best-practices. Local copies in `sources/dart`, `sources/vgv`, `leancode/`.
