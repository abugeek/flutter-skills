# Riverpod 3 (flutter_riverpod 3.4, riverpod_generator 4.x) — verified 2026-09-25

## Codegen: optional
Riverpod's docs: use `@riverpod` codegen **only if you already use codegen** (freezed, json_serializable). Dart macros were cancelled and build_runner is slow. Without codegen, use `NotifierProvider` / `AsyncNotifierProvider` directly. Both are first-class. Pick one style per codebase.

## Core API (v3)
```dart
// no codegen
final todosProvider = AsyncNotifierProvider<TodosNotifier, List<Todo>>(TodosNotifier.new);

class TodosNotifier extends AsyncNotifier<List<Todo>> {
  @override
  Future<List<Todo>> build() => ref.watch(todoRepositoryProvider).fetchAll(); // self-initializing

  Future<void> add(String title) async {
    final todo = await ref.read(todoRepositoryProvider).add(title);
    if (!ref.mounted) return;                        // v3: provider may be disposed during await
    state = AsyncData([...state.value ?? [], todo]); // v3: `value` is the old `valueOrNull`
  }
}

// codegen equivalent
@riverpod
class Todos extends _$Todos {
  @override
  Future<List<Todo>> build() => ref.watch(todoRepositoryProvider).fetchAll();
}
@riverpod
TodoRepository todoRepository(Ref ref) => HttpTodoRepository(ref.watch(dioProvider)); // v3: plain `Ref`
```
- Use `Notifier` / `AsyncNotifier` / `StreamNotifier` for state with actions, and `Provider` / `FutureProvider` for derived or read-only values. Put actions (methods) on the Notifier.
- `StateProvider`, `StateNotifierProvider` and `ChangeNotifierProvider` are **legacy** (moved to `import 'package:flutter_riverpod/legacy.dart';`). Don't use them in new code.
- v3 unified the classes: there's no more `AutoDisposeNotifier`, `FamilyNotifier`, or `XxxRef` types. Family args become constructor fields: `class C extends Notifier<int> { C(this.arg); final Arg arg; }`.
- `AsyncValue` is sealed. Render it with an exhaustive `switch (value) { AsyncData(:final value) => ..., AsyncError(:final error) => ..., AsyncLoading() => ... }`.
- **Automatic retry**: a failing provider retries with exponential backoff (200ms → 6.4s). Customize or disable it with `ProviderScope(retry: (count, error) => count > 3 ? null : Duration(seconds: count))`.
- Errors read through `ref.watch/read` come wrapped in `ProviderException` (the original is in `.exception`). `AsyncValue.error` is unwrapped.
- All providers use `==` to decide notifications. Large models should have cheap `==`, or override `updateShouldNotify`.
- Listeners of invisible widgets are paused automatically (via `TickerMode`).

## UI
- `ref.watch` in `build` for rendering, `ref.listen` for side effects (snackbar, navigation), `ref.read` only inside callbacks.
- Narrow rebuilds with `ref.watch(p.select((s) => s.count))`.
- **Mutations** (`import 'package:flutter_riverpod/experimental/mutation.dart';`, experimental, but the documented way to show loading/error for writes like form submit or add-to-cart):
```dart
final addTodoMutation = Mutation<void>();
// in build:
final add = ref.watch(addTodoMutation);
switch (add) {
  MutationPending() => const CircularProgressIndicator(),
  MutationError() => RetryButton(...),
  _ => ElevatedButton(onPressed: () => addTodoMutation.run(ref, (tsx) async {
         await tsx.get(todosProvider.notifier).add('New'); }), child: const Text('Add')),
}
```
Reads via `tsx.get(...)` keep providers alive until the mutation finishes, which fixes the old "provider disposed mid-request" bug with `ref.read` in `onPressed`. Keyed mutations (`addTodo(id)`) track per-item state. `mutation.reset(ref)` returns to idle.
- Offline persistence (experimental): call `persist(...)` in `build`, with `riverpod_sqflite`. `AsyncValue.isFromCache` tells you the value came from the DB.

## DO / DON'T (riverpod.dev)
- DON'T initialize providers from widgets (`initState` → `ref.read(p).init()`). Providers initialize themselves in `build`.
- DON'T use providers for ephemeral state (selected item, form state, animations, controllers). Use widget state or `flutter_hooks`.
- DON'T perform side effects (POST/submit) in provider initialization. Providers are for reads; writes go through Notifier methods or Mutations.
- Providers are **top-level finals only**. Never create them dynamically or as instance fields. Watch statically known providers, so lints work.
- Install `riverpod_lint`. It's an analysis_server_plugin now, so there's no `custom_lint` step: in `analysis_options.yaml` add
  ```yaml
  plugins:
    riverpod_lint: ^3.1.9
  ```

## Testing
```dart
test('adds todo', () async {
  final container = ProviderContainer.test(overrides: [      // auto-disposed
    todoRepositoryProvider.overrideWithValue(FakeTodoRepository()),
  ]);
  await container.read(todosProvider.future);
  await container.read(todosProvider.notifier).add('x');
  expect(container.read(todosProvider).value, hasLength(1));
});
```
Also available: `notifierProvider.overrideWithBuild((ref, self) => initial)` (mock only `build`), `futureProvider.overrideWithValue(AsyncData(42))`, and `tester.container()` in widget tests.

## Migrating 2 → 3 (checklist)
`valueOrNull` → `value`; `AutoDisposeX`/`FamilyX` → `X`; `XxxRef ref` → `Ref ref`; `createContainer` → `ProviderContainer.test`; catch `ProviderException` where you caught raw errors; move legacy providers to the `legacy.dart` import (then replace them); review `==`-based notification changes for streams. Full guide: riverpod.dev/docs/3.0_migration.
