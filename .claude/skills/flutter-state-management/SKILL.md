---
name: flutter-state-management
description: Choose and correctly use Flutter state management with current (2026) APIs - Riverpod 3 (Notifier/AsyncNotifier, mutations, Ref.mounted), BLoC/Cubit 9 (flutter_bloc), Flutter's official MVVM with ChangeNotifier + Commands, and built-ins (setState, ValueNotifier, ListenableBuilder); plus why to avoid GetX. Use this whenever the user writes or reviews a Cubit, Bloc, provider, Notifier, ViewModel or StatefulWidget, asks "BLoC or Riverpod?", handles loading/error states or one-off effects (snackbar, navigation), uses BuildContext after await, or hits rebuild/async bugs in Flutter, even if they don't say "state management".
---

# Flutter state management

Verified against official docs and pub.dev on 2026-09-25: Flutter 3.47 / Dart 3.13, `flutter_riverpod 3.4`, `flutter_bloc 9.1` / `bloc 9.2`, `provider 6.1`.

The rules that matter more than the library: **ephemeral (UI) state stays in the widget, shared business state lives outside it; every async operation has explicit loading/data/error; one-off effects are not state.**

## 1. Pick one (per codebase) and record why

| | Pick when | Cost |
|---|---|---|
| **Riverpod 3** (most downloaded: ~3.3M/30d) | You want DI + state + caching in one tool; async-heavy data; compile-safe dependencies; less boilerplate | Flexible, so the team must enforce boundaries or the provider graph sprawls |
| **Bloc / Cubit 9** (~2M/30d) | Large teams, strict and traceable state transitions, event transformations (debounce, droppable), regulated or long-lived apps | More boilerplate |
| **ChangeNotifier MVVM + provider** (Flutter's official architecture guide) | You want to follow docs.flutter.dev exactly, fewest dependencies, a team new to Flutter | You hand-write Commands/Result; less tooling |
| `setState`, `ValueNotifier` + `ValueListenableBuilder`, `ListenableBuilder`, `flutter_hooks` | Ephemeral state: selected tab, form input, animation, text controllers, expanded/collapsed | Doesn't scale to shared state |

- Don't mix two of the big three in one app unless you're mid-migration.
- **Avoid GetX** for new code. It bundles state, DI, navigation and utilities behind global singletons and context-free magic. That hides dependencies, makes tests and lifecycles hard, and it breaks separation of concerns. It has many likes but little adoption in serious production code. For an existing GetX app, migrate feature by feature.
- MobX and signals are valid but niche (signals: ~24k downloads/30d). Don't pick them for a team project unless the team already knows them.
- Both Riverpod and Bloc docs say: **do not put ephemeral state in providers/blocs.** It breaks back-navigation (the route's state leaks) and adds noise.

## 2. Load only the reference you need

- Riverpod: `references/riverpod.md` (v3 APIs, codegen decision, mutations, testing, 2→3 migration)
- Bloc/Cubit: `references/bloc.md` (naming conventions, state modeling, presentation events, transformers, bloc_test)
- ChangeNotifier MVVM: `references/mvvm.md` (official ViewModel + Command + Result pattern)

## 3. Universal async rules (all libraries)

- `async` ≠ background thread. CPU work (big JSON, loops, image processing) goes to `Isolate.run` / `compute`. `compute` runs on the main thread on web.
- After any `await`, check before touching context or state: `if (!context.mounted) return;` in widgets, `if (!ref.mounted) return;` in Riverpod 3 notifiers, `if (isClosed) return;` in Cubits.
- Create Futures/Streams **once** (initState, notifier `build`, bloc). Never create them in `build()`, or they re-fire on every rebuild.
- Run independent requests in parallel: `final (user, posts) = await (getUser(), getPosts()).wait;`
- Cancel subscriptions and dispose controllers. Every `listen` has a matching cancel.
- Errors become state (failure/`AsyncError`), never uncaught exceptions out of an `onPressed`.
- One-off effects (snackbar, dialog, navigation): Riverpod `ref.listen` or a Mutation; Bloc `BlocListener`/`bloc_presentation`; MVVM a Command's result listener. Never a boolean in state that has to be reset.
- Dependencies are injected (constructor or provider), never `ApiClient()` created inside a Cubit/Notifier/ViewModel, so they can be faked in tests.

## 4. Review checklist

1. Ephemeral state in the widget, shared state outside it?
2. Loading, error and empty states all rendered (exhaustive `switch` on a sealed state / `AsyncValue`)?
3. One-off effects handled as events/listeners, not state flags?
4. Anything created in `build()` that should persist (Future, ViewModel, controller, provider)?
5. `context`/`ref`/cubit used after `await` without a mounted check?
6. Subscriptions and controllers disposed?
7. Can the logic be unit-tested with fakes (dependencies injected)?
8. Is the rebuild scope minimal (`select`, `BlocSelector`, `ListenableBuilder` around the smallest subtree)?

## Sources

Primary: riverpod.dev (whats_new, do_dont, 3.0_migration, about_code_generation), bloclibrary.dev (naming-conventions, modeling-state, migration), docs.flutter.dev/app-architecture (guide, recommendations, case-study), engineering.verygood.ventures (bloc_state_handling, bloc_event_transformers), pub.dev stats. Secondary: leancode.co/glossary (state-management, bloc, riverpod, futurebuilder, asynchronous-programming).
If this project has `sources/` or `leancode/` folders, read the local copies. Refresh with `python3 fetch_sources.py`.
