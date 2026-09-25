---
name: flutter-architecture
description: Current (2026) Flutter app architecture from the Flutter team's official guide, Very Good Ventures and LeanCode - UI layer (View + ViewModel/Cubit/Notifier) and data layer (Repository + Service), feature folders, dependency injection, Result/Command patterns, networking and JSON models, go_router, monorepos with pub workspaces, day-one project setup, scaling teams, legacy refactoring. Use this whenever creating a new Flutter project or feature, deciding folder structure, adding a repository/API/service layer, choosing packages, reviewing Flutter code for maintainability, or scaling a Flutter team - even if the user only asks "where should this file go".
---

# Flutter architecture

Verified 2026-09-25 against docs.flutter.dev/app-architecture (Flutter 3.47), engineering.verygood.ventures, and pub.dev. For Dart syntax and widget code style, see the `flutter-dart-style` skill. For state libraries, see `flutter-state-management`.

**Core rule (Flutter team, "strongly recommend"): separate the UI layer from the data layer, keep widgets dumb, and let data flow one way.** Everything else is scaled to the project's size.

## 1. The layers

```
View (widget) ──calls commands/methods──▶ ViewModel | Cubit | Notifier ──▶ Repository ──▶ Service
      ◀──────────── listens to immutable state ◀───────────── returns models / Result ◀─ raw data
```
- **Service**: wraps exactly one external source (REST client, DB, platform plugin, SharedPreferences). No business logic. Returns raw/API models.
- **Repository**: the **source of truth** for one kind of data (`UserRepository`, `BookingRepository`). It combines services, caches, retries, maps API models to domain models, and exposes `Future<Result<T>>` or `Stream<T>`. No Flutter imports. **Define it as an abstract class** (officially "strongly recommend"), so tests use fakes and dev/staging use other implementations.
- **ViewModel / Cubit / Notifier**: one per screen or feature. Turns repository data into UI state and exposes actions (Commands/methods). No `BuildContext`, no widgets.
- **View**: layout, simple `if`s, animation, routing. No business logic.
- **Domain layer / use-cases: conditional.** Add them only when logic is complex or repeated across ViewModels. In most apps they're overhead.
- Separate API models from domain models only in large apps. Otherwise one immutable model is fine.

## 2. Scale the structure to the project

| Project | Structure |
|---|---|
| MVP / 1-3 devs | One package, feature folders (below). Abstract repositories + fakes. Skip use-cases and extra model layers. |
| Growing product | Same, plus `packages/` for reusable data/repository code (VGV layered: `packages/api_client`, `packages/user_repository`), with Dart **pub workspaces**. |
| Enterprise / many squads | Packages per business domain owned by squads, a platform team, a design-system squad, Melos for tasks (see §6). |

Official layout (Flutter's Compass sample): **data by type, UI by feature**. Repositories and services are shared across features; each feature has one view and one view model. Name classes by role and keep shared widgets in `ui/core/`, not `widgets/`.
```
lib/
├── ui/
│   ├── core/ ui/ (shared widgets) · themes/
│   └── <feature>/ view_models/<feature>_viewmodel.dart · widgets/<feature>_screen.dart
├── domain/models/            # immutable app models, used by data + ui
├── data/
│   ├── repositories/         # abstract BookingRepository + _remote / _local implementations
│   ├── services/             # api_client.dart, shared_preferences_service.dart
│   └── model/                # API models
├── config/ (DI wiring)  routing/  utils/ (result.dart, command.dart)
├── main.dart · main_development.dart · main_staging.dart   # entry points = different DI wiring
test/ (mirrors lib: data/ domain/ ui/ utils/)   testing/ (fakes/ models/ shared by tests)
```
VGV's equivalent: `lib/<feature>/{bloc,view}` + `packages/<x>_repository`, with a **Page/View split**: `LoginPage` provides the Bloc/ViewModel, and `LoginView` is pure UI you can test with a mock. Both are fine. Pick one and apply it everywhere.

## 3. Data, networking, persistence

- **Immutable models** ("strongly recommend"). Use freezed 4 (`@freezed abstract class User with _$User`, or `sealed class` for unions), dart_mappable, or plain `final` classes + `equatable`. With Dart 3.13 **primary constructors**, plain classes are short enough that many teams skip codegen. Codegen adds build time, so use it where it pays off (JSON, deep equality, unions).
- Parse JSON into models at the service boundary. Never pass `Map<String, dynamic>` to the UI. Treat API fields as nullable. `(json['price'] as num).toDouble()`.
- Return `Result<T>` (sealed Ok/Error) from repositories instead of throwing across layers. Callers `switch`, so errors can't be ignored.
- HTTP: `dio 5` when you need interceptors (auth/refresh, logging, retry), cancellation, or progress. Otherwise `http`. The client lives in a service. Never call it from widgets.
- Local data: `drift` (SQL, reactive) or `sqflite`. `hive_ce` for key-value/NoSQL. **Isar is unmaintained (last release 2023). Don't start new code on it.** `shared_preferences` is for settings only. `flutter_secure_storage` is for tokens.
- Offline-first: the local DB is the source of truth, the UI never reads the API directly, writes are queued and synced in the background with retry, and conflicts are resolved with last-write-wins or a merge. Riverpod 3 has experimental `persist()` for provider-level caching.

## 4. App-level decisions

- **DI**: `provider`/`RepositoryProvider` (official recommendation), Riverpod providers, or `get_it` for plain singletons. Avoid global mutable singletons reachable from anywhere.
- **Navigation**: `go_router` (official: fits ~90% of apps; typed routes via `go_router_builder`). `auto_route` if you want codegen'd typed routes everywhere. Keep redirects (auth gate) in one place.
- **Flavors / environments**: separate `main_*.dart` files that wire different repository implementations. There are no `if (isDev)` checks in feature code.
- **Errors**: a global handler (`FlutterError.onError` + `PlatformDispatcher.instance.onError`) → crash reporting. Define descriptive exception types, and document which calls throw.

## 5. Day-one setup checklist (do these before feature work)

1. Lints: `very_good_analysis` (strict) or `flutter_lints` (baseline), plus `riverpod_lint` / `bloc_lint` if applicable. Treat warnings as errors in CI.
2. `analysis_options.yaml` + `dart format` enforced in CI (the formatter is language-versioned; pin the SDK in `pubspec.yaml`, e.g. `environment: sdk: ^3.13.0, flutter: 3.47.x`).
3. CI on every PR: `flutter analyze`, `dart format --set-exit-if-changed`, `flutter test --coverage --test-randomize-ordering-seed random`.
4. Flavors (dev/staging/prod) and the DI wiring for each.
5. Architecture Decision Records (`docs/adr/`) for state library, folder layout, navigation, codegen yes/no.
6. Testing plan: unit tests for repositories and ViewModels (with fakes), widget tests for screens, a few goldens for design-system components, Patrol E2E for 1-3 critical journeys.
7. Error reporting, logging (`package:logging` or a logger passed errors as arguments, not interpolated), and an app-wide error UI.
8. Design tokens (colors, typography, spacing) in a theme extension from the start. There are no hard-coded colors in features.

## 6. Scaling teams and legacy (LeanCode + VGV experience)

- **Don't scale the team before conventions exist.** Give the core team a pre-implementation phase (~2 months at LeanCode) to settle networking, navigation, auth, i18n and errors.
- **Don't over-engineer.** Audits find proprietary meta-frameworks and day-one hyper-modularity as often as missing structure.
- Every package/folder has an owning *team*. Unowned "common" code rots, so give it to a platform team.
- Monorepo: **pub workspaces** (one resolution, faster IDE) + Melos for running scripts across packages. With FFCA-style packages (`feature_domain`, `feature_data`, `feature_presentation`), presentation never depends on data, and the app wires them together.
- Cross-feature calls go through small facades (sync queries or async events), and cross-feature navigation goes through route targets in a shared routing package.
- Localization belongs to a TMS (e.g. Phrase with `.arb` support), not the repo, as the source of truth.
- Legacy: `@Deprecated` **and enforce it** (two ways of doing one thing is worse than either). Refactor in levels: code quality → structural (codemods, design-system audit) → architectural (ADRs) → culture (ownership, boy-scout rule).
- Security (audit findings): biometrics must unlock a hardware-keystore key that decrypts the session, not just check "did FaceID pass". Use PKCE for OAuth, never roll your own crypto, and never store tokens in `SharedPreferences`.

## Sources

Primary: docs.flutter.dev/app-architecture (guide, recommendations, case-study), github.com/flutter/samples/compass_app, engineering.verygood.ventures (architecture, ffca, barrel_files, error_handling), pub.dev. Secondary: leancode.co/blog (feature-based-flutter-architecture, building-an-enterprise-application-in-flutter, top-findings-after-enterprise-mobile-app-audits, flutter-refactoring-framework, building-a-design-system-in-flutter-app), leancode.co/glossary (clean-architecture, offline-first, dio, json-parsing).
Local copies: `sources/` (refresh: `python3 fetch_sources.py`) and `leancode/`.
