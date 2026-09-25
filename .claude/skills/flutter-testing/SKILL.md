---
name: flutter-testing
description: Flutter testing strategy (Flutter team, Very Good Ventures, LeanCode/Patrol; verified 2026) - fakes vs mocks, unit tests with mocktail, widget tests, golden tests with Alchemist, E2E/UI tests with Patrol including native permission dialogs and notifications, device farms and sharding, Widget Previews, Widgetbook, debugging tools. Use this whenever the user writes, fixes, or plans Flutter tests, sees flaky goldens or CI test failures, needs to test permissions/notifications/native UI, picks between integration_test, Appium and Patrol, or asks how to make Flutter code testable.
---

# Flutter testing

Verified 2026-09-25: Flutter 3.47, patrol 4.10, alchemist 0.14, mocktail 1.0, bloc_test 10, flutter_riverpod 3.4. For Riverpod/Bloc-specific test APIs, see `flutter-state-management/references/`.

Use the testing pyramid on purpose. **Most coverage in fast unit tests of logic, widget tests for components, a few goldens for visuals, and E2E UI tests only for critical user journeys.** Each level checks something the others can't. Don't duplicate edge cases upward.

| Level | Checks | Tool |
|---|---|---|
| Unit | Business logic, Cubits/Notifiers/ViewModels, repositories, mappers, validators | `flutter_test` + `mocktail` |
| Widget | A component/screen's behavior in isolation | `flutter_test` (`patrol_finders` for nicer finders) |
| Golden | How it **looks**: design-system components | Alchemist |
| UI / E2E | The app's main purpose works end-to-end, including native UI | **Patrol** |

## Rules that apply to every level

- **Fakes over mocks** (Flutter team, "strongly recommend"). Write `FakeUserRepository implements UserRepository` with in-memory behavior in `testing/fakes/`. Mocks (mocktail) are for checking interactions or one-off stubs. Keep them **private per test file** (`class _MockApi extends Mock implements Api {}`), so a stub in one file can't leak into another.
- Name tests so the group and test names read as a sentence: `group(ShoppingCart, () { group('addItem', () { test('increases item count', ...) }) })`.
- No shared mutable state: create everything in `setUp` or inside the test.
- Run with random ordering in CI to expose hidden order dependencies: `flutter test --test-randomize-ordering-seed random`.
- Tag slow suites (`@Tags(['golden'])`) so you can run them separately.

## Unit tests

- Only possible if logic lives in pure Dart classes with **injected dependencies**. If a class needs `BuildContext`, it's not unit-testable, and that's a design smell.
- Mock with `mocktail` (simpler) or `mockito`. Never hit real APIs/DBs; use fakes/mocks to drive errors, empty data, and timeouts.
- Arrange → Act → Assert. Mark async tests `async` and **`await`** everything. A forgotten `await` is the #1 beginner bug and makes tests pass falsely.
- Fresh instances in `setUp()`, no shared state between tests.
- Test the async and error paths, not just the happy path.
- Readable matchers: `isEmpty`, `isA<T>()`, `startsWith(...)`, `await expectLater(f(), completion(42))`, `throwsA(isA<MyException>())`, not `expect(x is T, true)`.

## Widget tests

- Use Flutter's built-in widgets (`Text`) as test inputs, not your design-system widgets (`AppText`), unless those are under test. Custom widgets pull in themes/providers/l10n and can hide or cause failures unrelated to what you're testing.
- Unit tests can't cover layout, gestures, or navigation. Those belong in widget or integration tests.

## Golden tests

- Golden tests are for appearance, not behavior. Use them for small, isolated design-system components, **not whole screens**.
- They are platform-sensitive (fonts, anti-aliasing), so macOS-generated images fail on Linux CI. Two fixes:
  1. **Alchemist's CI goldens** (VGV's setup): text is rendered as blocks, so images match across OSes. Platform goldens (real text) run only locally:
     ```dart
     // test/flutter_test_config.dart
     Future<void> testExecutable(FutureOr<void> Function() testMain) async {
       const isRunningInCi = bool.fromEnvironment('CI');
       return AlchemistConfig.runWithConfig(
         config: AlchemistConfig(platformGoldensConfig: PlatformGoldensConfig(enabled: !isRunningInCi)),
         run: testMain,
       );
     }
     ```
     Run CI with `flutter test --dart-define=CI=true`.
     ⚠ As of 2026-09-25, alchemist 0.14 requires `equatable ^2`, so it can't be resolved alongside `equatable 3.0`. Keep equatable on 2.x until alchemist updates (check pub.dev).
  2. Or generate and verify all goldens in the same Linux container (a Docker image pinned to CI's Flutter version).
- Either way, lock the theme, fonts and surface size.
- Use **Alchemist** instead of raw `matchesGoldenFile`: consistent font loading, deterministic rendering, and many variants (themes/sizes/states) in one test.
- Make them deterministic: no `DateTime.now()`/random values, mock network images, and settle or disable animations.
- Update with `flutter test --update-goldens`, and **review the image diff** before committing. Hot reload does not update goldens.

## UI / E2E tests with Patrol

`integration_test` alone can't touch native UI (permission dialogs, notifications, system settings, other apps), and Appium can't see Flutter widgets well. Patrol bridges both. Its test runs on top of native runners (UIAutomator / XCUITest), so one Dart test can drive Flutter widgets and the OS. It supports Android, iOS, and Web (4.0+) and is listed in the official Flutter docs.

```dart
patrolTest('user can upvote a comment', ($) async {
  await $.pumpWidgetAndSettle(const App());
  await $.platform.mobile.grantPermissionWhenInUse(); // native dialog
  await $(TextField).enterText('Patrol');
  await $(ListTile).containing('Part 1').$(Icons.arrow_forward).scrollTo().tap();
  await $(ElevatedButton).at(2).tap();                // waits for visibility automatically
});
```

- Native actions use **`$.platform`** (Patrol 4.0+): `$.platform.tap` (all platforms), `$.platform.mobile.*` (Android+iOS), `$.platform.android|ios|web.*` (one platform). `$.native`/`$.native2` are deprecated. Migrate when you touch old tests.
- Cover **only crucial user paths**. Edge cases belong in lower-level tests.
- UI tests check function, not visuals (that's goldens).
- Scale with device farms (Firebase Test Lab, BrowserStack, LambdaTest, AWS Device Farm, emulator.wtf, Marathon), test bundling, and **sharding** across devices. Patrol emits JUnit reports for test-management tools.
- Tooling: Patrol VS Code extension (run/debug a single test in one click), Patrol MCP (lets an AI agent run tests, take screenshots, read the native tree).
- Process matters more than tools in big teams: make UI tests part of each user story's **acceptance criteria** in the Scrum team, not a separate QA waterfall, or they rot and take up dev time.

## Component catalogs & previews

- **Flutter Widget Previews** (stable in 3.47) render widgets in the IDE with `@Preview`-annotated functions. Use them for fast visual iteration without running the app.
- Widgetbook (3.25) is a shareable catalog with knobs, themes and devices, for design-system review with designers. LeanCode's VS Code "Widgetbook Entries Generator" scaffolds entries.

## Debugging

- Measure performance only in **profile mode**. Debug mode distorts timings.
- Use `debugPrint` or `dart:developer` `log()`, not `print` (which truncates long output on Android).
- DevTools: Widget Inspector (layout/constraints), Performance (jank), Memory (leaks), Network (works with `http`/`dio`, not every custom client).

## Sources

If this project has a `leancode/` folder, read `leancode/<path>.md`; otherwise fetch `https://leancode.co/<path>`.

- `glossary/unit-testing-in-flutter`, `glossary/golden-tests-in-flutter`, `glossary/debugging-in-flutter`
- `blog/the-role-of-ui-testing-in-large-apps`: why UI tests, what to cover, Patrol API examples
- `blog/everything-you-need-to-know-about-patrol`: architecture, device farms, sharding, MCP
- `blog/try-patrol-quick-hands-on-tutorial`: step-by-step setup
- `blog/patrol-4-0-release`, `blog/patrol-web-support`, `blog/patrol-mcp-release`, `blog/patrol-vs-code-extension`
- `blog/email-testing-in-automated-tests`, `blog/testing-sms-in-automated-tests`: testing OTP/email flows E2E
- `blog/moving-flutter-widgets-to-widgetbook`
- Docs: https://patrol.leancode.co
